#!/usr/bin/env python3
"""
物流经营数据分析平台 v2.0
德邦经营方向 · 海豚生

用法:
  python main.py                          # 默认分析
  python main.py -i data.xlsx             # 指定 Excel 数据
  python main.py --no-html                # 跳过 HTML 报告
  python main.py --no-excel               # 跳过 Excel 导出
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from alert_engine import run_all_alerts  # noqa: E402
from data_loader import (  # noqa: E402
    get_data_summary,
    load_config,
    load_data,
    preprocess_orders,
    validate_orders,
)
from export_excel import export_to_excel  # noqa: E402
from kpi_analyzer import (  # noqa: E402
    calc_city_ranking,
    calc_customer_segment,
    calc_efficiency_metrics,
    calc_monthly_trend,
    calc_mom_growth,
    calc_product_mix,
    calc_region_product_matrix,
    calc_revenue_summary,
    calc_sales_rep_ranking,
    calc_top_customers,
    calc_yoy_growth,
)
from report_generator import generate_html_report  # noqa: E402
from visualizer import generate_all_charts  # noqa: E402


def print_section(title: str) -> None:
    print(f"\n{'=' * 55}")
    print(f"  {title}")
    print("=" * 55)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="物流经营数据分析平台")
    parser.add_argument("-i", "--input", help="输入数据文件 (CSV/Excel)")
    parser.add_argument("-c", "--config", default="config/settings.yaml", help="配置文件路径")
    parser.add_argument("-o", "--output", help="输出目录")
    parser.add_argument("--no-html", action="store_true", help="不生成 HTML 报告")
    parser.add_argument("--no-excel", action="store_true", help="不导出 Excel")
    parser.add_argument("--no-charts", action="store_true", help="不生成图表")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = ROOT / args.config
    config = load_config(config_path) if config_path.exists() else {}

    project_name = config.get("project", {}).get("name", "物流经营数据分析平台")
    data_path = Path(args.input) if args.input else ROOT / config.get("data", {}).get("default_input", "data/sample/orders.csv")
    output_dir = Path(args.output) if args.output else ROOT / config.get("output", {}).get("dir", "output")
    charts_dir = output_dir / "charts"
    reports_dir = output_dir / "reports"
    export_dir = output_dir / "export"
    dpi = config.get("visual", {}).get("dpi", 150)

    print(f"[*] {project_name} v2.0")
    print(f"[*] 数据文件: {data_path}")

    if not data_path.exists():
        print(f"[ERROR] 数据文件不存在: {data_path}")
        print("[TIP] 运行 python scripts/generate_sample_data.py 生成示例数据")
        sys.exit(1)

    raw_df = load_data(data_path)
    ok, errors = validate_orders(raw_df)
    if not ok:
        for e in errors:
            print(f"[WARN] {e}")

    df = preprocess_orders(raw_df)
    summary = get_data_summary(df)
    print(f"[OK] 已加载 {summary['总记录数']} 条运单 ({summary['时间范围']})")

    # === 分析 ===
    metrics = calc_efficiency_metrics(df)
    region_summary = calc_revenue_summary(df)
    monthly = calc_monthly_trend(df)
    mom = calc_mom_growth(monthly)
    yoy = calc_yoy_growth(df)
    product_mix = calc_product_mix(df)
    customer_seg = calc_customer_segment(df)
    top_customers = calc_top_customers(df)
    sales_ranking = calc_sales_rep_ranking(df)
    region_product = calc_region_product_matrix(df)
    city_ranking = calc_city_ranking(df)
    alerts = run_all_alerts(df, region_summary, mom, config)

    # === 终端输出 ===
    print_section("核心 KPI")
    for k, v in metrics.items():
        print(f"  {k}: {v}")

    print_section("经营预警")
    if alerts:
        for a in alerts:
            tag = "!!" if a["level"] == "danger" else "!"
            print(f"  [{tag}] [{a['category']}] {a['message']}")
    else:
        print("  所有指标正常，暂无预警")

    print_section("区域营收 TOP")
    print(region_summary.to_string(index=False))

    print_section("月度环比")
    cols = ["month", "total_revenue", "order_count", "revenue_mom(%)", "profit_mom(%)"]
    print(mom[cols].to_string(index=False))

    if not yoy.empty:
        print_section("同比分析")
        print(yoy.to_string(index=False))

    print_section("客户分层")
    print(customer_seg.to_string(index=False))

    print_section("TOP 10 客户")
    print(top_customers.to_string(index=False))

    print_section("销售员排名")
    print(sales_ranking.to_string(index=False))

    print_section("城市 TOP 10")
    print(city_ranking.to_string(index=False))

    # === 图表 ===
    chart_paths = []
    if not args.no_charts:
        print_section("生成可视化图表")
        charts_dir.mkdir(parents=True, exist_ok=True)
        chart_paths = generate_all_charts(
            region_summary, monthly, product_mix,
            customer_seg, sales_ranking, region_product,
            charts_dir, dpi,
        )
        for cp in chart_paths:
            print(f"  [图表] {cp.name}")

    # === HTML 报告 ===
    if not args.no_html:
        print_section("生成 HTML 报告")
        reports_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        html_path = generate_html_report(
            reports_dir / f"report_{ts}.html",
            project_name, metrics, summary,
            region_summary, monthly, product_mix,
            customer_seg, top_customers, sales_ranking,
            mom, alerts, chart_paths,
        )
        print(f"  [报告] {html_path}")

    # === Excel 导出 ===
    if not args.no_excel:
        print_section("导出 Excel")
        export_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        xlsx_path = export_to_excel(
            export_dir / f"analysis_{ts}.xlsx",
            metrics, region_summary, mom, product_mix,
            customer_seg, top_customers, sales_ranking, alerts,
        )
        print(f"  [Excel] {xlsx_path}")

    print(f"\n[完成] 全部分析完成！输出目录: {output_dir}")


if __name__ == "__main__":
    main()
