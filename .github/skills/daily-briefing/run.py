#!/usr/bin/env python3
"""
AI 内参 — 完整自动化入口
读取 prompt 模板 → copilot -p 生成 HTML → Gmail 发送

用法:
  python run.py              # 使用项目根 .env
  python run.py /path/.env   # 指定 .env 路径
"""

import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
SGT = timezone(timedelta(hours=8))


def _load_env(env_path: Path | None = None) -> None:
    """加载 .env 文件。优先使用传入路径，否则从 skill 目录向上查找。"""
    from dotenv import load_dotenv

    if env_path and env_path.exists():
        load_dotenv(env_path)
        return

    d = SKILL_DIR
    while d != d.parent:
        if (d / ".env").exists():
            load_dotenv(d / ".env")
            return
        d = d.parent

    print("警告: 未找到 .env 文件，将依赖已有的环境变量")


def load_prompt() -> str:
    """读取 prompt 模板并替换日期变量。"""
    now = datetime.now(SGT)
    today = now.strftime("%Y年%m月%d日")
    weekday = now.strftime("%A")
    is_sunday = now.weekday() == 6

    template_file = SKILL_DIR / "prompts" / ("weekly.md" if is_sunday else "daily.md")
    template = template_file.read_text(encoding="utf-8")
    return template.replace("{{TODAY}}", today).replace("{{WEEKDAY}}", weekday)


def generate_briefing() -> str:
    """调用 copilot -p 生成简报 HTML。"""
    now = datetime.now(SGT)
    is_sunday = now.weekday() == 6
    subject_type = "周报" if is_sunday else "日报"
    print(f"[{now}] 正在通过 GitHub Copilot 生成{subject_type}...")

    prompt = load_prompt()
    command = [
        "copilot",
        "-p",
        prompt,
        "--allow-all-tools",
        "--allow-all-urls",
        "--no-ask-user",
        "--silent",
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=300,
        )
    except FileNotFoundError:
        print("GitHub Copilot CLI 未安装或不在 PATH 中")
        sys.exit(1)

    if result.returncode != 0:
        print(f"GitHub Copilot CLI 调用失败 (exit {result.returncode})")
        if result.stderr:
            print(f"stderr: {result.stderr}")
        if result.stdout:
            print(f"stdout: {result.stdout[:500]}")
        sys.exit(1)

    content = result.stdout.strip()
    print(f"[{datetime.now(SGT)}] 简报生成完成，长度: {len(content)} 字符")
    return content


def main() -> None:
    env_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    _load_env(env_path)

    # 延迟导入，确保 .env 已加载
    from send_email import send_email

    now = datetime.now(SGT)
    today = now.strftime("%Y年%m月%d日")
    weekday = now.strftime("%A")
    is_sunday = now.weekday() == 6

    print(f"{'=' * 50}")
    print(f"AI 内参 Agent")
    print(f"日期: {today} ({weekday})")
    print(f"类型: {'周报' if is_sunday else '日报'}")
    print(f"{'=' * 50}")

    content = generate_briefing()
    send_email(content)
    print(f"[{datetime.now(SGT)}] 完成!")


if __name__ == "__main__":
    main()
