#!/usr/bin/env python3
"""生成示例运单数据（2024-2025，约 150 条）"""

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

PRODUCTS = {
    "零担快运": (800, 3500, 20, 120),
    "快递": (150, 600, 0.5, 8),
    "整车运输": (8000, 15000, 8000, 25000),
    "同城配送": (200, 800, 5, 50),
    "仓储服务": (500, 3000, 0, 0),
}

CUSTOMERS = {
    "企业客户": ["华为供应链", "美的物流", "京东仓配", "顺丰合作", "比亚迪部件", "宁德时代", "海尔智家", "格力物流"],
    "个人客户": ["张先生", "李女士", "王商户", "赵老板", "陈师傅", "刘店主"],
}

SALES_REPS = ["张伟", "李娜", "王强", "刘洋", "陈静", "赵磊", "孙婷", "周杰"]


def generate_orders(count: int = 150, seed: int = 42) -> pd.DataFrame:
    random.seed(seed)
    rows = []
    start = datetime(2024, 1, 1)

    for i in range(count):
        day_offset = random.randint(0, 500)
        date = start + timedelta(days=day_offset)
        region = random.choice(list(REGIONS.keys()))
        city = random.choice(REGIONS[region])
        product = random.choice(list(PRODUCTS.keys()))
        rev_min, rev_max, w_min, w_max = PRODUCTS[product]

        customer_type = random.choices(["企业客户", "个人客户"], weights=[0.65, 0.35])[0]
        revenue = round(random.uniform(rev_min, rev_max), 2)
        margin = random.uniform(0.18, 0.38)
        cost = round(revenue * (1 - margin), 2)
        weight = round(random.uniform(w_min, w_max), 1) if w_max > 0 else 0

        delivery_days = random.choices([1, 2, 3, 4, 5, 7], weights=[15, 25, 30, 15, 10, 5])[0]
        satisfaction = random.choices([3, 4, 5, 2, 1], weights=[10, 35, 45, 7, 3])[0]
        is_return = 1 if random.random() < 0.04 else 0

        rows.append({
            "order_id": f"ORD{date.strftime('%Y%m')}{i+1:04d}",
            "date": date.strftime("%Y-%m-%d"),
            "region": region,
            "city": city,
            "product_type": product,
            "revenue": revenue,
            "cost": cost,
            "weight_kg": weight,
            "customer_type": customer_type,
            "customer_name": random.choice(CUSTOMERS[customer_type]),
            "sales_rep": random.choice(SALES_REPS),
            "delivery_days": delivery_days,
            "satisfaction": satisfaction,
            "is_return": is_return,
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "data" / "sample" / "orders.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df = generate_orders()
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"Generated {len(df)} orders -> {out}")
