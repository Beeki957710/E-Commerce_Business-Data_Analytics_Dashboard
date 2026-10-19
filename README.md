# E-Commerce Business & Data Analytics (Olist)

## Objective
Analyze e-commerce revenue, product categories, customer repeat behavior, delivery performance, freight costs, and review scores. Translate findings into measurable business recommendations.

## Tools
- Python / Pandas for data preparation and data-quality checks
- SQL for KPI analysis
- Power BI for interactive reporting
- Excel optionally for quick validation and pivots

## Dataset
Download the Olist Brazilian E-Commerce Public Dataset from:
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

Extract the CSVs into `data/raw/`. Do not commit large raw files to GitHub.

Expected files include:
- `olist_orders_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_products_dataset.csv`
- `olist_customers_dataset.csv`
- `olist_order_payments_dataset.csv`
- `olist_order_reviews_dataset.csv`

## Run the preparation script
From the project root:

```bash
python -m pip install -r requirements.txt
python notebooks/01_clean_and_prepare.py
```

Prepared files will be written to `data/processed/`:
- `order_fact.csv`: one row per order, for order-level KPIs
- `sales_detail.csv`: one row per order item, for category/product analysis
- `data_quality_report.csv`: basic validation checks

## SQL
Import `order_fact.csv` as `order_fact` and `sales_detail.csv` as `sales_detail` into SQLite, PostgreSQL, or another SQL database. Start with `sql/02_analysis_queries.sql`.

## Power BI dashboard
Import `order_fact.csv` and `sales_detail.csv`. Suggested pages:
1. Executive Overview: revenue, orders, average order value, monthly trend
2. Product & Category: category revenue, average item price, freight-to-revenue ratio
3. Customer: unique customers, repeat customer rate, customer geography
4. Delivery & Experience: delivery time, late delivery rate, review score

Use a single-direction relationship from `order_fact[order_id]` to `sales_detail[order_id]` only if the model's filter behavior is understood. Prefer a star schema with separate dimensions if expanding the project.

## KPI definitions
- Item revenue = sum of order-item `price` for delivered orders
- Freight total = sum of order-item `freight_value`
- Average order value = item revenue / distinct delivered orders
- Late delivery = delivered date later than estimated delivery date
- Repeat customer rate = unique customers with more than one delivered order / all unique customers with delivered orders

## Important limitation
The core Olist dataset does not provide product cost / COGS. Therefore, it supports revenue, freight, delivery, customer and review analysis, but not true profit or profit margin. Do not claim profitability unless you add a reliable cost dataset.

## Business Analyst outputs
- Business problem statement and stakeholder questions
- KPI definitions and assumptions
- Root-cause analysis of late delivery / low reviews / high freight share
- Recommendations with owners, expected impact, and success metrics

## Data Analyst outputs
- Data cleaning and quality checks
- SQL query file with 15–20 analyses
- Exploratory analysis and KPI validation
- Power BI dashboard and documented insights

## Before publishing
- Verify all figures against the raw data
- Record the actual findings; do not invent results
- Add screenshots to `dashboard/`
- Add a concise findings report to `reports/`
