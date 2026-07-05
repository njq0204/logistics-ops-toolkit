"""经营目标追踪模块"""

from typing import List, Tuple

import pandas as pd

# 目标指标 → (数据来源, 字段名)
FIELD_SOURCES = {
    "总营收(元)": ("monthly", "total_revenue"),
    "总单量": ("monthly", "order_count"),
    "毛利(元)": ("monthly", "gross_profit"),
    "毛利率(%)": ("metrics", "毛利率(%)"),
    "准时率(%)": ("metrics", "准时率(%)"),
    "平均满意度": ("metrics", "平均满意度"),
    "单公斤营收(元)": ("metrics", "单公斤营收(元)"),
    "单公斤毛利(元)": ("metrics", "单公斤毛利(元)"),
    "客诉率(%)": ("metrics", "客诉率(%)"),
}


LOWER_IS_BETTER = {"客诉率(%)", "退单率(%)"}


def _get_status(progress: float, inverse: bool = False) -> str:
    if progress >= 100:
        return "achieved"
    if progress >= 80:
        return "on_track"
    if progress >= 60:
        return "at_risk"
    return "behind"


def _status_label(status: str) -> str:
    return {
        "achieved": "已达标",
        "on_track": "正常",
        "at_risk": "有风险",
        "behind": "落后",
    }.get(status, "未知")


def calc_goal_progress(
    metrics: dict,
    monthly: pd.DataFrame,
    goals_config: dict,
) -> Tuple[List[dict], str]:
    """
    计算经营目标完成进度。
    月度类指标取最新月份数据，质量类指标取全局 KPI。
    """
    targets = goals_config.get("targets", {})
    if not targets:
        return [], ""

    latest_month = ""
    latest_row = None
    if len(monthly) > 0:
        latest_row = monthly.iloc[-1]
        latest_month = str(latest_row.get("month", ""))

    goals = []
    for name, target in targets.items():
        target = float(target)
        source_type, key = FIELD_SOURCES.get(name, ("metrics", name))

        if source_type == "monthly" and latest_row is not None:
            actual = float(latest_row.get(key, 0) or 0)
        else:
            actual = float(metrics.get(key, 0) or 0)

        progress = round(actual / target * 100, 1) if target > 0 else 0.0
        if name in LOWER_IS_BETTER and actual > 0:
            progress = round(min(target / actual * 100, 999), 1)
            gap = round(actual - target, 2)
        else:
            gap = round(target - actual, 2)
        status = _get_status(progress)

        goals.append({
            "name": name,
            "target": target,
            "actual": round(actual, 2),
            "progress_pct": progress,
            "gap": gap,
            "status": status,
            "status_label": _status_label(status),
            "period": latest_month or goals_config.get("period_label", "当期"),
        })

    return goals, latest_month


def summarize_goals(goals: List[dict]) -> dict:
    """目标达成汇总"""
    if not goals:
        return {"total": 0, "achieved": 0, "on_track": 0, "at_risk": 0, "behind": 0}
    return {
        "total": len(goals),
        "achieved": sum(1 for g in goals if g["status"] == "achieved"),
        "on_track": sum(1 for g in goals if g["status"] == "on_track"),
        "at_risk": sum(1 for g in goals if g["status"] == "at_risk"),
        "behind": sum(1 for g in goals if g["status"] == "behind"),
        "avg_progress": round(sum(g["progress_pct"] for g in goals) / len(goals), 1),
    }
