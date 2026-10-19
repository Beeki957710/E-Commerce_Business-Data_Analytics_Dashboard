"""
Olist E-Commerce Analytics: data preparation script
Put the original Olist CSV files in data/raw/ before running.

Expected files:
olist_orders_dataset.csv
olist_order_items_dataset.csv
olist_products_dataset.csv
olist_customers_dataset.csv
olist_order_payments_dataset.csv
olist_order_reviews_dataset.csv
olist_sellers_dataset.csv (optional)
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

def load_csv(filename, required=True):
    path = RAW / filename
    if not path.exists():
        if required:
            raise FileNotFoundError(
                f"Missing {path}. Download the Olist dataset and copy the CSV into data/raw/."
            )
        return pd.DataFrame()
    return pd.read_csv(path)

orders = load_csv("olist_orders_dataset.csv")
items = load_csv("olist_order_items_dataset.csv")
products = load_csv("olist_products_dataset.csv")
customers = load_csv("olist_customers_dataset.csv")
payments = load_csv("olist_order_payments_dataset.csv")
reviews = load_csv("olist_order_reviews_dataset.csv", required=False)
sellers = load_csv("olist_sellers_dataset.csv", required=False)

# Normalize column labels and parse dates.
for df in [orders, items, products, customers, payments, reviews, sellers]:
    if not df.empty:
        df.columns = [c.strip().lower() for c in df.columns]

date_cols = [
    "order_purchase_timestamp", "order_approved_at",
    "order_delivered_carrier_date", "order_delivered_customer_date",
    "order_estimated_delivery_date"
]
for col in date_cols:
    if col in orders.columns:
        orders[col] = pd.to_datetime(orders[col], errors="coerce")

# Numeric fields; invalid values become missing and are reported below.
for col in ["price", "freight_value"]:
    if col in items.columns:
        items[col] = pd.to_numeric(items[col], errors="coerce")
for col in ["payment_value"]:
    if col in payments.columns:
        payments[col] = pd.to_numeric(payments[col], errors="coerce")
if "review_score" in reviews.columns:
    reviews["review_score"] = pd.to_numeric(reviews["review_score"], errors="coerce")

# Remove exact duplicates and rows without keys.
orders = orders.drop_duplicates().dropna(subset=["order_id"])
items = items.drop_duplicates().dropna(subset=["order_id", "order_item_id"])
products = products.drop_duplicates().dropna(subset=["product_id"])
customers = customers.drop_duplicates().dropna(subset=["customer_id"])
payments = payments.drop_duplicates().dropna(subset=["order_id"])

# Aggregate order items to one row per order.
item_agg = items.groupby("order_id", as_index=False).agg(
    item_revenue=("price", "sum"),
    freight_total=("freight_value", "sum"),
    item_count=("order_item_id", "count"),
    distinct_products=("product_id", "nunique"),
    distinct_sellers=("seller_id", "nunique")
)

# Aggregate payments and reviews to avoid duplicating orders in the final order-level table.
payment_agg = payments.groupby("order_id", as_index=False).agg(
    payment_total=("payment_value", "sum"),
    payment_methods=("payment_type", "nunique"),
    max_installments=("payment_installments", "max")
)

if not reviews.empty and {"order_id", "review_score"}.issubset(reviews.columns):
    review_agg = reviews.groupby("order_id", as_index=False).agg(
        avg_review_score=("review_score", "mean"),
        review_count=("review_id", "nunique")
    )
else:
    review_agg = pd.DataFrame(columns=["order_id", "avg_review_score", "review_count"])

# Customer geography and repeat-customer identifier.
customer_cols = ["customer_id", "customer_unique_id", "customer_city", "customer_state"]
customer_cols = [c for c in customer_cols if c in customers.columns]
customer_dim = customers[customer_cols].drop_duplicates("customer_id")

# Product category summary at item grain.
if "product_category_name" in products.columns:
    product_dim = products[["product_id", "product_category_name"]].drop_duplicates("product_id")
else:
    product_dim = products[["product_id"]].drop_duplicates("product_id")

item_detail = items.merge(product_dim, on="product_id", how="left")
item_detail = item_detail.merge(
    orders[["order_id", "customer_id", "order_status", "order_purchase_timestamp",
            "order_delivered_customer_date", "order_estimated_delivery_date"]],
    on="order_id", how="left"
)
item_detail = item_detail.merge(customer_dim, on="customer_id", how="left")
item_detail["item_revenue"] = item_detail["price"]
item_detail["item_freight"] = item_detail["freight_value"]
item_detail.to_csv(OUT / "sales_detail.csv", index=False)

order_fact = orders.merge(item_agg, on="order_id", how="left")
order_fact = order_fact.merge(payment_agg, on="order_id", how="left")
order_fact = order_fact.merge(review_agg, on="order_id", how="left")
order_fact = order_fact.merge(customer_dim, on="customer_id", how="left")

order_fact["delivery_days"] = (
    order_fact["order_delivered_customer_date"] - order_fact["order_purchase_timestamp"]
).dt.total_seconds() / 86400
order_fact["is_delivered"] = order_fact["order_status"].eq("delivered")
order_fact["is_late"] = (
    order_fact["is_delivered"]
    & order_fact["order_delivered_customer_date"].notna()
    & order_fact["order_estimated_delivery_date"].notna()
    & (order_fact["order_delivered_customer_date"] > order_fact["order_estimated_delivery_date"])
)
order_fact["purchase_month"] = order_fact["order_purchase_timestamp"].dt.to_period("M").astype("string")
order_fact["purchase_year"] = order_fact["order_purchase_timestamp"].dt.year
order_fact["revenue"] = order_fact["item_revenue"]
order_fact["revenue_plus_freight"] = order_fact["item_revenue"] + order_fact["freight_total"]

# Revenue is not profit: Olist's core files do not provide product cost/COGS.
# Save data products for Power BI and SQL import.
order_fact.to_csv(OUT / "order_fact.csv", index=False)
item_detail.to_csv(OUT / "sales_detail.csv", index=False)
customers.to_csv(OUT / "customers.csv", index=False)
products.to_csv(OUT / "products.csv", index=False)
items.to_csv(OUT / "order_items.csv", index=False)

# Basic quality report.
quality = {
    "orders_rows": len(orders),
    "order_items_rows": len(items),
    "customers_rows": len(customers),
    "products_rows": len(products),
    "payments_rows": len(payments),
    "orders_duplicate_order_id": int(orders["order_id"].duplicated().sum()),
    "items_missing_price": int(items["price"].isna().sum()),
    "orders_missing_purchase_timestamp": int(orders["order_purchase_timestamp"].isna().sum()),
    "orders_without_items": int((~orders["order_id"].isin(items["order_id"])).sum()),
    "delivered_orders": int(order_fact["is_delivered"].sum()),
    "late_delivered_orders": int(order_fact["is_late"].sum()),
}
pd.Series(quality, name="value").to_csv(OUT / "data_quality_report.csv", header=True)

print("Data preparation complete.")
print(f"Processed files saved to: {OUT}")
print(pd.Series(quality).to_string())
print("\nImportant: revenue is not profit. Do not report profit margin without cost data.")
