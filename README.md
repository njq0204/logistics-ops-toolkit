# 物流经营数据分析平台 v2.0

> 德邦经营方向 · 海豚生 实战项目  
> 一站式物流经营 KPI 分析、可视化、预警与报告生成

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 项目亮点

| 模块 | 功能 |
|------|------|
| 核心 KPI | 营收、成本、毛利、毛利率、单均指标、准时率、满意度、退单率 |
| 区域分析 | 各区域营收/毛利/满意度/时效多维对比 |
| 趋势分析 | 月度趋势 + **环比(MoM)** + **同比(YoY)** |
| 客户分析 | 企业 vs 个人分层、TOP 10 大客户 |
| 销售分析 | 销售员业绩排名、客户覆盖数 |
| 产品分析 | 结构占比、毛利率、区域×产品热力图 |
| 城市分析 | 城市营收 TOP 10 |
| 经营预警 | 低毛利、低满意度、超时、退单、营收下滑自动预警 |
| 可视化 | 8 张专业图表自动生成 |
| 报告输出 | **HTML 交互报告** + **Excel 多 Sheet 导出** |
| 数据支持 | CSV / Excel 双格式导入，数据校验 |

---

## 项目结构

```
logistics-ops-toolkit/
├── main.py                     # 主程序入口 (CLI)
├── requirements.txt
├── README.md
├── LICENSE
├── config/
│   └── settings.yaml           # 分析参数配置
├── data/
│   └── sample/
│       └── orders.csv          # 示例数据 (150条, 2024-2025)
├── scripts/
│   └── generate_sample_data.py # 示例数据生成器
├── src/
│   ├── data_loader.py          # 数据加载 / 校验 / 预处理
│   ├── kpi_analyzer.py         # KPI 计算 (10+ 分析维度)
│   ├── alert_engine.py         # 经营预警引擎
│   ├── visualizer.py           # 8 张可视化图表
│   ├── report_generator.py     # HTML 报告生成
│   └── export_excel.py         # Excel 多 Sheet 导出
└── output/
    ├── charts/                 # 生成的图表
    ├── reports/                # HTML 报告
    └── export/                 # Excel 文件
```

---

## 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/njq0204/logistics-ops-toolkit.git
cd logistics-ops-toolkit

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行分析（默认使用示例数据）
python main.py
```

运行后在 `output/` 目录获得：
- `charts/` — 8 张分析图表
- `reports/report_YYYYMMDD_HHMM.html` — 完整 HTML 报告
- `export/analysis_YYYYMMDD_HHMM.xlsx` — Excel 多 Sheet 报表

---

## 命令行参数

```bash
python main.py                          # 默认分析
python main.py -i your_data.xlsx          # 导入 Excel 数据
python main.py -i your_data.csv           # 导入 CSV 数据
python main.py --no-html                  # 跳过 HTML 报告
python main.py --no-excel                 # 跳过 Excel 导出
python main.py --no-charts                # 跳过图表生成
python main.py -o ./my_output             # 自定义输出目录
```

---

## 数据格式

### 必要字段

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| order_id | 文本 | 运单号 | ORD202501001 |
| date | 日期 | 运单日期 | 2025-01-05 |
| region | 文本 | 区域 | 华东 |
| product_type | 文本 | 产品类型 | 零担快运 |
| revenue | 数值 | 营收(元) | 1280.50 |
| cost | 数值 | 成本(元) | 920.30 |
| weight_kg | 数值 | 重量(kg) | 45.2 |
| customer_type | 文本 | 客户类型 | 企业客户 |

### 可选字段（启用更多分析）

| 字段 | 说明 |
|------|------|
| city | 城市 |
| customer_name | 客户名称 |
| sales_rep | 销售员 |
| delivery_days | 配送时效(天) |
| satisfaction | 满意度 (1-5) |
| is_return | 是否退单 (0/1) |

### 重新生成示例数据

```bash
python scripts/generate_sample_data.py
```

---

## 分析模块详解

### 1. 核心 KPI 仪表盘
总营收、总成本、毛利、毛利率、单均营收、单均重量、准时率、平均满意度、退单率

### 2. 区域经营分析
各区域营收排名、毛利率对比、满意度、平均时效

### 3. 趋势 & 增长分析
- 月度营收/单量/毛利趋势
- 环比(MoM)：营收、单量、利润环比增长率
- 同比(YoY)：同月对比去年增长率

### 4. 客户价值分析
- 企业 vs 个人：营收、单量、客单价、满意度、退单率
- TOP 10 大客户排名

### 5. 销售绩效
销售员营收排名、毛利、客户覆盖数、满意度

### 6. 经营预警引擎
| 预警类型 | 触发条件 |
|----------|----------|
| 毛利率 | 区域毛利率 < 20% |
| 满意度 | 区域满意度 < 4.0 |
| 时效 | 超时运单占比过高 |
| 退单 | 全局退单率 > 5% |
| 营收趋势 | 环比下降 > 10% |

---

## 配置说明

编辑 `config/settings.yaml` 自定义分析参数：

```yaml
analysis:
  margin_warning_threshold: 20.0    # 毛利率预警线
  delivery_sla_days: 3              # 标准时效
  satisfaction_pass_score: 4.0      # 满意度及格线
```

---

## 输出示例

### 终端输出
```
[*] 物流经营数据分析平台 v2.0
[OK] 已加载 150 条运单 (2024-01-03 ~ 2025-05-14)

=======================================================
  核心 KPI
=======================================================
  总营收(元): 856432.50
  毛利率(%): 27.35
  准时率(%): 72.67
  ...

=======================================================
  经营预警
=======================================================
  [!] [毛利率] 区域 [西南] 毛利率 19.2% 低于警戒线 20%
```

### HTML 报告
打开 `output/reports/report_*.html`，包含 KPI 卡片、预警列表、图表、全部数据表格。

### Excel 报表
8 个 Sheet：核心KPI、区域分析、月度趋势、产品结构、客户分层、TOP客户、销售排名、经营预警

---

## 技术栈

- **Python 3.9+**
- **pandas** — 数据处理与分析
- **matplotlib** — 专业图表
- **openpyxl** — Excel 读写
- **PyYAML** — 配置管理

---

## 关于作者

**德邦经营方向 · 海豚生**  
用数据驱动经营决策，持续学习 Python 数据分析。

---

## License

MIT License
