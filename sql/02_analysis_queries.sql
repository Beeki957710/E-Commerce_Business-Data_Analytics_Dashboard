-- Olist E-Commerce Business & Data Analytics
-- Run these after importing data/processed/order_fact.csv as order_fact
-- and data/processed/sales_detail.csv as sales_detail into your SQL database.
-- Syntax is SQLite-friendly.

-- 1. Overall order and revenue KPIs
SELECT COUNT(DISTINCT order_id) AS orders,
       ROUND(SUM(revenue), 2) AS item_revenue,
       ROUND(AVG(revenue), 2) AS avg_item_revenue_per_order
FROM order_fact
WHERE order_status = 'delivered';

-- 2. Monthly revenue trend
SELECT purchase_month,
       COUNT(DISTINCT order_id) AS orders,
       ROUND(SUM(revenue), 2) AS revenue
FROM order_fact
WHERE order_status = 'delivered'
GROUP BY purchase_month
ORDER BY purchase_month;

-- 3. Order status distribution
SELECT order_status, COUNT(*) AS order_count
FROM order_fact
GROUP BY order_status
ORDER BY order_count DESC;

-- 4. Revenue by customer state
SELECT customer_state,
       ROUND(SUM(revenue), 2) AS revenue,
       COUNT(DISTINCT order_id) AS orders
FROM order_fact
WHERE order_status = 'delivered'
GROUP BY customer_state
ORDER BY revenue DESC;

-- 5. Revenue by product category
SELECT product_category_name,
       ROUND(SUM(price), 2) AS revenue,
       COUNT(*) AS item_rows
FROM sales_detail
WHERE order_status = 'delivered'
GROUP BY product_category_name
ORDER BY revenue DESC
LIMIT 15;

-- 6. Categories with high freight relative to item revenue
SELECT product_category_name,
       ROUND(SUM(price), 2) AS revenue,
       ROUND(SUM(freight_value), 2) AS freight,
       ROUND(100.0 * SUM(freight_value) / NULLIF(SUM(price), 0), 2) AS freight_to_revenue_pct
FROM sales_detail
WHERE order_status = 'delivered'
GROUP BY product_category_name
HAVING SUM(price) > 0
ORDER BY freight_to_revenue_pct DESC
LIMIT 15;

-- 7. Average delivery time by state
SELECT customer_state,
       ROUND(AVG(delivery_days), 2) AS avg_delivery_days,
       COUNT(*) AS delivered_orders
FROM order_fact
WHERE is_delivered = 1 AND delivery_days IS NOT NULL
GROUP BY customer_state
HAVING COUNT(*) >= 30
ORDER BY avg_delivery_days DESC;

-- 8. Late delivery rate by state
SELECT customer_state,
       COUNT(*) AS delivered_orders,
       SUM(is_late) AS late_orders,
       ROUND(100.0 * SUM(is_late) / NULLIF(COUNT(*), 0), 2) AS late_rate_pct
FROM order_fact
WHERE is_delivered = 1
GROUP BY customer_state
HAVING COUNT(*) >= 30
ORDER BY late_rate_pct DESC;

-- 9. Review score vs late delivery
SELECT is_late,
       ROUND(AVG(avg_review_score), 2) AS average_review_score,
       COUNT(*) AS orders
FROM order_fact
WHERE is_delivered = 1 AND avg_review_score IS NOT NULL
GROUP BY is_late;

-- 10. Repeat customer rate (based on unique customer ID)
WITH customer_orders AS (
    SELECT customer_unique_id, COUNT(DISTINCT order_id) AS order_count
    FROM order_fact
    WHERE customer_unique_id IS NOT NULL
      AND order_status = 'delivered'
    GROUP BY customer_unique_id
)
SELECT COUNT(*) AS customers,
       SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) AS repeat_customers,
       ROUND(100.0 * SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS repeat_customer_pct
FROM customer_orders;

-- 11. Average order value by payment type
-- Uses order-level payment total; payment method detail is not retained in order_fact.
-- Use the raw payment CSV for a true payment-type breakdown.

-- 12. Orders with high freight share
SELECT order_id, revenue, freight_total,
       ROUND(100.0 * freight_total / NULLIF(revenue, 0), 2) AS freight_share_pct
FROM order_fact
WHERE revenue > 0 AND order_status = 'delivered'
ORDER BY freight_share_pct DESC
LIMIT 20;

-- 13. Revenue per order item by category
SELECT product_category_name,
       ROUND(SUM(price) / NULLIF(COUNT(*), 0), 2) AS avg_item_price,
       COUNT(*) AS items
FROM sales_detail
WHERE order_status = 'delivered'
GROUP BY product_category_name
HAVING COUNT(*) >= 30
ORDER BY avg_item_price DESC;

-- 14. Monthly late delivery rate
SELECT purchase_month,
       COUNT(*) AS delivered_orders,
       SUM(is_late) AS late_orders,
       ROUND(100.0 * SUM(is_late) / NULLIF(COUNT(*), 0), 2) AS late_rate_pct
FROM order_fact
WHERE is_delivered = 1
GROUP BY purchase_month
ORDER BY purchase_month;

-- 15. Review scores by product category
SELECT product_category_name,
       ROUND(AVG(r.avg_review_score), 2) AS avg_review_score,
       COUNT(*) AS item_rows
FROM sales_detail s
JOIN (
    SELECT order_id, AVG(review_score) AS avg_review_score
    FROM (
        SELECT order_id, avg_review_score AS review_score
        FROM order_fact
        WHERE avg_review_score IS NOT NULL
    )
    GROUP BY order_id
) r ON s.order_id = r.order_id
WHERE s.order_status = 'delivered'
GROUP BY product_category_name
ORDER BY avg_review_score ASC;

-- 16. Customer city-level revenue (top 20)
SELECT customer_city, customer_state,
       ROUND(SUM(revenue), 2) AS revenue,
       COUNT(DISTINCT order_id) AS orders
FROM order_fact
WHERE order_status = 'delivered'
GROUP BY customer_city, customer_state
ORDER BY revenue DESC
LIMIT 20;

-- 17. Average items per delivered order
SELECT ROUND(AVG(item_count), 2) AS avg_items_per_order
FROM order_fact
WHERE is_delivered = 1;

-- 18. Difference between payment total and item revenue + freight
SELECT order_id, payment_total, revenue_plus_freight,
       ROUND(payment_total - revenue_plus_freight, 2) AS difference
FROM order_fact
WHERE payment_total IS NOT NULL
  AND revenue_plus_freight IS NOT NULL
ORDER BY ABS(payment_total - revenue_plus_freight) DESC
LIMIT 25;

-- 19. Orders with missing delivery timestamps
SELECT COUNT(*) AS delivered_missing_delivery_timestamp
FROM order_fact
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NULL;

-- 20. Monthly average review score
SELECT purchase_month,
       ROUND(AVG(avg_review_score), 2) AS avg_review_score,
       COUNT(avg_review_score) AS reviewed_orders
FROM order_fact
WHERE order_status = 'delivered'
GROUP BY purchase_month
ORDER BY purchase_month;

-- Important limitation: the core dataset does not provide cost of goods sold (COGS).
-- Analyze revenue, freight, delivery and reviews; do not label revenue as profit.
