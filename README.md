# 🌐 全球科技与科学日报 (Daily Tech News Aggregator)

这是一个基于 Python、大语言模型 (LLM) 和 GitHub Actions 的自动化新闻聚合系统。它每天定时从全球顶级的科技媒体、学术期刊、知名论坛抓取最新资讯，交由 AI 进行重要性评级、筛选、翻译和总结，最后将排版精美的 Top 20 中文科技简报自动发送到您的邮箱。

## ✨ 核心特性

- **🌍 全球视野**：支持从 RSS 订阅源获取最新内容，涵盖 AI、物理、生物医疗、航空航天等各大前沿领域。
- **🧠 AI 智能处理**：一次性将海量信息提交给大模型（如 Gemini），由 AI 充当“主编”，挑选出最具价值的 20 条新闻，并生成高质量的中文摘要。
- **⚖️ 智能权重过滤**：优先展示新闻媒体和高价值论坛，避免被海量的枯燥学术论文刷榜（权重排序：News > Forum > Video > Blog > Paper）。
- **☁️ 零成本自动化部署**：利用 GitHub Actions 的免费算力，实现每天早上自动运行，无需本地开机，无需租赁服务器。
- **📧 邮件自动推送**：采用优化的 HTML 排版，清爽直观，每日清晨在收件箱中查收最新科技动态。

## 🛠️ 技术架构

- **语言**: Python 3.12
- **依赖库**: 
  - `feedparser` (解析 RSS 源)
  - `beautifulsoup4` (清理多余的 HTML 标签，节省 Token)
  - `google-genai` (调用 Gemini 大模型处理数据)
- **调度系统**: GitHub Actions (Cron 定时任务)
- **通知方式**: `smtplib` (通过 Gmail SMTP 发送邮件)

## 🚀 部署指南 (零成本方案)

只需将本项目 Fork 或提交到您的私人 GitHub 仓库，配置好密钥，即可全自动运行。

### 1. 准备工作

您需要准备好以下三个重要信息：
1. **Gemini API Key**: 前往 [Google AI Studio](https://aistudio.google.com/) 免费申请。免费额度（每天 1500 次调用）对于本系统每天 1 次的调用量来说绰绰有余。
2. **发件邮箱 (Gmail)**: 一个用来发送邮件的 Google 邮箱账号。
3. **Gmail 应用专用密码**:
   - 登录您的 Google 账号，进入“管理您的 Google 帐号”。
   - 开启**两步验证**。
   - 搜索并生成“**应用专用密码 (App Password)**”，获取一段 16 位的密码。

### 2. 配置 GitHub Secrets

进入您的 GitHub 仓库网页，依次点击：
`Settings` -> `Secrets and variables` -> `Actions` -> `New repository secret`

依次添加以下 3 个变量（名称必须完全一致）：
- `LLM_API_KEY`: 填入您的 Gemini API Key。
- `GMAIL_USER`: 填入您的 Gmail 邮箱地址（例如 `your-email@gmail.com`）。
- `GMAIL_APP_PASSWORD`: 填入刚生成的 16 位应用专用密码。

*(注：系统默认收件人配置在 `main.py` 的 `RECIPIENT_EMAIL` 变量中，部署前请确保已修改为您自己的收件邮箱。)*

### 3. 测试与运行

部署完成后，系统默认会在每天的 **北京时间 09:00 (UTC 01:00)** 自动运行。

您可以随时进行手动测试：
1. 点击仓库上方的 **Actions** 标签页。
2. 在左侧选择 **Daily Tech News Aggregator** 工作流。
3. 点击右侧的 **Run workflow** 按钮手动触发。
4. 运行成功后，检查您的邮箱是否收到了测试简报！

## ⚙️ 个性化配置 (feeds.json)

如果你想添加、修改或删除新闻源，只需要修改项目根目录下的 `feeds.json` 文件即可。

格式示例：
```json
{
  "url": "https://export.arxiv.org/rss/cs.AI",
  "category": "AI",
  "source_type": "Paper",
  "name": "ArXiv cs.AI"
}
```
- `url`: 目标网站的有效 RSS 地址。
- `category`: 类别分类（将在邮件标签中显示）。
- `source_type`: 数据源类型，建议从 `News`, `Forum`, `Video`, `Blog`, `Paper` 中选择，AI 会根据该类型分配筛选权重。
- `name`: 数据源名称。

## 📜 许可证

MIT License. 您可以随意修改、分发和自用。
