#!/usr/bin/env python3
"""
数据文件监听 — 新文件放入 inbox 自动触发分析

用法:
  python scripts/watch_inbox.py

将 CSV/Excel 文件放入 data/inbox/ 目录，系统自动分析并更新大屏。
"""

import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from data_loader import load_config
from pipeline import run_analysis

INBOX = ROOT / "data" / "inbox"
PROCESSED = ROOT / "data" / "processed"
SUPPORTED = {".csv", ".xlsx", ".xls"}


def process_file(filepath: Path, config: dict, output_dir: Path) -> None:
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 检测到新文件: {filepath.name}")
    try:
        result = run_analysis(filepath, config, output_dir)
        dest = PROCESSED / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filepath.name}"
        shutil.move(str(filepath), str(dest))
        print(f"[OK] 分析完成 | 运单: {result.data_summary['总记录数']} | 已归档: {dest.name}")
        if result.dashboard_path:
            print(f"[OK] 大屏已更新: {result.dashboard_path}")
    except Exception as e:
        print(f"[ERROR] 处理失败: {e}")


def main():
    config_path = ROOT / "config" / "settings.yaml"
    config = load_config(config_path) if config_path.exists() else {}
    output_dir = ROOT / config.get("output", {}).get("dir", "output")

    INBOX.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)

    seen = set()
    poll_interval = config.get("automation", {}).get("watch_poll_seconds", 5)

    print(f"[*] 文件监听已启动")
    print(f"[*] 监听目录: {INBOX}")
    print(f"[*] 支持格式: {', '.join(SUPPORTED)}")
    print(f"[*] 轮询间隔: {poll_interval}s | 按 Ctrl+C 停止")

    while True:
        for f in INBOX.iterdir():
            if f.suffix.lower() in SUPPORTED and f.name not in seen:
                seen.add(f.name)
                process_file(f, config, output_dir)
        time.sleep(poll_interval)


if __name__ == "__main__":
    main()
