"""分析流水线 — 统一调度所有分析模块"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from alert_engine import run_all_alerts
from data_loader import get_data_summary, load_data, preprocess_orders, validate_orders
from export_excel import export_to_excel
from kpi_analyzer import (
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
from report_generator import generate_html_report
from visualizer import generate_all_charts


@dataclass
class AnalysisResult:
    """分析结果容器"""
    df: pd.DataFrame
    data_summary: dict
    metrics: dict
    region_summary: pd.DataFrame
    monthly: pd.DataFrame
    mom: pd.DataFrame
    yoy: pd.DataFrame
    product_mix: pd.DataFrame
    customer_seg: pd.DataFrame
    top_customers: pd.DataFrame
    sales_ranking: pd.DataFrame
    region_product: pd.DataFrame
    city_ranking: pd.DataFrame
    alerts: List[dict]
    validation_errors: List[str] = field(default_factory=list)
    chart_paths: List[Path] = field(default_factory=list)
    html_path: Optional[Path] = None
    excel_path: Optional[Path] = None
    dashboard_path: Optional[Path] = None
    data_json_path: Optional[Path] = None
    run_at: str = ""


def run_analysis(
    data_path: Path,
    config: dict,
    output_dir: Path,
    generate_charts: bool = True,
    generate_html: bool = True,
    generate_excel: bool = True,
    generate_dashboard: bool = True,
) -> AnalysisResult:
    """执行完整分析流水线"""
    project_name = config.get("project", {}).get("name", "物流经营数据分析平台")
    dpi = config.get("visual", {}).get("dpi", 150)
    charts_dir = output_dir / "charts"
    reports_dir = output_dir / "reports"
    export_dir = output_dir / "export"
    dashboard_dir = output_dir / "dashboard"

    raw_df = load_data(data_path)
    ok, errors = validate_orders(raw_df)
    df = preprocess_orders(raw_df)

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

    result = AnalysisResult(
        df=df,
        data_summary=get_data_summary(df),
        metrics=metrics,
        region_summary=region_summary,
        monthly=monthly,
        mom=mom,
        yoy=yoy,
        product_mix=product_mix,
        customer_seg=customer_seg,
        top_customers=top_customers,
        sales_ranking=sales_ranking,
        region_product=region_product,
        city_ranking=city_ranking,
        alerts=alerts,
        validation_errors=errors if not ok else [],
        run_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    if generate_charts:
        charts_dir.mkdir(parents=True, exist_ok=True)
        result.chart_paths = generate_all_charts(
            region_summary, monthly, product_mix,
            customer_seg, sales_ranking, region_product,
            charts_dir, dpi,
        )

    if generate_html:
        reports_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        result.html_path = generate_html_report(
            reports_dir / f"report_{ts}.html",
            project_name, metrics, result.data_summary,
            region_summary, monthly, product_mix,
            customer_seg, top_customers, sales_ranking,
            mom, alerts, result.chart_paths,
        )

    if generate_excel:
        export_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        result.excel_path = export_to_excel(
            export_dir / f"analysis_{ts}.xlsx",
            metrics, region_summary, mom, product_mix,
            customer_seg, top_customers, sales_ranking, alerts,
        )

    if generate_dashboard:
        from dashboard_generator import export_dashboard_data, generate_bigscreen_html
        dashboard_dir.mkdir(parents=True, exist_ok=True)
        result.data_json_path = export_dashboard_data(result, dashboard_dir / "data.json")
        refresh_sec = config.get("dashboard", {}).get("auto_refresh_seconds", 60)
        result.dashboard_path = generate_bigscreen_html(
            dashboard_dir / "index.html",
            project_name,
            refresh_sec,
        )

    return result


def result_to_api_dict(result: AnalysisResult) -> Dict[str, Any]:
    """将分析结果转为 API / 大屏 JSON"""
    return {
        "updated_at": result.run_at,
        "data_summary": result.data_summary,
        "metrics": result.metrics,
        "regions": result.region_summary.to_dict(orient="records"),
        "monthly": result.monthly.to_dict(orient="records"),
        "mom": result.mom.to_dict(orient="records"),
        "products": result.product_mix.to_dict(orient="records"),
        "customers": result.customer_seg.to_dict(orient="records"),
        "top_customers": result.top_customers.to_dict(orient="records"),
        "sales": result.sales_ranking.to_dict(orient="records"),
        "cities": result.city_ranking.to_dict(orient="records"),
        "alerts": result.alerts,
    }
