"""经营诊断引擎 — 发现问题 + 给出能落地赚钱的建议"""

from typing import Dict, List

import pandas as pd


def _money(v: float) -> str:
    if abs(v) >= 10000:
        return f"{v/10000:.1f}万"
    return f"{v:.0f}元"


def generate_diagnosis(
    metrics: dict,
    region_summary: pd.DataFrame,
    product_mix: pd.DataFrame,
    top_customers: pd.DataFrame,
    customer_abc: pd.DataFrame,
    distance_mix: pd.DataFrame,
    mom: pd.DataFrame,
    goals: List[dict],
    alerts: List[dict],
    config: dict,
) -> dict:
    """
    生成经营诊断报告。
    返回: highlights(亮点), risks(风险), opportunities(机会), actions(行动建议)
    """
    benchmarks = config.get("benchmarks", {})
    rev_per_kg_target = benchmarks.get("revenue_per_kg", 1.5)
    margin_target = benchmarks.get("margin_rate", 25.0)

    highlights: List[str] = []
    risks: List[str] = []
    opportunities: List[str] = []
    actions: List[dict] = []

    # --- 整体盈利 ---
    margin = metrics.get("毛利率(%)", 0)
    gross_profit = metrics.get("毛利(元)", 0)
    if margin >= margin_target:
        highlights.append(f"整体毛利率 {margin}%，高于基准 {margin_target}%，盈利模型健康")
    else:
        risks.append(f"整体毛利率仅 {margin}%，低于基准 {margin_target}%，存在「赚流水不赚利润」风险")
        actions.append({
            "priority": "高",
            "area": "定价/成本",
            "action": "排查低毛利产品与客户，对低于成本线的线路立即调价或停发",
            "expected_impact": "毛利率提升 2-3 个百分点",
        })

    # --- 单公斤 economics（零担核心）---
    rev_per_kg = metrics.get("单公斤营收(元)", 0)
    profit_per_kg = metrics.get("单公斤毛利(元)", 0)
    if rev_per_kg > 0:
        if rev_per_kg >= rev_per_kg_target:
            highlights.append(f"单公斤营收 {rev_per_kg} 元，高于基准 {rev_per_kg_target} 元，定价能力良好")
        else:
            gap = rev_per_kg_target - rev_per_kg
            risks.append(f"单公斤营收 {rev_per_kg} 元，低于基准 {rev_per_kg_target} 元，每吨少赚约 {gap*1000:.0f} 元")
            actions.append({
                "priority": "高",
                "area": "单公斤营收",
                "action": f"对单公斤营收低于 {rev_per_kg_target} 元的区域/产品做重泡比优化和报价复核，重点推「精准卡航」等高毛利产品",
                "expected_impact": f"单公斤营收提升 0.1-0.2 元，对应增收约 {_money(gap * metrics.get('总计费重量(kg)', metrics.get('总货量(kg)', 0)))}",
            })

    if profit_per_kg > 0:
        opportunities.append(f"当前单公斤毛利 {profit_per_kg} 元，若货量增长 10%，可直接增加毛利 {_money(gross_profit * 0.1)}")

    # --- 区域分析 ---
    if not region_summary.empty:
        worst = region_summary.sort_values("margin_rate").iloc[0]
        best = region_summary.sort_values("total_revenue", ascending=False).iloc[0]
        low_margin_regions = region_summary[region_summary["margin_rate"] < margin_target]
        if not low_margin_regions.empty:
            names = "、".join(low_margin_regions["region"].tolist())
            risks.append(f"{names} 毛利率低于 {margin_target}%，拉低整体利润")
            for _, row in low_margin_regions.iterrows():
                actions.append({
                    "priority": "高",
                    "area": f"区域-{row['region']}",
                    "action": f"{row['region']}区重点审查成本结构：优化提货线路、提升装载率、减少空返",
                    "expected_impact": f"该区域毛利约 {_money(row['gross_profit'])}，提升 1% 约增收 {_money(row['total_revenue']*0.01)}",
                })
        highlights.append(f"{best['region']}区营收最高（{_money(best['total_revenue'])}），可作为标杆复制经验")

    # --- 产品结构 ---
    if not product_mix.empty:
        low_prod = product_mix[product_mix["margin_rate"] < margin_target].sort_values("total_revenue", ascending=False)
        high_prod = product_mix.sort_values("margin_rate", ascending=False).iloc[0]
        if not low_prod.empty:
            p = low_prod.iloc[0]
            risks.append(f"「{p['product_type']}」营收占比 {p['revenue_share']}%，但毛利率仅 {p['margin_rate']}%")
            actions.append({
                "priority": "中",
                "area": "产品结构",
                "action": f"收缩低毛利产品「{p['product_type']}」的促销力度，引导客户转向「{high_prod['product_type']}」（毛利率 {high_prod['margin_rate']}%）",
                "expected_impact": "产品结构优化，整体毛利率提升",
            })
        opportunities.append(f"「{high_prod['product_type']}」毛利率最高（{high_prod['margin_rate']}%），可加大销售激励")

    # --- 客户 ABC ---
    if not customer_abc.empty:
        a_customers = customer_abc[customer_abc["abc_class"] == "A"]
        if not a_customers.empty:
            a_rev_share = a_customers["revenue_share"].sum()
            a_names = "、".join(a_customers["customer_name"].head(3).tolist())
            highlights.append(f"TOP 客户（A类）贡献营收 {a_rev_share:.1f}%，{a_names} 等需重点维护")
            actions.append({
                "priority": "高",
                "area": "客户经营",
                "action": f"对 A 类客户（{a_names}）制定专属服务方案和年度合同续签计划，防止流失",
                "expected_impact": f"保住 A 类客户即保住约 {_money(metrics.get('总营收(元)',0) * a_rev_share / 100)} 营收",
            })
        c_high_rev = customer_abc[(customer_abc["abc_class"] == "C") & (customer_abc["total_revenue"] > customer_abc["total_revenue"].median())]
        if not c_high_rev.empty:
            opportunities.append(f"有 {len(c_high_rev)} 个 C 类客户具备升级潜力，可通过增购转化为 B/A 类")

    # --- 距离类型 ---
    if not distance_mix.empty and "distance_type" in distance_mix.columns:
        cross = distance_mix[distance_mix["distance_type"] == "跨省"]
        local = distance_mix[distance_mix["distance_type"] == "同城"]
        if not cross.empty and not local.empty:
            cross_margin = cross.iloc[0].get("margin_rate", 0)
            local_margin = local.iloc[0].get("margin_rate", 0)
            if local_margin > cross_margin:
                opportunities.append(f"同城业务毛利率（{local_margin}%）高于跨省（{cross_margin}%），可加大同城当日达推广")

    # --- 趋势 ---
    if len(mom) >= 2:
        latest = mom.iloc[-1]
        if pd.notna(latest.get("revenue_mom(%)")) and latest["revenue_mom(%)"] < -10:
            risks.append(f"最新月 [{latest['month']}] 营收环比下降 {abs(latest['revenue_mom(%)'])}%，需紧急排查")
            actions.append({
                "priority": "紧急",
                "area": "营收趋势",
                "action": "立即召开区域经营复盘：分解单量下降是流失客户还是单价下降，制定挽回方案",
                "expected_impact": "阻止营收下滑趋势，稳住基本盘",
            })
        elif pd.notna(latest.get("revenue_mom(%)")) and latest["revenue_mom(%)"] > 5:
            highlights.append(f"最新月营收环比增长 {latest['revenue_mom(%)']}%，增长势头良好")

    # --- 时效与满意度（影响复购=赚钱）---
    on_time = metrics.get("准时率(%)", 100)
    if on_time < 75:
        risks.append(f"准时率 {on_time}% 偏低，超时直接影响客户复购和企业客户合同续签")
        actions.append({
            "priority": "高",
            "area": "时效提升",
            "action": "梳理超时率最高的 3 条线路，优化班次衔接；对超时订单做根因分析（提货/干线/派送）",
            "expected_impact": "准时率每提升 5%，客户满意度提升约 0.2 分，减少流失",
        })

    sat = metrics.get("平均满意度", 5)
    if sat < 4.0:
        risks.append(f"客户满意度 {sat} 分，低于 4.0 及格线，存在客户流失和客诉风险")
        actions.append({
            "priority": "中",
            "area": "客户体验",
            "action": "对满意度 ≤3 分的客户做回访，重点解决破损/延误/服务态度问题",
            "expected_impact": "降低退单和客诉率，保护营收",
        })

    # --- 目标追踪 ---
    for g in goals:
        if g.get("status") == "behind":
            risks.append(f"目标「{g['name']}」完成率仅 {g['progress_pct']}%（{g['period']}）")
        elif g.get("status") == "achieved":
            highlights.append(f"目标「{g['name']}」已达标（{g['progress_pct']}%）")

    # --- 从预警补充 ---
    for a in alerts:
        if a.get("category") == "目标追踪" and a not in [r for r in risks]:
            risks.append(a["message"])

    # 按优先级排序行动建议
    priority_order = {"紧急": 0, "高": 1, "中": 2, "低": 3}
    actions.sort(key=lambda x: priority_order.get(x.get("priority", "低"), 9))

    # 综合评分
    score = 70
    score += min(len(highlights) * 3, 15)
    score -= min(len(risks) * 4, 30)
    score -= len([a for a in alerts if a.get("level") == "danger"]) * 5
    score = max(0, min(100, score))

    summary = _build_summary(score, len(risks), len(actions), gross_profit)

    return {
        "score": score,
        "summary": summary,
        "highlights": highlights[:6],
        "risks": risks[:8],
        "opportunities": opportunities[:5],
        "actions": actions[:8],
    }


def _build_summary(score: int, risk_count: int, action_count: int, gross_profit: float) -> str:
    if score >= 80:
        level = "经营健康"
    elif score >= 60:
        level = "基本稳健，有改进空间"
    else:
        level = "存在较大经营风险，需立即干预"
    return (
        f"综合评分 {score}/100（{level}）。"
        f"当前毛利 {_money(gross_profit)}，识别 {risk_count} 项风险、{action_count} 条可执行建议。"
        f"优先处理「高/紧急」动作，直接作用于增收降本。"
    )
