"""经营预警引擎"""

from typing import Dict, List

import pandas as pd


def check_margin_alerts(region_summary: pd.DataFrame, threshold: float) -> List[dict]:
    """毛利率低于阈值的区域预警"""
    alerts = []
    low = region_summary[region_summary["margin_rate"] < threshold]
    for _, row in low.iterrows():
        alerts.append({
            "level": "warning",
            "category": "毛利率",
            "message": f"区域 [{row['region']}] 毛利率 {row['margin_rate']}% 低于警戒线 {threshold}%",
            "region": row["region"],
            "value": row["margin_rate"],
        })
    return alerts


def check_satisfaction_alerts(df: pd.DataFrame, threshold: float) -> List[dict]:
    """满意度偏低的区域预警"""
    alerts = []
    region_sat = df.groupby("region")["satisfaction"].mean()
    for region, score in region_sat.items():
        if score < threshold:
            alerts.append({
                "level": "warning",
                "category": "客户满意度",
                "message": f"区域 [{region}] 平均满意度 {score:.1f} 低于标准 {threshold}",
                "region": region,
                "value": round(score, 2),
            })
    return alerts


def check_delivery_alerts(df: pd.DataFrame, sla_days: int) -> List[dict]:
    """超时运单预警"""
    alerts = []
    late = df[df["delivery_days"] > sla_days]
    if len(late) > 0:
        late_rate = len(late) / len(df) * 100
        alerts.append({
            "level": "danger" if late_rate > 15 else "warning",
            "category": "时效",
            "message": f"共 {len(late)} 单超时（>{sla_days}天），占比 {late_rate:.1f}%",
            "region": "全局",
            "value": round(late_rate, 2),
        })
    return alerts


def check_return_alerts(df: pd.DataFrame, threshold_pct: float = 5.0) -> List[dict]:
    """退单率预警"""
    alerts = []
    return_rate = df["is_return"].sum() / len(df) * 100
    if return_rate > threshold_pct:
        alerts.append({
            "level": "danger",
            "category": "退单",
            "message": f"全局退单率 {return_rate:.1f}% 超过阈值 {threshold_pct}%",
            "region": "全局",
            "value": round(return_rate, 2),
        })
    return alerts


def check_revenue_decline(mom: pd.DataFrame) -> List[dict]:
    """营收环比下降预警"""
    alerts = []
    if len(mom) < 2:
        return alerts
    latest = mom.iloc[-1]
    if pd.notna(latest.get("revenue_mom(%)")) and latest["revenue_mom(%)"] < -10:
        alerts.append({
            "level": "danger",
            "category": "营收趋势",
            "message": f"最新月份 [{latest['month']}] 营收环比下降 {abs(latest['revenue_mom(%)'])}%",
            "region": "全局",
            "value": latest["revenue_mom(%)"],
        })
    return alerts


def check_goal_alerts(goals: List[dict]) -> List[dict]:
    """经营目标落后预警"""
    alerts = []
    for g in goals:
        if g["status"] == "behind":
            alerts.append({
                "level": "danger",
                "category": "目标追踪",
                "message": f"[{g['period']}] {g['name']} 完成率 {g['progress_pct']}%，落后目标（差 {g['gap']}）",
                "region": "全局",
                "value": g["progress_pct"],
            })
        elif g["status"] == "at_risk":
            alerts.append({
                "level": "warning",
                "category": "目标追踪",
                "message": f"[{g['period']}] {g['name']} 完成率 {g['progress_pct']}%，存在达标风险",
                "region": "全局",
                "value": g["progress_pct"],
            })
    return alerts


def run_all_alerts(
    df: pd.DataFrame,
    region_summary: pd.DataFrame,
    mom: pd.DataFrame,
    config: dict,
) -> List[dict]:
    """运行全部预警检查"""
    analysis_cfg = config.get("analysis", {})
    margin_threshold = analysis_cfg.get("margin_warning_threshold", 20.0)
    sla_days = analysis_cfg.get("delivery_sla_days", 3)
    sat_threshold = analysis_cfg.get("satisfaction_pass_score", 4.0)

    alerts = []
    alerts.extend(check_margin_alerts(region_summary, margin_threshold))
    alerts.extend(check_satisfaction_alerts(df, sat_threshold))
    alerts.extend(check_delivery_alerts(df, sla_days))
    alerts.extend(check_return_alerts(df))
    alerts.extend(check_revenue_decline(mom))
    return alerts
