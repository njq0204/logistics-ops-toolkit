#!/usr/bin/env python3
"""
自动化调度器 — 定时执行分析任务

用法:
  python scripts/auto_scheduler.py              # 默认每 30 分钟
  python scripts/auto_scheduler.py --interval 10  # 每 10 分钟
  python scripts/auto_scheduler.py --once       # 只运行一次
"""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from data_loader import load_config
from pipeline import run_analysis


def run_job(config: dict, data_path: Path, output_dir: Path) -> None:
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 自动分析开始...")
    try:
        result = run_analysis(data_path, config, output_dir)
        print(f"[OK] 分析完成 | 运单: {result.data_summary['总记录数']} | 预警: {len(result.alerts)}")
        if result.dashboard_path:
            print(f"[OK] 大屏已更新: {result.dashboard_path}")
    except Exception as e:
        print(f"[ERROR] 分析失败: {e}")


def main():
    parser = argparse.ArgumentParser(description="自动化定时分析")
    parser.add_argument("--interval", type=int, default=30, help="运行间隔(分钟)")
    parser.add_argument("--once", action="store_true", help="只运行一次")
    parser.add_argument("-i", "--input", help="数据文件路径")
    args = parser.parse_args()

    config_path = ROOT / "config" / "settings.yaml"
    config = load_config(config_path) if config_path.exists() else {}
    data_path = Path(args.input) if args.input else ROOT / config.get("data", {}).get("default_input", "data/sample/orders.csv")
    output_dir = ROOT / config.get("output", {}).get("dir", "output")

    print(f"[*] 自动化调度器启动")
    print(f"[*] 数据源: {data_path}")
    print(f"[*] 间隔: {'单次' if args.once else str(args.interval) + ' 分钟'}")

    if args.once:
        run_job(config, data_path, output_dir)
        return

    while True:
        run_job(config, data_path, output_dir)
        print(f"[...] 下次运行: {args.interval} 分钟后")
        time.sleep(args.interval * 60)


if __name__ == "__main__":
    main()
