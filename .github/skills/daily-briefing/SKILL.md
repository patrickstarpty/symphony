---
name: daily-briefing
description: Generate or send the AI industry daily or weekly briefing for this repository. Use this when asked to create the briefing, send the briefing, or update the daily briefing workflow.
---

# AI领域的每日简报

生成 AI 行业日报/周报，通过 Gmail 发送。

## 触发条件

用户提到：生成简报、发简报、每日简报、daily briefing、AI 内参

## 工作流程

1. **判断类型**：周日 → 周报（`prompts/weekly.md`），其余 → 日报（`prompts/daily.md`）
2. **搜索新闻**：使用 WebSearch / WebFetch，按 prompt 模板中的关注公司、领域、信息源搜索
3. **生成 HTML**：整理为结构化简报，中文，邮件友好的 HTML 格式
4. **发送邮件**：将 HTML 写入临时文件，调用 `send_email.py` 发送

## 发送邮件

```bash
.venv/bin/python .github/skills/daily-briefing/send_email.py /tmp/briefing_draft.html
```

需要环境变量 `BRIEFING_SENDER` 和 `GMAIL_APP_PASSWORD`（从项目根 `.env` 加载）。

## 完整自动化（不经过会话，直接 `copilot -p` 生成 + 发送）

```bash
.venv/bin/python .github/skills/daily-briefing/run.py
```

## 文件结构

```
daily-briefing/                  # SKILL.md — 你在这里
├── SKILL.md                     # 本文件：skill 元数据与执行指引
├── run.py                       # 自动化入口：加载 prompt → copilot -p → 发邮件
├── send_email.py                # Gmail SMTP 发送，可独立调用
└── prompts/
    ├── daily.md                 # 日报 prompt 模板（关注点、信息源、格式）
    └── weekly.md                # 周报 prompt 模板
```

## 自定义

- 修改关注的公司/领域/信息源 → 编辑 `prompts/daily.md` 和 `prompts/weekly.md`
- 修改收件人 → 设置环境变量 `BRIEFING_RECIPIENTS`（逗号分隔）
- 修改时区 → 编辑 `run.py` 和 `send_email.py` 中的 `SGT` 定义
