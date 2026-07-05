"""数据大屏生成器 — ECharts 可视化大屏"""

import json
import math
from pathlib import Path
from typing import Any, Union

from pipeline import AnalysisResult, result_to_api_dict


def _sanitize_for_json(obj: Any) -> Any:
    """将 NaN / Inf 转为 null，确保输出合法 JSON"""
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_for_json(v) for v in obj]
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    return obj


def export_dashboard_data(result: AnalysisResult, output_path: Union[str, Path]) -> Path:
    """导出大屏 JSON 数据"""
    output_path = Path(output_path)
    data = _sanitize_for_json(result_to_api_dict(result))
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def generate_bigscreen_html(
    output_path: Union[str, Path],
    project_name: str,
    refresh_seconds: int = 60,
    embedded_data: dict = None,
) -> Path:
    """生成数据大屏 HTML（ECharts + 内嵌数据 + 自动刷新）"""
    output_path = Path(output_path)
    embedded_json = ""
    if embedded_data:
        safe = json.dumps(_sanitize_for_json(embedded_data), ensure_ascii=False)
        safe = safe.replace("</", "<\\/")
        embedded_json = f"<script>window.__DASHBOARD_DATA__ = {safe};</script>"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{project_name} - 数据大屏</title>
<script src="https://cdn.bootcdn.net/ajax/libs/echarts/5.4.3/echarts.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{height:100%;background:#020818;color:#fff;font-family:'Microsoft YaHei',sans-serif;overflow:hidden}}
.page{{display:flex;flex-direction:column;height:100vh}}
.bg-grid{{position:fixed;inset:0;background:
  linear-gradient(rgba(0,102,204,.05) 1px,transparent 1px),
  linear-gradient(90deg,rgba(0,102,204,.05) 1px,transparent 1px);
  background-size:40px 40px;pointer-events:none;z-index:0}}
.header{{flex:0 0 64px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;
  background:linear-gradient(180deg,rgba(0,102,204,.3),transparent);border-bottom:1px solid rgba(0,150,255,.3);z-index:1}}
.header h1{{font-size:24px;letter-spacing:4px;background:linear-gradient(90deg,#4fc3f7,#fff,#4fc3f7);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.header-right{{display:flex;gap:20px;align-items:center;font-size:13px;color:#7eb8da}}
.header-right .clock{{font-size:18px;color:#4fc3f7;font-family:monospace}}
.refresh-badge{{background:rgba(0,150,255,.15);border:1px solid rgba(0,150,255,.4);
  padding:4px 12px;border-radius:20px;font-size:12px}}
.content{{flex:1;display:flex;flex-direction:column;gap:10px;padding:10px;min-height:0;z-index:1}}
.row-top{{flex:3;display:grid;grid-template-columns:1fr 1.6fr 1fr;grid-template-rows:1fr 1fr;gap:10px;min-height:0}}
.row-bottom{{flex:2;display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;min-height:0}}
.panel{{background:rgba(6,30,60,.75);border:1px solid rgba(0,150,255,.25);border-radius:8px;
  display:flex;flex-direction:column;min-height:0;overflow:hidden}}
.panel::before{{content:'';height:2px;background:linear-gradient(90deg,transparent,#0096ff,transparent)}}
.panel-title{{flex:0 0 36px;padding:8px 12px;font-size:13px;color:#4fc3f7;border-bottom:1px solid rgba(0,150,255,.15);
  display:flex;align-items:center;gap:8px}}
.panel-title::before{{content:'';width:3px;height:14px;background:#0096ff;border-radius:2px}}
.panel-body{{flex:1;padding:6px;min-height:0;position:relative}}
.kpi-grid{{display:grid;grid-template-columns:1fr 1fr;gap:8px;height:100%}}
.kpi-card{{background:rgba(0,80,160,.2);border:1px solid rgba(0,150,255,.2);border-radius:6px;
  padding:10px;text-align:center;display:flex;flex-direction:column;justify-content:center}}
.kpi-value{{font-size:22px;font-weight:700;color:#4fc3f7;font-family:monospace}}
.kpi-label{{font-size:11px;color:#7eb8da;margin-top:4px}}
.chart-box{{width:100%;height:100%;min-height:120px}}
.alert-scroll{{height:100%;overflow:hidden}}
.alert-list{{animation:scrollUp 20s linear infinite}}
.alert-item{{padding:8px 12px;margin-bottom:6px;border-radius:4px;font-size:12px;
  background:rgba(255,80,80,.1);border-left:3px solid #ff5050}}
.alert-item.warn{{background:rgba(255,180,0,.1);border-left-color:#ffb400}}
.alert-item.ok{{background:rgba(0,200,100,.1);border-left-color:#00c864}}
@keyframes scrollUp{{0%{{transform:translateY(0)}}100%{{transform:translateY(-50%)}}}}
.footer{{flex:0 0 30px;display:flex;align-items:center;justify-content:center;
  font-size:11px;color:#4a7a9a;border-top:1px solid rgba(0,150,255,.15);z-index:1}}
.center-panel{{grid-row:1/3;grid-column:2}}
.gauge-row{{display:flex;height:100%;gap:6px}}
.gauge-box{{flex:1;min-height:120px}}
.rank-table{{width:100%;font-size:12px;border-collapse:collapse}}
.rank-table th{{color:#4fc3f7;padding:6px 8px;text-align:left;border-bottom:1px solid rgba(0,150,255,.2)}}
.rank-table td{{padding:5px 8px;border-bottom:1px solid rgba(0,150,255,.08);color:#b0cce0}}
.rank-num{{display:inline-block;width:20px;height:20px;line-height:20px;text-align:center;border-radius:50%;font-size:11px;font-weight:bold}}
.rank-1{{background:#ffd700;color:#000}}.rank-2{{background:#c0c0c0;color:#000}}.rank-3{{background:#cd7f32;color:#fff}}
.rank-n{{background:rgba(0,150,255,.2);color:#4fc3f7}}
.error-banner{{background:rgba(255,80,80,.2);border:1px solid #ff5050;color:#ffaaaa;
  padding:10px 20px;text-align:center;font-size:13px;display:none;z-index:2}}
.goal-list{{height:100%;overflow-y:auto;padding:4px}}
.goal-item{{margin-bottom:10px}}
.goal-header{{display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px;color:#b0cce0}}
.goal-name{{color:#4fc3f7}}
.goal-status{{font-size:11px;padding:1px 8px;border-radius:10px}}
.goal-status.achieved{{background:rgba(0,200,100,.2);color:#00c864}}
.goal-status.on_track{{background:rgba(0,150,255,.2);color:#4fc3f7}}
.goal-status.at_risk{{background:rgba(255,180,0,.2);color:#ffb400}}
.goal-status.behind{{background:rgba(255,80,80,.2);color:#ff5050}}
.goal-bar{{height:8px;background:rgba(0,50,100,.5);border-radius:4px;overflow:hidden}}
.goal-bar-fill{{height:100%;border-radius:4px;transition:width 1s ease}}
.goal-detail{{font-size:10px;color:#6a8aaa;margin-top:2px}}
</style>
</head>
<body>
<div class="page">
<div class="bg-grid"></div>
<div class="error-banner" id="errorBanner"></div>
<div class="header">
  <h1>{project_name}</h1>
  <div class="header-right">
    <span class="refresh-badge">自动刷新 {refresh_seconds}s</span>
    <span id="updateTime">数据加载中...</span>
    <span id="diagScore" style="font-size:16px;color:#ffb400;font-weight:bold"></span>
    <span class="clock" id="clock"></span>
  </div>
</div>

<div class="content">
<div class="row-top">
  <!-- 左列 -->
  <div class="panel">
    <div class="panel-title">核心 KPI 指标</div>
    <div class="panel-body"><div class="kpi-grid" id="kpiGrid"></div></div>
  </div>
  <div class="panel">
    <div class="panel-title">产品结构分布</div>
    <div class="panel-body"><div class="chart-box" id="productChart"></div></div>
  </div>

  <!-- 中间大屏 -->
  <div class="panel center-panel">
    <div class="panel-title">各区域营收 & 单量分析</div>
    <div class="panel-body"><div class="chart-box" id="regionChart"></div></div>
  </div>

  <!-- 右列 -->
  <div class="panel">
    <div class="panel-title">经营健康度</div>
    <div class="panel-body"><div class="gauge-row">
      <div class="gauge-box" id="gaugeMargin"></div>
      <div class="gauge-box" id="gaugeOnTime"></div>
    </div></div>
  </div>
  <div class="panel">
    <div class="panel-title">预警 & 行动建议</div>
    <div class="panel-body"><div class="alert-scroll"><div class="alert-list" id="alertList"></div></div></div>
  </div>
</div>

<div class="row-bottom">
  <div class="panel">
    <div class="panel-title">月度营收趋势</div>
    <div class="panel-body"><div class="chart-box" id="trendChart"></div></div>
  </div>
  <div class="panel">
    <div class="panel-title">客户分层对比</div>
    <div class="panel-body"><div class="chart-box" id="customerChart"></div></div>
  </div>
  <div class="panel">
    <div class="panel-title">经营目标追踪</div>
    <div class="panel-body" style="display:flex;flex-direction:column;gap:4px">
      <div class="chart-box" id="goalChart" style="flex:1.2;min-height:80px"></div>
      <div class="goal-list" id="goalList" style="flex:1"></div>
    </div>
  </div>
</div>
</div>

<div class="footer">物流经营数据大屏 v3.1 · 德邦经营方向 · 海豚生 · 按 F11 全屏展示</div>
</div>
{embedded_json}
<script>
const REFRESH_SEC = {refresh_seconds};
let charts = {{}};

function updateClock() {{
  const now = new Date();
  document.getElementById('clock').textContent = now.toLocaleString('zh-CN', {{hour12:false}});
}}
setInterval(updateClock, 1000);
updateClock();

function animateValue(el, end, decimals=0, suffix='') {{
  const start = 0;
  const duration = 1200;
  const startTime = performance.now();
  function step(now) {{
    const p = Math.min((now - startTime) / duration, 1);
    const val = start + (end - start) * (1 - Math.pow(1 - p, 3));
    el.textContent = val.toFixed(decimals) + suffix;
    if (p < 1) requestAnimationFrame(step);
  }}
  requestAnimationFrame(step);
}}

function renderKPI(metrics) {{
  const keys = ['总营收(元)','总单量','毛利率(%)','准时率(%)','平均满意度','毛利(元)'];
  const grid = document.getElementById('kpiGrid');
  grid.innerHTML = '';
  keys.forEach(k => {{
    if (metrics[k] === undefined) return;
    const card = document.createElement('div');
    card.className = 'kpi-card';
    const val = document.createElement('div');
    val.className = 'kpi-value';
    const label = document.createElement('div');
    label.className = 'kpi-label';
    label.textContent = k;
    card.appendChild(val);
    card.appendChild(label);
    grid.appendChild(card);
    const v = metrics[k];
    const isPct = k.includes('%');
    animateValue(val, v, isPct ? 1 : (v > 1000 ? 0 : 2), isPct ? '%' : '');
  }});
}}

function showError(msg) {{
  const el = document.getElementById('errorBanner');
  el.textContent = msg;
  el.style.display = 'block';
}}

function initCharts() {{
  if (typeof echarts === 'undefined') {{
    showError('ECharts 加载失败，请检查网络连接后刷新页面');
    return false;
  }}
  ['regionChart','productChart','trendChart','customerChart','gaugeMargin','gaugeOnTime','goalChart'].forEach(id => {{
    const el = document.getElementById(id);
    if (el) charts[id] = echarts.init(el, null, {{renderer:'canvas'}});
  }});
  window.addEventListener('resize', () => Object.values(charts).forEach(c => c && c.resize()));
  return true;
}}

function resizeCharts() {{
  setTimeout(() => Object.values(charts).forEach(c => c && c.resize()), 100);
}}

function renderDashboard(data) {{
  if (!data || !data.metrics) {{
    showError('数据格式错误');
    return;
  }}
  document.getElementById('errorBanner').style.display = 'none';
  document.getElementById('updateTime').textContent = '更新: ' + data.updated_at;

  renderKPI(data.metrics);
  renderGoals(data.goals || [], data.goal_period || '');
  renderDiagnosis(data.diagnosis || {{}});

  if (!charts.regionChart) return;
  const regions = data.regions || [];
  charts.regionChart.setOption({{
    tooltip: {{trigger:'axis'}},
    legend: {{data:['营收','单量'],textStyle:{{color:'#7eb8da'}}}},
    grid:{{left:50,right:50,bottom:30,top:40}},
    xAxis:{{type:'category',data:regions.map(r=>r.region),axisLabel:{{color:'#7eb8da'}}}},
    yAxis:[
      {{type:'value',name:'营收',axisLabel:{{color:'#7eb8da',formatter:v=>(v/10000).toFixed(0)+'万'}}}},
      {{type:'value',name:'单量',axisLabel:{{color:'#7eb8da'}}}}
    ],
    series:[
      {{name:'营收',type:'bar',data:regions.map(r=>r.total_revenue),itemStyle:{{color:new echarts.graphic.LinearGradient(0,0,0,1,[{{offset:0,color:'#0096ff'}},{{offset:1,color:'#004080'}}])}}}},
      {{name:'单量',type:'line',yAxisIndex:1,data:regions.map(r=>r.order_count),lineStyle:{{color:'#ffb400'}},itemStyle:{{color:'#ffb400'}}}}
    ]
  }});

  // 产品饼图
  const products = data.products || [];
  charts.productChart.setOption({{
    tooltip:{{trigger:'item',formatter:'{{b}}: {{d}}%'}},
    series:[{{type:'pie',radius:['35%','65%'],center:['50%','55%'],
      data:products.map(p=>({{name:p.product_type,value:p.total_revenue}})),
      label:{{color:'#b0cce0',fontSize:11}},
      itemStyle:{{borderRadius:4,borderColor:'#020818',borderWidth:2}}
    }}]
  }});

  // 月度趋势
  const monthly = data.monthly || [];
  charts.trendChart.setOption({{
    tooltip:{{trigger:'axis'}},
    grid:{{left:50,right:20,bottom:30,top:20}},
    xAxis:{{type:'category',data:monthly.map(m=>m.month),axisLabel:{{color:'#7eb8da',rotate:30,fontSize:10}}}},
    yAxis:{{type:'value',axisLabel:{{color:'#7eb8da',formatter:v=>(v/10000).toFixed(0)+'万'}}}},
    series:[{{type:'line',smooth:true,data:monthly.map(m=>m.total_revenue),
      areaStyle:{{color:new echarts.graphic.LinearGradient(0,0,0,1,[{{offset:0,color:'rgba(0,150,255,.4)'}},{{offset:1,color:'rgba(0,150,255,0)'}}])}},
      lineStyle:{{color:'#0096ff',width:2}},itemStyle:{{color:'#4fc3f7'}}
    }}]
  }});

  // 客户分层
  const customers = data.customers || [];
  charts.customerChart.setOption({{
    tooltip:{{trigger:'axis'}},
    legend:{{data:['营收','单量'],textStyle:{{color:'#7eb8da'}}}},
    grid:{{left:50,right:20,bottom:30,top:30}},
    xAxis:{{type:'category',data:customers.map(c=>c.customer_type),axisLabel:{{color:'#7eb8da'}}}},
    yAxis:{{type:'value',axisLabel:{{color:'#7eb8da'}}}},
    series:[
      {{name:'营收',type:'bar',data:customers.map(c=>c.total_revenue),itemStyle:{{color:'#0096ff'}}}},
      {{name:'单量',type:'bar',data:customers.map(c=>c.order_count),itemStyle:{{color:'#00c864'}}}}
    ]
  }});

  // 仪表盘
  const margin = data.metrics['毛利率(%)'] || 0;
  const onTime = data.metrics['准时率(%)'] || 0;
  const gaugeOpt = (val, name, color) => ({{
    series:[{{type:'gauge',radius:'85%',center:['50%','55%'],
      min:0,max:100,splitNumber:5,
      axisLine:{{lineStyle:{{width:12,color:[[0.3,'#ff5050'],[0.7,'#ffb400'],[1,color]]}}}},
      axisLabel:{{color:'#7eb8da',fontSize:9}},detail:{{fontSize:18,color:'#fff',formatter:'{{value}}%'}},
      data:[{{value:val,name:name}}],
      title:{{color:'#7eb8da',fontSize:11,offsetCenter:[0,'70%']}}
    }}]
  }});
  charts.gaugeMargin.setOption(gaugeOpt(margin,'毛利率','#0096ff'));
  charts.gaugeOnTime.setOption(gaugeOpt(onTime,'准时率','#00c864'));

  // 目标进度横向图
  const goals = data.goals || [];
  if (charts.goalChart && goals.length > 0) {{
    const colors = {{achieved:'#00c864',on_track:'#0096ff',at_risk:'#ffb400',behind:'#ff5050'}};
    charts.goalChart.setOption({{
      tooltip:{{trigger:'axis',formatter:p=>`${{p[0].name}}: ${{p[0].value}}%`}},
      grid:{{left:90,right:40,bottom:10,top:10}},
      xAxis:{{type:'value',max:100,axisLabel:{{color:'#7eb8da',formatter:'{{value}}%'}}}},
      yAxis:{{type:'category',data:goals.map(g=>g.name).reverse(),axisLabel:{{color:'#7eb8da',fontSize:10}}}},
      series:[{{type:'bar',data:goals.map(g=>({{value:Math.min(g.progress_pct,100),itemStyle:{{color:colors[g.status]||'#0096ff'}}}})).reverse(),
        barWidth:14,label:{{show:true,position:'right',formatter:p=>p.value+'%',color:'#b0cce0',fontSize:10}}
      }}]
    }});
  }}

  // 预警 + 行动建议
  const alerts = data.alerts || [];
  const actions = (data.diagnosis || {{}}).actions || [];
  const alertEl = document.getElementById('alertList');
  let items = '';
  if (actions.length) {{
    items += actions.slice(0,5).map(a => `<div class="alert-item warn">[${{a.priority}}][${{a.area}}] ${{a.action}}</div>`).join('');
  }}
  if (alerts.length === 0 && !items) {{
    alertEl.innerHTML = '<div class="alert-item ok">所有指标正常，暂无预警</div>';
  }} else {{
    if (!items) items = alerts.map(a => `<div class="alert-item ${{a.level==='danger'?'':'warn'}}">[${{a.category}}] ${{a.message}}</div>`).join('');
    else items += alerts.map(a => `<div class="alert-item ${{a.level==='danger'?'':'warn'}}">[${{a.category}}] ${{a.message}}</div>`).join('');
    alertEl.innerHTML = items + items;
  }}

  resizeCharts();
}}

function renderDiagnosis(diag) {{
  const el = document.getElementById('diagScore');
  if (!diag || !diag.score) {{ el.textContent = ''; return; }}
  el.textContent = '评分 ' + diag.score + '/100';
}}

function renderGoals(goals, period) {{
  const el = document.getElementById('goalList');
  if (!goals.length) {{
    el.innerHTML = '<div style="color:#6a8aaa;font-size:12px;padding:10px">未配置经营目标，请编辑 config/settings.yaml</div>';
    return;
  }}
  const colors = {{achieved:'#00c864',on_track:'#0096ff',at_risk:'#ffb400',behind:'#ff5050'}};
  el.innerHTML = (period ? `<div style="font-size:11px;color:#6a8aaa;margin-bottom:8px">统计周期: ${{period}}</div>` : '') +
    goals.map(g => `
    <div class="goal-item">
      <div class="goal-header">
        <span class="goal-name">${{g.name}}</span>
        <span class="goal-status ${{g.status}}">${{g.status_label}} ${{g.progress_pct}}%</span>
      </div>
      <div class="goal-bar"><div class="goal-bar-fill" style="width:${{Math.min(g.progress_pct,100)}}%;background:${{colors[g.status]||'#0096ff'}}"></div></div>
      <div class="goal-detail">实际 ${{g.actual}} / 目标 ${{g.target}}</div>
    </div>`).join('');
}}

async function loadData() {{
  // 优先使用 HTML 内嵌数据（支持直接双击打开）
  if (window.__DASHBOARD_DATA__) {{
    renderDashboard(window.__DASHBOARD_DATA__);
  }}

  // 通过 Web 服务运行时，拉取最新数据
  if (location.protocol === 'file:') return;

  for (const url of ['/api/data', 'data.json']) {{
    try {{
      const resp = await fetch(url + '?t=' + Date.now());
      if (!resp.ok) continue;
      const data = await resp.json();
      renderDashboard(data);
      return;
    }} catch(e) {{
      console.warn('加载失败:', url, e);
    }}
  }}

  if (!window.__DASHBOARD_DATA__) {{
    showError('数据加载失败，请先运行: python main.py');
  }}
}}

window.addEventListener('DOMContentLoaded', () => {{
  if (initCharts()) loadData();
  setInterval(loadData, REFRESH_SEC * 1000);
}});
</script>
</body>
</html>"""

    output_path.write_text(html, encoding="utf-8")
    return output_path
