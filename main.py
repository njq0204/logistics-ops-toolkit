#!/usr/bin/env python3
"""
物流经营数据分析平台 v3.0
德邦经营方向 · 海豚生

用法:
  python main.py                          # 完整分析 + 大屏
  python main.py -i data.xlsx             # 指定数据
  python scripts/start_bigscreen.py       # 启动数据大屏 Web 服务
  python scripts/auto_scheduler.py        # 定时自动分析
  python scripts/watch_inbox.py           # 监听新数据文件
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from data_loader import load_config  # noqa: E402
from pipeline import run_analysis  # noqa: E402


def print_section(title: str) -> None:
    print(f"\n{'=' * 55}")
    print(f"  {title}")
    print("=" * 55)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="物流经营数据分析平台 v3.0")
    parser.add_argument("-i", "--input", help="输入数据文件 (CSV/Excel)")
    parser.add_argument("-c", "--config", default="config/settings.yaml", help="配置文件")
    parser.add_argument("-o", "--output", help="输出目录")
    parser.add_argument("--no-html", action="store_true", help="不生成 HTML 报告")
    parser.add_argument("--no-excel", action="store_true", help="不导出 Excel")
    parser.add_argument("--no-charts", action="store_true", help="不生成图表")
    parser.add_argument("--no-dashboard", action="store_true", help="不生成数据大屏")
    parser.add_argument("--serve", action="store_true", help="分析完成后启动大屏 Web 服务")
    parser.add_argument("--port", type=int, default=8080, help="Web 服务端口")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = ROOT / args.config
    config = load_config(config_path) if config_path.exists() else {}

    version = config.get("project", {}).get("version", "3.0.0")
    project_name = config.get("project", {}).get("name", "物流经营数据分析平台")
    data_path = Path(args.input) if args.input else ROOT / config.get("data", {}).get("default_input", "data/sample/orders.csv")
    output_dir = Path(args.output) if args.output else ROOT / config.get("output", {}).get("dir", "output")

    print(f"[*] {project_name} v{version}")
    print(f"[*] 数据文件: {data_path}")

    if not data_path.exists():
        print(f"[ERROR] 数据文件不存在: {data_path}")
        print("[TIP] 运行 python scripts/generate_sample_data.py 生成示例数据")
        sys.exit(1)

    result = run_analysis(
        data_path, config, output_dir,
        generate_charts=not args.no_charts,
        generate_html=not args.no_html,
        generate_excel=not args.no_excel,
        generate_dashboard=not args.no_dashboard,
    )

    if result.validation_errors:
        for e in result.validation_errors:
            print(f"[WARN] {e}")

    print(f"[OK] 已加载 {result.data_summary['总记录数']} 条运单 ({result.data_summary['时间范围']})")

    print_section("核心 KPI")
    for k, v in result.metrics.items():
        print(f"  {k}: {v}")

    print_section("经营预警")
    if result.alerts:
        for a in result.alerts:
            tag = "!!" if a["level"] == "danger" else "!"
            print(f"  [{tag}] [{a['category']}] {a['message']}")
    else:
        print("  所有指标正常，暂无预警")

    if result.goals:
        print_section(f"经营目标追踪 ({result.goal_period or '当期'})")
        for g in result.goals:
            bar = "#" * int(min(g["progress_pct"], 100) / 5) + "-" * (20 - int(min(g["progress_pct"], 100) / 5))
            print(f"  [{g['status_label']:4s}] {g['name']}: {g['actual']}/{g['target']} ({g['progress_pct']}%) [{bar}]")
        s = result.goal_summary
        print(f"  汇总: 共{s['total']}项 | 达标{s['achieved']} | 正常{s['on_track']} | 风险{s['at_risk']} | 落后{s['behind']} | 均值{s['avg_progress']}%")

    if result.notify_result and not result.notify_result.get("skipped"):
        print_section("预警通知")
        for ch in result.notify_result.get("channels", []):
            status = "OK" if ch.get("ok") else "FAIL"
            print(f"  [{status}] {ch.get('channel', '?')}: {ch.get('path') or ch.get('response') or ch.get('error', '')}")
    elif result.notify_result and result.notify_result.get("skipped"):
        print(f"\n[通知] 跳过: {result.notify_result.get('reason')}")

    if result.diagnosis:
        d = result.diagnosis
        print_section(f"经营诊断 (评分 {d.get('score', '-')}/100)")
        print(f"  {d.get('summary', '')}")
        if d.get("highlights"):
            print("  [亮点]")
            for h in d["highlights"][:3]:
                print(f"    + {h}")
        if d.get("risks"):
            print("  [风险]")
            for r in d["risks"][:3]:
                print(f"    - {r}")
        if d.get("actions"):
            print("  [行动建议 — 优先执行]")
            for a in d["actions"][:5]:
                print(f"    [{a.get('priority','')}] {a.get('action','')}")
                print(f"         -> {a.get('expected_impact','')}")

    if result.chart_paths:
        print_section("可视化图表")
        for cp in result.chart_paths:
            print(f"  [图表] {cp.name}")

    if result.html_path:
        print_section("HTML 报告")
        print(f"  [报告] {result.html_path}")

    if result.excel_path:
        print_section("Excel 导出")
        print(f"  [Excel] {result.excel_path}")

    if result.dashboard_path:
        print_section("数据大屏")
        print(f"  [大屏] {result.dashboard_path}")
        print(f"  [数据] {result.data_json_path}")
        print(f"  [启动] python scripts/start_bigscreen.py --port {args.port}")

    print(f"\n[完成] 全部分析完成！输出目录: {output_dir}")

    if args.serve:
        print(f"\n[*] 正在启动大屏 Web 服务 (port {args.port})...")
        from web_server import main as serve
        serve("127.0.0.1", args.port)


if __name__ == "__main__":
    main()
