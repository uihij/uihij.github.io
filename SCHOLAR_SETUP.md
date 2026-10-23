# Google Scholar 自动更新说明

Scholar 账号已经固定为 `-7pRQHMAAAAJ`，无需再配置账号ID。

1. 将本文件夹中的全部内容上传到 GitHub Pages 仓库根目录，必须保留 `.github` 和 `scripts` 文件夹。
2. 在 GitHub 仓库中打开 **Actions -> Update Google Scholar metrics -> Run workflow**，执行第一次更新。
3. 工作流之后每6小时自动检查一次引用和论文变化。
4. 网页会显示总引用、h-index、i10-index和各论文引用；发现新论文时会自动加入 Publications。
5. 每次变化保存在 `scholar_history.json`。

如果 Actions 日志提示Google返回403，请申请SerpAPI Key，然后进入：

`Settings -> Secrets and variables -> Actions -> Secrets`

添加名称为 `SERPAPI_KEY` 的仓库Secret。脚本会自动改用SerpAPI，无需修改代码。
