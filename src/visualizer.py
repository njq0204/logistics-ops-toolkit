"""数据可视化模块 — 全面版"""

from pathlib import Path
from typing import List, Union

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

COLORS = ["#0066CC", "#FF9900", "#00AA66", "#CC3366", "#9966CC", "#FF6633", "#33CCCC"]


def _save(fig, output_dir: Path, name: str, dpi: int = 150) -> Path:
    path = output_dir / f"{name}.png"
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close()
    return path


def plot_region_revenue(summary: pd.DataFrame, output_dir: Union[str, Path], dpi: int = 150) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(summary["region"], summary["total_revenue"], color=COLORS[0], alpha=0.85)
    ax.bar_label(bars, fmt="%.0f", fontsize=8, padding=3)
    ax.set_title("各区域营收对比", fontsize=14, fontweight="bold")
    ax.set_xlabel("区域")
    ax.set_ylabel("营收（元）")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x/10000:.0f}万" if x >= 10000 else f"{x:.0f}"))
    ax.tick_params(axis="x", rotation=30)
    return _save(fig, output_dir, "region_revenue", dpi)


def plot_region_margin(summary: pd.DataFrame, output_dir: Union[str, Path], dpi: int = 150) -> Path:
    output_dir = Path(output_dir)
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = [COLORS[2] if m >= 25 else COLORS[1] if m >= 20 else COLORS[3] for m in summary["margin_rate"]]
    bars = ax.bar(summary["region"], summary["margin_rate"], color=colors, alpha=0.85)
    ax.bar_label(bars, fmt="%.1f%%", fontsize=9)
    ax.axhline(y=20, color="red", linestyle="--", alpha=0.5, label="警戒线 20%")
    ax.set_title("各区域毛利率对比", fontsize=14, fontweight="bold")
    ax.set_ylabel("毛利率 (%)")
    ax.legend()
    ax.tick_params(axis="x", rotation=30)
    return _save(fig, output_dir, "region_margin", dpi)


def plot_monthly_trend(trend: pd.DataFrame, output_dir: Union[str, Path], dpi: int = 150) -> Path:
    output_dir = Path(output_dir)
    fig, ax1 = plt.subplots(figsize=(11, 5))
    ax1.plot(trend["month"], trend["total_revenue"], "o-", color=COLORS[0], linewidth=2, label="营收")
    ax1.fill_between(range(len(trend)), trend["total_revenue"], alpha=0.1, color=COLORS[0])
    ax1.set_xlabel("月份")
    ax1.set_ylabel("营收（元）", color=COLORS[0])
    ax1.tick_params(axis="x", rotation=45)

    ax2 = ax1.twinx()
    ax2.bar(trend["month"], trend["order_count"], alpha=0.25, color=COLORS[1], label="单量")
    ax2.set_ylabel("单量", color=COLORS[1])
    ax1.set_title("月度营收与单量趋势", fontsize=14, fontweight="bold")
    return _save(fig, output_dir, "monthly_trend", dpi)


def plot_product_mix(mix: pd.DataFrame, output_dir: Union[str, Path], dpi: int = 150) -> Path:
    output_dir = Path(output_dir)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.pie(mix["total_revenue"], labels=mix["product_type"], autopct="%1.1f%%",
            startangle=90, colors=COLORS[:len(mix)])
    ax1.set_title("营收占比", fontweight="bold")
    ax2.barh(mix["product_type"], mix["margin_rate"], color=COLORS[2], alpha=0.85)
    ax2.set_title("各产品毛利率", fontweight="bold")
    ax2.set_xlabel("毛利率 (%)")
    fig.suptitle("产品结构分析", fontsize=14, fontweight="bold")
    return _save(fig, output_dir, "product_mix", dpi)


def plot_customer_segment(seg: pd.DataFrame, output_dir: Union[str, Path], dpi: int = 150) -> Path:
    output_dir = Path(output_dir)
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    axes[0].bar(seg["customer_type"], seg["total_revenue"], color=[COLORS[0], COLORS[1]])
    axes[0].set_title("客户类型营收")
    axes[1].bar(seg["customer_type"], seg["order_count"], color=[COLORS[0], COLORS[1]])
    axes[1].set_title("客户类型单量")
    axes[2].bar(seg["customer_type"], seg["avg_satisfaction"], color=[COLORS[2], COLORS[3]])
    axes[2].set_title("平均满意度")
    axes[2].set_ylim(0, 5.5)
    fig.suptitle("客户分层分析", fontsize=14, fontweight="bold")
    return _save(fig, output_dir, "customer_segment", dpi)


def plot_sales_ranking(ranking: pd.DataFrame, output_dir: Union[str, Path], dpi: int = 150) -> Path:
    output_dir = Path(output_dir)
    top = ranking.head(8)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(top["sales_rep"][::-1], top["total_revenue"][::-1], color=COLORS[0], alpha=0.85)
    ax.set_title("销售员业绩 TOP 8", fontsize=14, fontweight="bold")
    ax.set_xlabel("营收（元）")
    return _save(fig, output_dir, "sales_ranking", dpi)


def plot_region_product_heatmap(matrix: pd.DataFrame, output_dir: Union[str, Path], dpi: int = 150) -> Path:
    output_dir = Path(output_dir)
    pivot = matrix.pivot_table(index="region", columns="product_type", values="total_revenue", fill_value=0)
    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(pivot.values, cmap="Blues", aspect="auto")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=30, ha="right")
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.values[i, j]
            if val > 0:
                ax.text(j, i, f"{val/10000:.0f}万", ha="center", va="center", fontsize=8,
                        color="white" if val > pivot.values.max() * 0.6 else "black")
    plt.colorbar(im, ax=ax, label="营收（元）")
    ax.set_title("区域 × 产品 营收热力图", fontsize=14, fontweight="bold")
    return _save(fig, output_dir, "region_product_heatmap", dpi)


def plot_satisfaction_trend(monthly: pd.DataFrame, output_dir: Union[str, Path], dpi: int = 150) -> Path:
    output_dir = Path(output_dir)
    if "avg_satisfaction" not in monthly.columns:
        return output_dir / "satisfaction_trend.png"
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(monthly["month"], monthly["avg_satisfaction"], "s-", color=COLORS[2], linewidth=2)
    ax.axhline(y=4.0, color="red", linestyle="--", alpha=0.5, label="及格线 4.0")
    ax.set_ylim(1, 5.5)
    ax.set_title("月度客户满意度趋势", fontsize=14, fontweight="bold")
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    return _save(fig, output_dir, "satisfaction_trend", dpi)


def generate_all_charts(
    region_summary: pd.DataFrame,
    monthly: pd.DataFrame,
    product_mix: pd.DataFrame,
    customer_seg: pd.DataFrame,
    sales_ranking: pd.DataFrame,
    region_product: pd.DataFrame,
    output_dir: Union[str, Path],
    dpi: int = 150,
) -> List[Path]:
    """一键生成全部图表"""
    output_dir = Path(output_dir)
    charts = [
        plot_region_revenue(region_summary, output_dir, dpi),
        plot_region_margin(region_summary, output_dir, dpi),
        plot_monthly_trend(monthly, output_dir, dpi),
        plot_product_mix(product_mix, output_dir, dpi),
        plot_customer_segment(customer_seg, output_dir, dpi),
        plot_sales_ranking(sales_ranking, output_dir, dpi),
        plot_region_product_heatmap(region_product, output_dir, dpi),
        plot_satisfaction_trend(monthly, output_dir, dpi),
    ]
    return charts
