#!/usr/bin/env python3
"""测试预警通知配置"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from data_loader import load_config
from notifier import send_alert_notifications

if __name__ == "__main__":
    config = load_config(ROOT / "config" / "settings.yaml")
    output_dir = ROOT / "output"

    test_alerts = [
        {"level": "danger", "category": "测试", "message": "这是一条测试预警，请忽略"},
        {"level": "warning", "category": "毛利率", "message": "区域 [西南] 毛利率 19.2% 低于警戒线"},
    ]
    test_goals = [
        {"name": "总营收(元)", "actual": 15699, "target": 50000, "progress_pct": 31.4, "status_label": "落后"},
    ]

    print("[*] 发送测试通知...")
    result = send_alert_notifications(
        test_alerts, config, output_dir,
        goals=test_goals,
        run_at="测试",
    )
    print(f"[结果] {result}")
