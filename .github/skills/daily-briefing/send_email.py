"""
Gmail SMTP 邮件发送模块

可独立运行：python send_email.py <html_file>
也可作为模块导入：from send_email import send_email

环境变量（需提前设置或通过 .env 加载）：
  BRIEFING_SENDER      发件 Gmail 地址
  GMAIL_APP_PASSWORD    Gmail 应用专用密码
  BRIEFING_RECIPIENTS   收件地址，逗号分隔（可选，有默认值）
"""

import smtplib
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta
from pathlib import Path

SGT = timezone(timedelta(hours=8))


def send_email(html_content: str) -> None:
    sender = os.environ.get("BRIEFING_SENDER", "")
    password = os.environ.get("GMAIL_APP_PASSWORD", "")
    recipients = os.environ.get(
        "BRIEFING_RECIPIENTS", "patrickstar.pty@gmail.com"
    ).split(",")

    if not sender:
        print("错误: 未设置 BRIEFING_SENDER")
        sys.exit(1)
    if not password:
        print("错误: 未设置 GMAIL_APP_PASSWORD")
        sys.exit(1)

    now = datetime.now(SGT)
    today = now.strftime("%Y年%m月%d日")
    is_sunday = now.weekday() == 6
    subject_type = "周报" if is_sunday else "日报"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📋 AI 内参·{subject_type} | {today}"
    msg["From"] = f"AI 内参 Agent <{sender}>"
    msg["To"] = ", ".join(recipients)

    if "<html" not in html_content.lower():
        html_content = (
            '<html><body style="font-family: -apple-system, \'Segoe UI\', sans-serif;'
            ' max-width: 680px; margin: 0 auto; padding: 20px;'
            f' color: #333; line-height: 1.6;">{html_content}</body></html>'
        )

    msg.attach(MIMEText(html_content, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipients, msg.as_string())
        print(f"[{now}] 邮件已发送至 {recipients}")
    except Exception as e:
        print(f"[{now}] 邮件发送失败: {e}")
        backup = f"/tmp/briefing_{now.strftime('%Y%m%d')}.html"
        Path(backup).write_text(html_content, encoding="utf-8")
        print(f"已保存备份至 {backup}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"用法: python {sys.argv[0]} <html_file>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"错误: 文件不存在 {path}")
        sys.exit(1)

    send_email(path.read_text(encoding="utf-8"))
