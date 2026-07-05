#!/usr/bin/env python3
"""生成德邦经营向示例运单数据"""

import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

REGIONS = {
    "华东": ["上海", "杭州", "南京", "苏州", "合肥"],
    "华南": ["广州", "深圳", "东莞", "佛山", "厦门"],
    "华北": ["北京", "天津", "石家庄", "济南", "青岛"],
    "华中": ["武汉", "长沙", "郑州", "南昌", "合肥"],
    "西南": ["成都", "重庆", "昆明", "贵阳", "拉萨"],
}

# 德邦经营产品体系
PRODUCTS = {
    "大件快递": (300, 1200, 5, 80),
    "精准卡航": (800, 3500, 20, 500),
    "精准汽运": (600, 2800, 30, 800),
    "同城当日达": (150, 600, 1, 30),
    "整车运输": (8000, 15000, 8000, 25000),
    "仓储配送": (500, 3000, 0, 0),
}

DISTANCE_TYPES = ["同城", "省内", "跨省"]
DISTANCE_WEIGHTS = [0.25, 0.35, 0.40]

CUSTOMERS = {
    "企业客户": ["华为供应链", "美的物流", "京东仓配", "顺丰合作", "比亚迪部件", "宁德时代", "海尔智家", "格力物流"],
    "个人客户": ["张先生", "李女士", "王商户", "赵老板", "陈师傅", "刘店主"],
}

SALES_REPS = ["张伟", "李娜", "王强", "刘洋", "陈静", "赵磊", "孙婷", "周杰"]


def _billing_weight(actual_kg: float, product: str) -> float:
    """模拟重泡比计费：体积大则计费重量 > 实际重量"""
    if actual_kg <= 0:
        return 0
    ratio = random.uniform(1.0, 1.8) if product in ("大件快递", "精准卡航") else random.uniform(1.0, 1.3)
    return round(actual_kg * ratio, 1)


def generate_orders(count: int = 150, seed: int = 42) -> pd.DataFrame:
    random.seed(seed)
    rows = []
    start = datetime(2024, 1, 1)

    for i in range(count):
        day_offset = random.randint(0, 500)
        date = start + timedelta(days=day_offset)
        region = random.choice(list(REGIONS.keys()))
        city = random.choice(REGIONS[region])
        product = random.choices(
            list(PRODUCTS.keys()),
            weights=[20, 25, 20, 15, 10, 10],
        )[0]
        rev_min, rev_max, w_min, w_max = PRODUCTS[product]

        customer_type = random.choices(["企业客户", "个人客户"], weights=[0.65, 0.35])[0]
        revenue = round(random.uniform(rev_min, rev_max), 2)
        margin = random.uniform(0.18, 0.38)
        cost = round(revenue * (1 - margin), 2)
        weight = round(random.uniform(w_min, w_max), 1) if w_max > 0 else 0
        billing_weight = _billing_weight(weight, product)
        distance_type = random.choices(DISTANCE_TYPES, weights=DISTANCE_WEIGHTS)[0]

        delivery_days = random.choices([1, 2, 3, 4, 5, 7], weights=[15, 25, 30, 15, 10, 5])[0]
        satisfaction = random.choices([3, 4, 5, 2, 1], weights=[10, 35, 45, 7, 3])[0]
        is_return = 1 if random.random() < 0.04 else 0
        is_complaint = 1 if satisfaction <= 2 or (is_return and random.random() < 0.5) else 0

        rows.append({
            "order_id": f"ORD{date.strftime('%Y%m')}{i+1:04d}",
            "date": date.strftime("%Y-%m-%d"),
            "region": region,
            "city": city,
            "product_type": product,
            "distance_type": distance_type,
            "revenue": revenue,
            "cost": cost,
            "weight_kg": weight,
            "billing_weight_kg": billing_weight,
            "customer_type": customer_type,
            "customer_name": random.choice(CUSTOMERS[customer_type]),
            "sales_rep": random.choice(SALES_REPS),
            "delivery_days": delivery_days,
            "satisfaction": satisfaction,
            "is_return": is_return,
            "is_complaint": is_complaint,
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "data" / "sample" / "orders.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df = generate_orders()
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"Generated {len(df)} orders -> {out}")
