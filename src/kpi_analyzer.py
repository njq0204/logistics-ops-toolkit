"""经营 KPI 计算模块 — 全面版"""

from typing import Dict, List, Optional

import pandas as pd


def calc_efficiency_metrics(df: pd.DataFrame) -> dict:
    """经营效率核心指标"""
    total_revenue = df["revenue"].sum()
    total_cost = df["cost"].sum()
    order_count = len(df)
    gross_profit = total_revenue - total_cost

    metrics = {
        "总营收(元)": round(total_revenue, 2),
        "总成本(元)": round(total_cost, 2),
        "毛利(元)": round(gross_profit, 2),
        "毛利率(%)": round(gross_profit / total_revenue * 100, 2) if total_revenue else 0,
        "总单量": order_count,
        "单均营收(元)": round(total_revenue / order_count, 2),
        "单均重量(kg)": round(df["weight_kg"].mean(), 2),
        "总货量(kg)": round(df["weight_kg"].sum(), 2),
    }

    if "delivery_days" in df.columns:
        metrics["平均时效(天)"] = round(df["delivery_days"].mean(), 1)
        on_time = (df["delivery_days"] <= 3).sum()
        metrics["准时率(%)"] = round(on_time / order_count * 100, 2)

    if "satisfaction" in df.columns:
        metrics["平均满意度"] = round(df["satisfaction"].mean(), 2)

    if "is_return" in df.columns:
        metrics["退单率(%)"] = round(df["is_return"].sum() / order_count * 100, 2)

    return metrics


def calc_revenue_summary(df: pd.DataFrame) -> pd.DataFrame:
    """按区域汇总"""
    summary = (
        df.groupby("region")
        .agg(
            order_count=("order_id", "count"),
            total_revenue=("revenue", "sum"),
            total_cost=("cost", "sum"),
            avg_weight=("weight_kg", "mean"),
            avg_satisfaction=("satisfaction", "mean"),
            avg_delivery=("delivery_days", "mean"),
        )
        .reset_index()
    )
    summary["gross_profit"] = summary["total_revenue"] - summary["total_cost"]
    summary["margin_rate"] = (summary["gross_profit"] / summary["total_revenue"] * 100).round(2)
    summary["avg_satisfaction"] = summary["avg_satisfaction"].round(2)
    summary["avg_delivery"] = summary["avg_delivery"].round(1)
    return summary.sort_values("total_revenue", ascending=False)


def calc_monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """按月统计趋势"""
    trend = (
        df.groupby("month")
        .agg(
            order_count=("order_id", "count"),
            total_revenue=("revenue", "sum"),
            total_cost=("cost", "sum"),
            avg_satisfaction=("satisfaction", "mean"),
        )
        .reset_index()
        .sort_values("month")
    )
    trend["gross_profit"] = trend["total_revenue"] - trend["total_cost"]
    trend["margin_rate"] = (trend["gross_profit"] / trend["total_revenue"] * 100).round(2)
    trend["avg_satisfaction"] = trend["avg_satisfaction"].round(2)
    return trend


def calc_mom_growth(monthly: pd.DataFrame) -> pd.DataFrame:
    """环比增长率（MoM）"""
    mom = monthly.copy()
    mom["revenue_mom(%)"] = mom["total_revenue"].pct_change().mul(100).round(2)
    mom["order_mom(%)"] = mom["order_count"].pct_change().mul(100).round(2)
    mom["profit_mom(%)"] = mom["gross_profit"].pct_change().mul(100).round(2)
    return mom


def calc_yoy_growth(df: pd.DataFrame) -> pd.DataFrame:
    """同比增长率（YoY）— 按月份对比"""
    df = df.copy()
    df["month_num"] = df["date"].dt.month
    yearly = (
        df.groupby(["year", "month_num"])
        .agg(total_revenue=("revenue", "sum"), order_count=("order_id", "count"))
        .reset_index()
    )

    years = sorted(yearly["year"].unique())
    if len(years) < 2:
        return pd.DataFrame(columns=["month_num", "revenue_yoy(%)", "order_yoy(%)"])

    current = yearly[yearly["year"] == years[-1]].set_index("month_num")
    previous = yearly[yearly["year"] == years[-2]].set_index("month_num")

    result = []
    for m in current.index:
        if m in previous.index:
            rev_yoy = (current.loc[m, "total_revenue"] / previous.loc[m, "total_revenue"] - 1) * 100
            ord_yoy = (current.loc[m, "order_count"] / previous.loc[m, "order_count"] - 1) * 100
            result.append({
                "month_num": m,
                "revenue_yoy(%)": round(rev_yoy, 2),
                "order_yoy(%)": round(ord_yoy, 2),
            })

    return pd.DataFrame(result)


def calc_product_mix(df: pd.DataFrame) -> pd.DataFrame:
    """产品结构分析"""
    mix = (
        df.groupby("product_type")
        .agg(
            order_count=("order_id", "count"),
            total_revenue=("revenue", "sum"),
            total_cost=("cost", "sum"),
            avg_weight=("weight_kg", "mean"),
        )
        .reset_index()
    )
    total = mix["total_revenue"].sum()
    mix["revenue_share"] = (mix["total_revenue"] / total * 100).round(2)
    mix["gross_profit"] = mix["total_revenue"] - mix["total_cost"]
    mix["margin_rate"] = (mix["gross_profit"] / mix["total_revenue"] * 100).round(2)
    return mix.sort_values("total_revenue", ascending=False)


def calc_customer_segment(df: pd.DataFrame) -> pd.DataFrame:
    """客户分层：企业 vs 个人"""
    seg = (
        df.groupby("customer_type")
        .agg(
            order_count=("order_id", "count"),
            total_revenue=("revenue", "sum"),
            total_cost=("cost", "sum"),
            avg_order_value=("revenue", "mean"),
            avg_satisfaction=("satisfaction", "mean"),
            return_count=("is_return", "sum"),
        )
        .reset_index()
    )
    seg["gross_profit"] = seg["total_revenue"] - seg["total_cost"]
    seg["margin_rate"] = (seg["gross_profit"] / seg["total_revenue"] * 100).round(2)
    seg["avg_order_value"] = seg["avg_order_value"].round(2)
    seg["avg_satisfaction"] = seg["avg_satisfaction"].round(2)
    seg["return_rate(%)"] = (seg["return_count"] / seg["order_count"] * 100).round(2)
    return seg


def calc_top_customers(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """TOP 客户排名"""
    top = (
        df.groupby(["customer_name", "customer_type"])
        .agg(
            order_count=("order_id", "count"),
            total_revenue=("revenue", "sum"),
            avg_satisfaction=("satisfaction", "mean"),
        )
        .reset_index()
        .sort_values("total_revenue", ascending=False)
        .head(top_n)
    )
    top["avg_satisfaction"] = top["avg_satisfaction"].round(2)
    top["total_revenue"] = top["total_revenue"].round(2)
    return top


def calc_sales_rep_ranking(df: pd.DataFrame) -> pd.DataFrame:
    """销售员业绩排名"""
    ranking = (
        df.groupby("sales_rep")
        .agg(
            order_count=("order_id", "count"),
            total_revenue=("revenue", "sum"),
            total_cost=("cost", "sum"),
            avg_satisfaction=("satisfaction", "mean"),
            customer_count=("customer_name", "nunique"),
        )
        .reset_index()
    )
    ranking["gross_profit"] = ranking["total_revenue"] - ranking["total_cost"]
    ranking["margin_rate"] = (ranking["gross_profit"] / ranking["total_revenue"] * 100).round(2)
    ranking["avg_satisfaction"] = ranking["avg_satisfaction"].round(2)
    return ranking.sort_values("total_revenue", ascending=False)


def calc_region_product_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """区域 × 产品 交叉分析"""
    matrix = (
        df.groupby(["region", "product_type"])
        .agg(total_revenue=("revenue", "sum"), order_count=("order_id", "count"))
        .reset_index()
    )
    return matrix.sort_values("total_revenue", ascending=False)


def calc_city_ranking(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """城市营收 TOP"""
    city = (
        df.groupby(["city", "region"])
        .agg(total_revenue=("revenue", "sum"), order_count=("order_id", "count"))
        .reset_index()
        .sort_values("total_revenue", ascending=False)
        .head(top_n)
    )
    city["total_revenue"] = city["total_revenue"].round(2)
    return city
