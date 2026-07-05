"""Excel 报表导出"""

from pathlib import Path
from typing import Union

import pandas as pd


def export_to_excel(
    output_path: Union[str, Path],
    metrics: dict,
    region_summary: pd.DataFrame,
    monthly: pd.DataFrame,
    product_mix: pd.DataFrame,
    customer_seg: pd.DataFrame,
    top_customers: pd.DataFrame,
    sales_ranking: pd.DataFrame,
    alerts: list,
) -> Path:
    """导出多 Sheet Excel 经营分析报告"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    metrics_df = pd.DataFrame(list(metrics.items()), columns=["指标", "数值"])
    alerts_df = pd.DataFrame(alerts) if alerts else pd.DataFrame([{"message": "暂无预警"}])

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        metrics_df.to_excel(writer, sheet_name="核心KPI", index=False)
        region_summary.to_excel(writer, sheet_name="区域分析", index=False)
        monthly.to_excel(writer, sheet_name="月度趋势", index=False)
        product_mix.to_excel(writer, sheet_name="产品结构", index=False)
        customer_seg.to_excel(writer, sheet_name="客户分层", index=False)
        top_customers.to_excel(writer, sheet_name="TOP客户", index=False)
        sales_ranking.to_excel(writer, sheet_name="销售排名", index=False)
        alerts_df.to_excel(writer, sheet_name="经营预警", index=False)

    return output_path
