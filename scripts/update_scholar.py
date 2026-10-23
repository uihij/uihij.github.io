import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SCHOLAR_ID = "-7pRQHMAAAAJ"
PROFILE_URL = f"https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en&pagesize=100"

api_key = os.getenv("SERPAPI_KEY", "").strip()
if api_key:
    payload = requests.get("https://serpapi.com/search.json", params={"engine": "google_scholar_author", "author_id": SCHOLAR_ID, "hl": "en", "num": 100, "api_key": api_key}, timeout=30).json()
    table = payload["cited_by"]["table"]
    stats = [int(table[0]["citations"]["all"]), 0, int(table[1]["h_index"]["all"]), 0, int(table[2]["i10_index"]["all"]), 0]
    papers = [{"title": p["title"], "url": p.get("link", PROFILE_URL), "citations": int(p.get("cited_by", {}).get("value", 0)), "year": int(p.get("year") or 0)} for p in payload.get("articles", [])]
else:
    response = requests.get(PROFILE_URL, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36"}, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    stats = [int(x.get_text(strip=True).replace(",", "")) for x in soup.select("#gsc_rsb_st .gsc_rsb_std")]
    if len(stats) < 6:
        raise RuntimeError("Google Scholar blocked the request. Add SERPAPI_KEY as a GitHub Actions secret.")
    papers = []
    for row in soup.select(".gsc_a_tr"):
        title = row.select_one(".gsc_a_at")
        cited = row.select_one(".gsc_a_ac")
        year = row.select_one(".gsc_a_y")
        papers.append({"title": title.get_text(" ", strip=True), "url": "https://scholar.google.com" + title.get("href", ""), "citations": int(cited.get_text(strip=True) or 0), "year": int(year.get_text(strip=True) or 0)})

now = datetime.now(timezone.utc).isoformat()
data = {"status": "ok", "profile_url": PROFILE_URL, "updated_at": now, "citations": stats[0], "h_index": stats[2], "i10_index": stats[4], "papers": papers}
history_path = ROOT / "scholar_history.json"
history = json.loads(history_path.read_text(encoding="utf-8")) if history_path.exists() else []
old = history[-1]["data"] if history else None
changes = []
if old:
    if data["citations"] != old["citations"]:
        changes.append(f"Total citations: {old['citations']} -> {data['citations']}")
    old_papers = {p["title"]: p for p in old["papers"]}
    for paper in papers:
        previous = old_papers.get(paper["title"])
        if previous is None:
            changes.append("New paper: " + paper["title"])
        elif paper["citations"] != previous["citations"]:
            changes.append(f"{paper['title']}: {previous['citations']} -> {paper['citations']}")
if old is None or changes:
    history.append({"checked_at": now, "changes": changes or ["Initial Scholar snapshot"], "data": data})
    history_path.write_text(json.dumps(history[-200:], ensure_ascii=False, indent=2), encoding="utf-8")

(ROOT / "scholar_metrics.js").write_text("window.SCHOLAR_METRICS=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
print(f"Scholar updated: citations={data['citations']} h={data['h_index']} i10={data['i10_index']} papers={len(papers)} changes={len(changes)}")
