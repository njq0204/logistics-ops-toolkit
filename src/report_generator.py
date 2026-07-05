"""HTML 分析报告生成器"""

from datetime import datetime
from pathlib import Path
from typing import List, Union

import pandas as pd


def _df_to_html(df: pd.DataFrame, max_rows: int = 20) -> str:
    return df.head(max_rows).to_html(index=False, classes="data-table", border=0)


def _alert_badge(level: str) -> str:
    colors = {"danger": "#e74c3c", "warning": "#f39c12", "info": "#3498db"}
    return colors.get(level, "#95a5a6")


def generate_html_report(
    output_path: Union[str, Path],
    project_name: str,
    metrics: dict,
    data_summary: dict,
    region_summary: pd.DataFrame,
    monthly: pd.DataFrame,
    product_mix: pd.DataFrame,
    customer_seg: pd.DataFrame,
    top_customers: pd.DataFrame,
    sales_ranking: pd.DataFrame,
    mom: pd.DataFrame,
    alerts: List[dict],
    chart_paths: List[Path],
) -> Path:
    """生成完整的 HTML 经营分析报告"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    chart_tags = ""
    for cp in chart_paths:
        rel = cp.name
        chart_tags += f'<div class="chart-card"><img src="../charts/{rel}" alt="{rel}"><p>{cp.stem}</p></div>\n'

    alert_html = ""
    if alerts:
        for a in alerts:
            color = _alert_badge(a.get("level", "info"))
            alert_html += f'<div class="alert" style="border-left:4px solid {color}"><strong>[{a.get("category","")}]</strong> {a["message"]}</div>\n'
    else:
        alert_html = '<div class="alert ok">所有指标正常，暂无预警</div>'

    kpi_cards = ""
    for k, v in metrics.items():
        kpi_cards += f'<div class="kpi-card"><div class="kpi-value">{v}</div><div class="kpi-label">{k}</div></div>\n'

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{project_name} - 经营分析报告</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:'Microsoft YaHei','Segoe UI',sans-serif; background:#f0f2f5; color:#333; }}
  .header {{ background:linear-gradient(135deg,#0066CC,#004999); color:#fff; padding:32px 40px; }}
  .header h1 {{ font-size:28px; margin-bottom:8px; }}
  .header p {{ opacity:0.85; font-size:14px; }}
  .container {{ max-width:1200px; margin:0 auto; padding:24px; }}
  .section {{ background:#fff; border-radius:12px; padding:24px; margin-bottom:20px; box-shadow:0 2px 8px rgba(0,0,0,0.06); }}
  .section h2 {{ font-size:18px; color:#0066CC; margin-bottom:16px; padding-bottom:8px; border-bottom:2px solid #e8f0fe; }}
  .kpi-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(160px,1fr)); gap:12px; }}
  .kpi-card {{ background:#f8faff; border-radius:8px; padding:16px; text-align:center; border:1px solid #e8f0fe; }}
  .kpi-value {{ font-size:22px; font-weight:700; color:#0066CC; }}
  .kpi-label {{ font-size:12px; color:#666; margin-top:4px; }}
  .data-table {{ width:100%; border-collapse:collapse; font-size:13px; }}
  .data-table th {{ background:#0066CC; color:#fff; padding:10px 12px; text-align:left; }}
  .data-table td {{ padding:8px 12px; border-bottom:1px solid #eee; }}
  .data-table tr:hover {{ background:#f8faff; }}
  .alert {{ padding:12px 16px; margin-bottom:8px; background:#fff8f0; border-radius:6px; font-size:14px; }}
  .alert.ok {{ background:#f0fff4; border-left:4px solid #00AA66; }}
  .chart-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(360px,1fr)); gap:16px; }}
  .chart-card {{ text-align:center; }}
  .chart-card img {{ max-width:100%; border-radius:8px; border:1px solid #eee; }}
  .chart-card p {{ font-size:13px; color:#666; margin-top:8px; }}
  .summary-bar {{ display:flex; gap:24px; flex-wrap:wrap; font-size:14px; color:#555; margin-bottom:16px; }}
  .summary-bar span {{ background:#e8f0fe; padding:6px 14px; border-radius:20px; }}
  .footer {{ text-align:center; padding:20px; color:#999; font-size:12px; }}
</style>
</head>
<body>
<div class="header">
  <h1>{project_name}</h1>
  <p>经营分析报告 · 生成时间 {now}</p>
</div>
<div class="container">

  <div class="section">
    <h2>数据概览</h2>
    <div class="summary-bar">
      {"".join(f'<span>{k}: {v}</span>' for k, v in data_summary.items())}
    </div>
  </div>

  <div class="section">
    <h2>核心 KPI</h2>
    <div class="kpi-grid">{kpi_cards}</div>
  </div>

  <div class="section">
    <h2>经营预警</h2>
    {alert_html}
  </div>

  <div class="section">
    <h2>可视化图表</h2>
    <div class="chart-grid">{chart_tags}</div>
  </div>

  <div class="section">
    <h2>区域营收分析</h2>
    {_df_to_html(region_summary)}
  </div>

  <div class="section">
    <h2>月度趋势 & 环比</h2>
    {_df_to_html(mom)}
  </div>

  <div class="section">
    <h2>产品结构</h2>
    {_df_to_html(product_mix)}
  </div>

  <div class="section">
    <h2>客户分层</h2>
    {_df_to_html(customer_seg)}
  </div>

  <div class="section">
    <h2>TOP 10 客户</h2>
    {_df_to_html(top_customers)}
  </div>

  <div class="section">
    <h2>销售员业绩排名</h2>
    {_df_to_html(sales_ranking)}
  </div>

</div>
<div class="footer">物流经营数据分析平台 v2.0 · 德邦经营方向 · 海豚生</div>
</body>
</html>"""

    output_path.write_text(html, encoding="utf-8")
    return output_path
