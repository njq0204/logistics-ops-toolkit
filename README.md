# 物流经营数据分析平台 v3.0

> 德邦经营方向 · 海豚生 实战项目  
> 一站式物流经营分析 · **数据大屏** · **自动化调度** · 预警 · 报告

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com)
[![ECharts](https://img.shields.io/badge/ECharts-5.0-red.svg)](https://echarts.apache.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## v3.0 新特性

| 模块 | 功能 |
|------|------|
| **数据大屏** | ECharts 暗色科技风大屏，KPI 动画、区域柱状图、仪表盘、预警滚动 |
| **Web 服务** | Flask 本地服务，浏览器实时查看，API 接口 |
| **自动刷新** | 大屏每 60 秒自动拉取最新数据 |
| **定时任务** | 按间隔自动运行分析，更新报告和大屏 |
| **文件监听** | 新 CSV/Excel 放入 inbox 自动触发分析 |
| **GitHub Actions** | 每周自动生成报告并上传 Artifact |
| **一键启动** | `start_bigscreen.py` 启动服务并打开浏览器 |

---

## 项目结构

```
logistics-ops-toolkit/
├── main.py                         # 主入口
├── config/settings.yaml            # 全局配置
├── scripts/
│   ├── generate_sample_data.py     # 生成示例数据
│   ├── start_bigscreen.py          # 一键启动大屏 ★
│   ├── auto_scheduler.py           # 定时自动分析 ★
│   └── watch_inbox.py              # 文件监听自动化 ★
├── src/
│   ├── pipeline.py                 # 分析流水线
│   ├── dashboard_generator.py      # 大屏 HTML + JSON ★
│   ├── web_server.py               # Flask Web 服务 ★
│   ├── kpi_analyzer.py             # KPI 计算
│   ├── alert_engine.py             # 预警引擎
│   ├── visualizer.py               # Matplotlib 图表
│   ├── report_generator.py         # HTML 报告
│   └── export_excel.py             # Excel 导出
├── data/
│   ├── sample/orders.csv           # 示例数据
│   ├── inbox/                      # 自动监听投递箱 ★
│   └── processed/                  # 已处理归档
├── .github/workflows/
│   └── auto-report.yml             # CI 自动报告 ★
└── output/
    ├── charts/                     # 静态图表
    ├── reports/                    # HTML 报告
    ├── export/                     # Excel
    └── dashboard/                  # 数据大屏 ★
        ├── index.html
        └── data.json
```

---

## 快速开始

```bash
pip install -r requirements.txt
python main.py
python scripts/start_bigscreen.py
```

浏览器自动打开 **http://127.0.0.1:8080**，按 **F11** 全屏展示大屏。

---

## 数据大屏

### 启动方式

```bash
# 方式 1：一键启动（推荐）
python scripts/start_bigscreen.py

# 方式 2：分析 + 启动服务
python main.py --serve

# 方式 3：自定义端口
python scripts/start_bigscreen.py --port 9090
```

### 大屏内容

- 核心 KPI 数字动画（营收、单量、毛利率、准时率等）
- 区域营收 & 单量双轴图
- 产品结构饼图
- 月度营收趋势
- 客户分层对比
- 毛利率 / 准时率仪表盘
- 经营预警滚动播报
- 销售员 TOP 5 排名
- 每 60 秒自动刷新数据

---

## 自动化

### 1. 定时自动分析

```bash
# 每 30 分钟自动运行（默认）
python scripts/auto_scheduler.py

# 每 10 分钟
python scripts/auto_scheduler.py --interval 10

# 只运行一次
python scripts/auto_scheduler.py --once
```

### 2. 文件监听（Drop & Analyze）

```bash
# 启动监听
python scripts/watch_inbox.py

# 把 CSV/Excel 丢进 data/inbox/ → 自动分析 → 更新大屏
```

### 3. GitHub Actions 自动报告

推送到 GitHub 后，每周一自动生成分析报告，可在 Actions → Artifacts 下载。

### 4. API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 数据大屏 |
| `/api/data` | GET | 获取 JSON 数据 |
| `/api/status` | GET | 服务状态 |
| `/api/refresh` | POST | 手动触发重新分析 |

---

## 命令行参数

```bash
python main.py                          # 完整分析 + 大屏
python main.py --serve                  # 分析完启动 Web 服务
python main.py -i data.xlsx             # 指定 Excel
python main.py --no-dashboard           # 跳过大屏生成
python main.py --no-html --no-excel     # 只要图表和大屏
```

---

## 配置

编辑 `config/settings.yaml`：

```yaml
dashboard:
  auto_refresh_seconds: 60    # 大屏刷新间隔

automation:
  schedule_interval_minutes: 30
  watch_poll_seconds: 5
```

---

## 技术栈

- **Python 3.9+** — 数据处理
- **Flask** — Web 服务
- **ECharts 5** — 交互式大屏图表
- **pandas + matplotlib** — 分析与静态图表
- **GitHub Actions** — CI 自动化

---

## 关于作者

**德邦经营方向 · 海豚生**  
用数据驱动经营决策，持续学习 Python 数据分析。

---

## License

MIT License
