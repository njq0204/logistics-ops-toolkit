# 物流经营数据分析工具包 🐬

> 德邦经营方向 · 海豚生 学习实践项目  
> 用 Python 做物流经营 KPI 分析，覆盖区域营收、月度趋势、产品结构等核心指标

---

## 项目简介

本项目是一个面向**物流经营方向**的数据分析入门工具，帮助快速完成：

- 📊 **经营 KPI 计算** — 营收、成本、毛利、毛利率、单均指标
- 🗺️ **区域分析** — 各区域营收排名与盈利能力对比
- 📈 **趋势分析** — 月度营收与单量变化趋势
- 🥧 **产品结构** — 零担 / 快递 / 整车等业务占比
- 📉 **可视化输出** — 自动生成分析图表

---

## 项目结构

```
logistics-ops-toolkit/
├── main.py                 # 主程序入口
├── requirements.txt        # Python 依赖
├── README.md
├── data/
│   └── sample/
│       └── orders.csv      # 示例运单数据
├── src/
│   ├── data_loader.py      # 数据加载与预处理
│   ├── kpi_analyzer.py     # KPI 计算模块
│   └── visualizer.py       # 图表生成模块
└── output/                 # 运行后生成的图表（自动创建）
```

---

## 快速开始

### 1. 克隆 / 下载项目

```bash
git clone https://github.com/你的用户名/logistics-ops-toolkit.git
cd logistics-ops-toolkit
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行分析

```bash
python main.py
```

运行后终端会输出 KPI 报表，`output/` 目录下会生成 3 张图表：

| 图表 | 说明 |
|------|------|
| `region_revenue.png` | 各区域营收对比 |
| `monthly_trend.png` | 月度营收与单量趋势 |
| `product_mix.png` | 产品结构占比 |

---

## 核心 KPI 说明

| 指标 | 含义 |
|------|------|
| 总营收 | 所有运单收入合计 |
| 总成本 | 所有运单成本合计 |
| 毛利 | 营收 − 成本 |
| 毛利率 | 毛利 / 营收 × 100% |
| 单均营收 | 总营收 / 总单量 |
| 单均重量 | 平均货物重量 (kg) |

---

## 自定义数据

将你自己的运单数据放到 `data/sample/orders.csv`，格式如下：

| 字段 | 说明 | 示例 |
|------|------|------|
| order_id | 运单号 | ORD202501001 |
| date | 日期 | 2025-01-05 |
| region | 区域 | 华东 |
| product_type | 产品类型 | 零担快运 / 快递 / 整车运输 |
| revenue | 营收（元） | 1280.50 |
| cost | 成本（元） | 920.30 |
| weight_kg | 重量（kg） | 45.2 |
| customer_type | 客户类型 | 企业客户 / 个人客户 |

---

## 技术栈

- **Python 3.10+**
- **pandas** — 数据处理
- **matplotlib** — 数据可视化

---

## 后续计划

- [ ] 支持 Excel 数据导入
- [ ] 增加客户分层分析（企业 vs 个人）
- [ ] 添加同比 / 环比计算
- [ ] 生成 HTML 分析报告

---

## 关于作者

🐬 **德邦经营方向 · 海豚生**  
正在学习物流经营数据分析，用代码驱动经营决策。

---

## License

MIT License — 自由使用、修改和分享
