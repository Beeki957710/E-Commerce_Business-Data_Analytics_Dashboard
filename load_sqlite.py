
import sqlite3
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "processed"
DB = BASE / "olist_analytics.db"

order_fact = pd.read_csv(DATA / "order_fact.csv")
sales_detail = pd.read_csv(DATA / "sales_detail.csv")

with sqlite3.connect(DB) as conn:
    order_fact.to_sql(
        "order_fact", conn, if_exists="replace", index=False
    )
    sales_detail.to_sql(
        "sales_detail", conn, if_exists="replace", index=False
    )

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_sales_order
        ON sales_detail(order_id)
    """)

    print("Database created successfully:", DB.name)

    for table in ["order_fact", "sales_detail"]:
        count = conn.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]
        print(f"{table}: {count:,} rows")
