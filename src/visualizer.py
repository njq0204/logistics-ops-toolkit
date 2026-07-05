"""数据可视化模块"""

from pathlib import Path
from typing import Union

import matplotlib.pyplot as plt
import pandas as pd

# 中文显示支持
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False


def plot_region_revenue(summary: pd.DataFrame, output_dir: Union[str, Path]) -> Path:
    """区域营收柱状图"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(summary["region"], summary["total_revenue"], color="#0066CC", alpha=0.85)
    ax.set_title("各区域营收对比", fontsize=14, fontweight="bold")
    ax.set_xlabel("区域")
    ax.set_ylabel("营收（元）")
    ax.tick_params(axis="x", rotation=30)
    plt.tight_layout()

    path = output_dir / "region_revenue.png"
    fig.savefig(path, dpi=150)
    plt.close()
    return path


def plot_monthly_trend(trend: pd.DataFrame, output_dir: Union[str, Path]) -> Path:
    """月度营收趋势折线图"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(trend["month"], trend["total_revenue"], "o-", color="#0066CC", label="营收")
    ax1.set_xlabel("月份")
    ax1.set_ylabel("营收（元）", color="#0066CC")
    ax1.tick_params(axis="x", rotation=45)

    ax2 = ax1.twinx()
    ax2.bar(trend["month"], trend["order_count"], alpha=0.3, color="#FF9900", label="单量")
    ax2.set_ylabel("单量", color="#FF9900")

    ax1.set_title("月度营收与单量趋势", fontsize=14, fontweight="bold")
    plt.tight_layout()

    path = output_dir / "monthly_trend.png"
    fig.savefig(path, dpi=150)
    plt.close()
    return path


def plot_product_mix(mix: pd.DataFrame, output_dir: Union[str, Path]) -> Path:
    """产品结构饼图"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(
        mix["total_revenue"],
        labels=mix["product_type"],
        autopct="%1.1f%%",
        startangle=90,
        colors=["#0066CC", "#FF9900", "#00AA66", "#CC3366", "#9966CC"],
    )
    ax.set_title("产品结构（按营收占比）", fontsize=14, fontweight="bold")
    plt.tight_layout()

    path = output_dir / "product_mix.png"
    fig.savefig(path, dpi=150)
    plt.close()
    return path
