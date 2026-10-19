-- SQLite schema for the prepared Olist data.
-- For today's project, you can import the processed CSVs into SQLite or load them into Power BI.
CREATE TABLE IF NOT EXISTS order_fact (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT,
    order_status TEXT,
    order_purchase_timestamp TEXT,
    order_delivered_customer_date TEXT,
    order_estimated_delivery_date TEXT,
    item_revenue REAL,
    freight_total REAL,
    item_count INTEGER,
    distinct_products INTEGER,
    distinct_sellers INTEGER,
    payment_total REAL,
    payment_methods INTEGER,
    max_installments INTEGER,
    avg_review_score REAL,
    review_count INTEGER,
    customer_unique_id TEXT,
    customer_city TEXT,
    customer_state TEXT,
    delivery_days REAL,
    is_delivered INTEGER,
    is_late INTEGER,
    purchase_month TEXT,
    purchase_year INTEGER,
    revenue REAL,
    revenue_plus_freight REAL
);

CREATE TABLE IF NOT EXISTS sales_detail (
    order_id TEXT,
    order_item_id INTEGER,
    product_id TEXT,
    seller_id TEXT,
    price REAL,
    freight_value REAL,
    product_category_name TEXT,
    customer_id TEXT,
    order_status TEXT,
    order_purchase_timestamp TEXT,
    order_delivered_customer_date TEXT,
    order_estimated_delivery_date TEXT,
    customer_unique_id TEXT,
    customer_city TEXT,
    customer_state TEXT,
    item_revenue REAL,
    item_freight REAL
);

CREATE INDEX IF NOT EXISTS idx_order_fact_purchase_date
ON order_fact(order_purchase_timestamp);
CREATE INDEX IF NOT EXISTS idx_sales_detail_category
ON sales_detail(product_category_name);
CREATE INDEX IF NOT EXISTS idx_sales_detail_order
ON sales_detail(order_id);
