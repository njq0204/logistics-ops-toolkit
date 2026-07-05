"""数据加载与预处理"""

from pathlib import Path
from typing import Union

import pandas as pd


def load_csv(path: Union[str, Path]) -> pd.DataFrame:
    """加载 CSV 文件"""
    df = pd.read_csv(path, encoding="utf-8-sig")
    return df


def preprocess_orders(df: pd.DataFrame) -> pd.DataFrame:
    """预处理运单数据：类型转换、缺失值处理"""
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
    df["cost"] = pd.to_numeric(df["cost"], errors="coerce")
    df["weight_kg"] = pd.to_numeric(df["weight_kg"], errors="coerce")
    df = df.dropna(subset=["revenue", "cost", "region"])
    return df
