# 物流经营数据分析平台 v3.2

> 德邦经营方向 · 海豚生 实战项目  
> **不是看数工具，是帮经营「发现问题 → 给出动作 → 估算增收」的决策助手**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com)
[![ECharts](https://img.shields.io/badge/ECharts-5.0-red.svg)](https://echarts.apache.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 这个项目解决什么问题？

网点/区域经营日常要回答的不是「营收多少」，而是：

| 经营问题 | 本工具怎么做 |
|---------|-------------|
| 赚的是真钱还是流水？ | 单公斤营收/成本/毛利 + 毛利率，对标基准线 |
| 哪个区域/产品/客户在拖后腿？ | 区域×产品热力、ABC 客户、距离结构分析 |
| 下个月该干什么？ | **自动经营诊断**：亮点 / 风险 / 机会 + **可执行行动建议（含预期增收）** |
| 目标完成了没有？ | 月度 KPI 目标追踪，大屏进度条 + Excel 目标 Sheet |
| 异常谁第一时间知道？ | 预警引擎 + 企业微信/邮件/本地日志推送 |
| 汇报材料怎么出？ | 一键生成 **16+ Sheet 专业 Excel** + HTML 报告 + ECharts 大屏 |

> 示例数据为德邦产品体系（大件快递、精准卡航、精准汽运等），字段贴近真实经营场景，可直接替换为网点导出 CSV。

---

## v3.2 核心升级 ★

| 模块 | 功能 | 经营价值 |
|------|------|---------|
| **德邦向 KPI** | 单公斤营收/成本/毛利、客诉率、跨省占比 | 零担经营核心 unit economics，一眼看定价能力 |
| **经营诊断引擎** | 综合评分 + 亮点/风险/机会 + 优先级行动建议 | 把分析结论变成「下周该干什么」，并估算增收 |
| **ABC 客户分析** | A/B/C 分层 + 营收集中度 | 识别要锁住的头部客户，防止流失 |
| **距离结构** | 同城/同省/跨省占比与 economics | 指导线路优化和报价策略 |
| **专业 Excel** | 16+ Sheet、条件格式、内嵌图表 | 直接用于周会/月会汇报，不用二次加工 |

---

## 德邦经营指标对照表

| 本工具指标 | 德邦经营语境 | 怎么用来赚钱 |
|-----------|-------------|-------------|
| **单公斤营收(元)** | 零担定价能力 / 重泡比管理 | 低于基准 → 推精准卡航等高毛利产品、复核报价 |
| **单公斤成本(元)** | 操作+干线+末端综合成本 | 高于同行 → 优化配载、减少二次中转 |
| **单公斤毛利(元)** | 每吨真实赚多少 | 货量 × 单公斤毛利 = 可预期的利润增量 |
| **毛利率(%)** | 整体盈利健康度 | 低于 25% 要排查「赚流水不赚利润」的客户/线路 |
| **准时率(%)** | 时效承诺兑现 | 每提升 5% → 减少客诉、保住 B 端合同 |
| **客诉率(%)** | 服务质量（越低越好） | 超 3% 要重点回访、查责任环节 |
| **跨省占比(%)** | 货量结构 / 干线依赖 | 跨省过高要关注干线成本和时效风险 |
| **ABC 客户** | 80/20 法则 | A 类客户专人维护，防止头部流失 |
| **距离结构** | 同城/同省/跨省 | 指导产品组合和线路资源投放 |

基准线可在 `config/settings.yaml` → `benchmarks` 按网点实际情况调整。

---

## 经营诊断示例

运行 `python main.py` 后，终端会输出类似：

```
[经营诊断] 综合评分 72/100
  [亮点]
    - 单公斤营收 1.52 元，高于基准 1.5 元
  [风险]
    - 整体毛利率仅 22%，低于基准 25%
    - 华东区毛利率低于 25%，拉低整体利润
  [行动建议 → 下周执行]
    [高] 排查低毛利产品与客户，对低于成本线的线路立即调价或停发
         -> 毛利率提升 2-3 个百分点
    [高] 对单公斤营收低于 1.5 元的区域做重泡比优化和报价复核
         -> 单公斤营收提升 0.1-0.2 元，对应增收约 877元
```

诊断结果同步写入：**Excel「经营诊断」Sheet**、**HTML 报告**、**数据大屏行动建议滚动区**。

---

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 生成德邦向示例数据（150 条运单）
python scripts/generate_sample_data.py

# 3. 一键分析（图表 + 报告 + Excel + 大屏）
python main.py

# 4. 启动数据大屏（浏览器自动打开）
python scripts/start_bigscreen.py
```

浏览器访问 **http://127.0.0.1:8080**，按 **F11** 全屏展示。

> **环境提示**：若遇 `numpy 2.x` 与 `numexpr/bottleneck` 冲突，执行 `pip install "numpy<2"` 即可。

---

## 项目结构

```
logistics-ops-toolkit/
├── main.py                         # 主入口（含诊断输出）
├── config/settings.yaml            # 配置：基准线、目标、通知
├── scripts/
│   ├── generate_sample_data.py     # 德邦向示例数据 ★
│   ├── start_bigscreen.py          # 一键启动大屏
│   ├── auto_scheduler.py           # 定时自动分析
│   ├── watch_inbox.py              # 文件监听自动化
│   └── test_notify.py              # 测试预警通知
├── src/
│   ├── pipeline.py                 # 分析流水线
│   ├── kpi_analyzer.py             # 德邦 KPI + ABC + 距离 ★
│   ├── diagnosis_engine.py         # 经营诊断 + 赚钱建议 ★
│   ├── goal_tracker.py             # 经营目标追踪
│   ├── alert_engine.py             # 预警引擎
│   ├── notifier.py                 # 企业微信/邮件通知
│   ├── dashboard_generator.py      # ECharts 大屏
│   ├── export_excel.py             # 16+ Sheet 专业 Excel ★
│   ├── report_generator.py         # HTML 报告
│   └── web_server.py               # Flask Web 服务
├── data/
│   ├── sample/orders.csv           # 示例运单
│   └── inbox/                      # 丢 CSV 自动分析
└── output/
    ├── export/analysis_*.xlsx      # 经营分析 Excel
    ├── reports/report_*.html       # HTML 报告
    ├── dashboard/index.html        # 数据大屏
    └── charts/                     # 静态图表
```

---

## Excel 输出（16+ Sheet）

| Sheet | 内容 |
|-------|------|
| 经营概览 | KPI 总览 + 诊断评分 |
| 经营诊断 | 亮点 / 风险 / 机会 |
| 行动建议 | 优先级 + 领域 + 预期影响 |
| 单公斤 economics | 区域单公斤营收/成本/毛利 |
| ABC 客户 | 客户分层与营收占比 |
| 距离结构 | 同城/同省/跨省分析 |
| 区域/产品/客户/销售 | 多维经营分析 |
| 目标追踪 | 当月 KPI 完成进度 |
| 预警明细 | 触发的经营预警 |
| 运单明细 | 原始数据（可配置行数） |

---

## 数据大屏

```bash
python scripts/start_bigscreen.py          # 推荐
python main.py --serve                     # 分析 + 启动服务
python scripts/start_bigscreen.py --port 9090
```

**大屏内容：**
- 核心 KPI 数字动画（含单公斤指标）
- 经营诊断综合评分
- 目标进度条 + 横向对比图
- 区域/产品/客户/趋势图表
- **行动建议 + 预警滚动播报**
- 每 60 秒自动刷新

---

## 自动化

```bash
# 定时分析（默认 30 分钟）
python scripts/auto_scheduler.py

# 文件监听：CSV/Excel 丢进 data/inbox/ 自动分析
python scripts/watch_inbox.py
```

GitHub Actions 每周一自动生成报告，可在 Actions → Artifacts 下载。

---

## 配置要点

编辑 `config/settings.yaml`：

```yaml
# 经营基准线（诊断对标用）
benchmarks:
  revenue_per_kg: 1.5      # 单公斤营收基准(元)
  margin_rate: 25.0        # 毛利率基准(%)
  on_time_rate: 75.0       # 准时率基准(%)
  complaint_rate: 3.0      # 客诉率上限(%)

# 月度经营目标
goals:
  targets:
    总营收(元): 50000
    毛利率(%): 28.0
    准时率(%): 75.0

# 预警通知
notifications:
  enabled: true
  channels:
    webhook:
      enabled: true
      url: "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
```

---

## 命令行参数

```bash
python main.py                          # 完整分析
python main.py --serve                  # 分析完启动 Web 服务
python main.py -i data/your_orders.csv  # 指定数据文件
python main.py --no-dashboard           # 跳过大屏
python main.py --no-html --no-excel     # 只要图表和大屏
```

---

## 替换为真实数据

CSV 需包含以下字段（列名可配置）：

| 字段 | 说明 |
|------|------|
| order_date | 下单日期 |
| region | 区域/网点 |
| product_type | 产品类型（大件快递、精准卡航等） |
| revenue | 营收 |
| cost | 成本 |
| billing_weight_kg | 计费重量 |
| distance_type | 同城/同省/跨省 |
| is_on_time | 是否准时 |
| is_complaint | 是否客诉 |
| customer_name | 客户名 |
| customer_type | 客户类型 |

把网点导出的 CSV 放入 `data/inbox/` 或 `python main.py -i your_file.csv` 即可。

---

## 技术栈

- **Python 3.9+** — pandas 数据处理
- **Flask** — Web 服务 + API
- **ECharts 5** — 交互式数据大屏
- **openpyxl** — 专业 Excel 导出
- **GitHub Actions** — CI 自动报告

---

## 关于作者

**德邦经营方向 · 海豚生**  
用数据驱动经营决策 — 不只出报表，更要给出能落地、能增收的动作。

GitHub: [njq0204/logistics-ops-toolkit](https://github.com/njq0204/logistics-ops-toolkit)

---

## License

MIT License
