
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent / "olist_analytics.db"

queries = {
    "1. Overall business KPIs": """
        SELECT
            COUNT(*) AS total_orders,
            SUM(CASE WHEN order_status = 'delivered'
                     THEN 1 ELSE 0 END) AS delivered_orders,
            ROUND(SUM(CASE WHEN order_status = 'delivered'
                           THEN revenue ELSE 0 END), 2)
                AS delivered_item_revenue
        FROM order_fact
    """,

    "2. Monthly revenue": """
        SELECT
            purchase_month,
            COUNT(*) AS delivered_orders,
            ROUND(SUM(revenue), 2) AS item_revenue
        FROM order_fact
        WHERE order_status = 'delivered'
        GROUP BY purchase_month
        ORDER BY purchase_month
    """,

    "3. Delivery performance": """
        SELECT
            customer_state,
            COUNT(*) AS delivered_orders,
            ROUND(AVG(delivery_days), 2) AS avg_delivery_days,
            ROUND(100.0 * AVG(is_late), 2) AS late_rate_pct
        FROM order_fact
        WHERE is_delivered = 1
        GROUP BY customer_state
        HAVING COUNT(*) >= 30
        ORDER BY late_rate_pct DESC
        LIMIT 10
    """,

    "4. Top product categories": """
        SELECT
            product_category_name,
            ROUND(SUM(price), 2) AS item_revenue,
            COUNT(*) AS items_sold
        FROM sales_detail
        WHERE order_status = 'delivered'
        GROUP BY product_category_name
        ORDER BY item_revenue DESC
        LIMIT 10
    """,

    
    "5. Repeat customer rate": """
        WITH customer_orders AS (
            SELECT customer_unique_id,
                   COUNT(DISTINCT order_id) AS orders
            FROM order_fact
            WHERE order_status = 'delivered'
              AND customer_unique_id IS NOT NULL
            GROUP BY customer_unique_id
        )
        SELECT
            COUNT(*) AS unique_customers,
            SUM(CASE WHEN orders > 1 THEN 1 ELSE 0 END)
                AS repeat_customers,
            ROUND(
                100.0 * SUM(CASE WHEN orders > 1 THEN 1 ELSE 0 END)
                / COUNT(*), 2
            ) AS repeat_customer_pct
        FROM customer_orders
    """,

    "6. Late delivery and review scores": """
        SELECT
            CASE WHEN is_late = 1
                 THEN 'Late'
                 ELSE 'On time or early'
            END AS delivery_group,
            ROUND(AVG(avg_review_score), 2) AS avg_review_score,
            COUNT(*) AS orders
        FROM order_fact
        WHERE is_delivered = 1
          AND avg_review_score IS NOT NULL
        GROUP BY delivery_group
    """,

    "7. Freight burden by category": """
        SELECT
            product_category_name,
            ROUND(SUM(price), 2) AS item_revenue,
            ROUND(SUM(freight_value), 2) AS freight,
            ROUND(
                100.0 * SUM(freight_value)
                / NULLIF(SUM(price), 0), 2
            ) AS freight_to_revenue_pct
        FROM sales_detail
        WHERE order_status = 'delivered'
        GROUP BY product_category_name
        HAVING SUM(price) > 0
        ORDER BY freight_to_revenue_pct DESC
        LIMIT 10
    """

}

with sqlite3.connect(DB) as conn:
    for title, sql in queries.items():
        print(f"\n{'=' * 55}")
        print(title)
        print("=" * 55)

        for row in conn.execute(sql):
            print(row)
