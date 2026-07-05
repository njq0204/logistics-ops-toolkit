"""经营 KPI 计算模块"""

import pandas as pd


def calc_revenue_summary(df: pd.DataFrame) -> pd.DataFrame:
    """按区域汇总营收、成本、毛利"""
    summary = (
        df.groupby("region")
        .agg(
            order_count=("order_id", "count"),
            total_revenue=("revenue", "sum"),
            total_cost=("cost", "sum"),
            avg_weight=("weight_kg", "mean"),
        )
        .reset_index()
    )
    summary["gross_profit"] = summary["total_revenue"] - summary["total_cost"]
    summary["margin_rate"] = (
        summary["gross_profit"] / summary["total_revenue"] * 100
    ).round(2)
    return summary.sort_values("total_revenue", ascending=False)


def calc_monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """按月统计营收与单量趋势"""
    df = df.copy()
    df["month"] = df["date"].dt.to_period("M").astype(str)
    trend = (
        df.groupby("month")
        .agg(
            order_count=("order_id", "count"),
            total_revenue=("revenue", "sum"),
            total_cost=("cost", "sum"),
        )
        .reset_index()
    )
    trend["gross_profit"] = trend["total_revenue"] - trend["total_cost"]
    return trend


def calc_product_mix(df: pd.DataFrame) -> pd.DataFrame:
    """产品结构分析：各产品类型占比"""
    mix = (
        df.groupby("product_type")
        .agg(
            order_count=("order_id", "count"),
            total_revenue=("revenue", "sum"),
        )
        .reset_index()
    )
    total = mix["total_revenue"].sum()
    mix["revenue_share"] = (mix["total_revenue"] / total * 100).round(2)
    return mix.sort_values("total_revenue", ascending=False)


def calc_efficiency_metrics(df: pd.DataFrame) -> dict:
    """经营效率核心指标"""
    total_revenue = df["revenue"].sum()
    total_cost = df["cost"].sum()
    order_count = len(df)
    return {
        "总营收(元)": round(total_revenue, 2),
        "总成本(元)": round(total_cost, 2),
        "毛利(元)": round(total_revenue - total_cost, 2),
        "毛利率(%)": round((total_revenue - total_cost) / total_revenue * 100, 2),
        "总单量": order_count,
        "单均营收(元)": round(total_revenue / order_count, 2),
        "单均重量(kg)": round(df["weight_kg"].mean(), 2),
    }
