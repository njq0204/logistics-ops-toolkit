# 输出目录

此目录用于存放运行 `python main.py` 后自动生成的分析结果。

## 目录说明

| 子目录 | 内容 |
|--------|------|
| `charts/` | 8 张分析图表 (PNG) |
| `reports/` | HTML 经营分析报告 |
| `export/` | Excel 多 Sheet 报表 |

## 如何生成

在项目根目录运行：

```bash
pip install -r requirements.txt
python main.py
```

运行完成后，用浏览器打开 `reports/report_*.html` 查看完整报告。

> 此目录下的生成文件默认不上传 GitHub（在 .gitignore 中排除）。
