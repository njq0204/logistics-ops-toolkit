"""数据加载、校验与预处理"""

from pathlib import Path
from typing import List, Optional, Tuple, Union

import pandas as pd
import yaml

REQUIRED_COLUMNS = [
    "order_id", "date", "region", "product_type",
    "revenue", "cost", "weight_kg", "customer_type",
]

OPTIONAL_COLUMNS = [
    "city", "customer_name", "sales_rep",
    "delivery_days", "satisfaction", "is_return",
    "billing_weight_kg", "distance_type", "is_complaint",
]


def load_config(config_path: Union[str, Path]) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_data(path: Union[str, Path]) -> pd.DataFrame:
    """自动识别 CSV / Excel 格式加载数据"""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path, encoding="utf-8-sig")
    if suffix in (".xlsx", ".xls"):
        return pd.read_excel(path)
    raise ValueError(f"不支持的文件格式: {suffix}，请使用 .csv 或 .xlsx")


def validate_orders(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """校验数据完整性，返回 (是否通过, 错误列表)"""
    errors = []
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        errors.append(f"缺少必要字段: {', '.join(missing)}")

    if "revenue" in df.columns and (df["revenue"] < 0).any():
        errors.append("存在负值营收记录")

    if "cost" in df.columns and (df["cost"] < 0).any():
        errors.append("存在负值成本记录")

    dup = df["order_id"].duplicated().sum() if "order_id" in df.columns else 0
    if dup > 0:
        errors.append(f"存在 {dup} 条重复运单号")

    return len(errors) == 0, errors


def preprocess_orders(df: pd.DataFrame) -> pd.DataFrame:
    """预处理运单数据"""
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
    df["cost"] = pd.to_numeric(df["cost"], errors="coerce")
    df["weight_kg"] = pd.to_numeric(df["weight_kg"], errors="coerce").fillna(0)

    for col in ["delivery_days", "satisfaction", "is_return", "is_complaint", "billing_weight_kg"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "billing_weight_kg" not in df.columns:
        df["billing_weight_kg"] = df["weight_kg"]
    else:
        df["billing_weight_kg"] = df["billing_weight_kg"].fillna(df["weight_kg"])

    if "distance_type" not in df.columns:
        df["distance_type"] = "跨省"
    if "is_complaint" not in df.columns:
        df["is_complaint"] = 0

    if "city" not in df.columns:
        df["city"] = "未知"
    if "customer_name" not in df.columns:
        df["customer_name"] = "未知客户"
    if "sales_rep" not in df.columns:
        df["sales_rep"] = "未分配"
    if "delivery_days" not in df.columns:
        df["delivery_days"] = 3
    if "satisfaction" not in df.columns:
        df["satisfaction"] = 4
    if "is_return" not in df.columns:
        df["is_return"] = 0

    df["gross_profit"] = df["revenue"] - df["cost"]
    df["margin_rate"] = (df["gross_profit"] / df["revenue"] * 100).round(2)
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["year"] = df["date"].dt.year
    df["year_month"] = df["date"].dt.strftime("%Y-%m")

    df = df.dropna(subset=["revenue", "cost", "region"])
    return df


def get_data_summary(df: pd.DataFrame) -> dict:
    """数据概览"""
    return {
        "总记录数": len(df),
        "时间范围": f"{df['date'].min().strftime('%Y-%m-%d')} ~ {df['date'].max().strftime('%Y-%m-%d')}",
        "区域数": df["region"].nunique(),
        "产品类型数": df["product_type"].nunique(),
        "客户数": df["customer_name"].nunique() if "customer_name" in df.columns else 0,
    }
