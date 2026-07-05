#!/usr/bin/env python3
"""物流经营数据分析 - 主程序入口"""

import sys
from pathlib import Path

# 将 src 加入模块搜索路径
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from data_loader import load_csv, preprocess_orders  # noqa: E402
from kpi_analyzer import (  # noqa: E402
    calc_efficiency_metrics,
    calc_monthly_trend,
    calc_product_mix,
    calc_revenue_summary,
)
from visualizer import plot_monthly_trend, plot_product_mix, plot_region_revenue  # noqa: E402


def print_section(title: str) -> None:
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print("=" * 50)


def main() -> None:
    data_path = ROOT / "data" / "sample" / "orders.csv"
    output_dir = ROOT / "output"

    print("[*] 物流经营数据分析工具")
    print(f"[*] 数据文件: {data_path}")

    df = preprocess_orders(load_csv(data_path))
    print(f"[OK] 已加载 {len(df)} 条运单记录")

    # 核心 KPI
    print_section("经营效率核心指标")
    metrics = calc_efficiency_metrics(df)
    for key, value in metrics.items():
        print(f"  {key}: {value}")

    # 区域分析
    print_section("区域营收排名")
    region_summary = calc_revenue_summary(df)
    print(region_summary.to_string(index=False))

    # 月度趋势
    print_section("月度趋势")
    monthly = calc_monthly_trend(df)
    print(monthly.to_string(index=False))

    # 产品结构
    print_section("产品结构")
    product_mix = calc_product_mix(df)
    print(product_mix.to_string(index=False))

    # 生成图表
    print_section("生成可视化图表")
    output_dir.mkdir(exist_ok=True)
    charts = [
        plot_region_revenue(region_summary, output_dir),
        plot_monthly_trend(monthly, output_dir),
        plot_product_mix(product_mix, output_dir),
    ]
    for chart in charts:
        print(f"  [图表] 已保存: {chart}")

    print("\n[完成] 分析完成！图表保存在 output/ 目录")


if __name__ == "__main__":
    main()
