# Power BI Build Guide

## Load
Import `data/processed/order_fact.csv` and `data/processed/sales_detail.csv`.

## Recommended measures (DAX)
```DAX
Item Revenue =
CALCULATE(
    SUM(order_fact[revenue]),
    order_fact[order_status] = "delivered"
)

Delivered Orders =
CALCULATE(
    DISTINCTCOUNT(order_fact[order_id]),
    order_fact[order_status] = "delivered"
)

Average Order Value =
DIVIDE([Item Revenue], [Delivered Orders])

Freight Total =
CALCULATE(
    SUM(order_fact[freight_total]),
    order_fact[order_status] = "delivered"
)

Late Delivered Orders =
CALCULATE(
    COUNTROWS(order_fact),
    order_fact[is_delivered] = TRUE(),
    order_fact[is_late] = TRUE()
)

Late Delivery Rate =
DIVIDE([Late Delivered Orders], [Delivered Orders])

Average Delivery Days =
CALCULATE(
    AVERAGE(order_fact[delivery_days]),
    order_fact[is_delivered] = TRUE()
)

Average Review Score =
CALCULATE(
    AVERAGE(order_fact[avg_review_score]),
    order_fact[is_delivered] = TRUE()
)
```

If Boolean columns import as 0/1, replace TRUE() with 1.

## Pages
1. Executive Overview: Item Revenue, Delivered Orders, Average Order Value, monthly revenue line chart, revenue by state bar chart.
2. Product Analysis: revenue by category, item count, average item price, freight-to-revenue ratio.
3. Customer Analysis: distinct customers, repeat customer rate, city/state comparisons.
4. Delivery & Experience: late delivery rate, average delivery days, average review score, late vs on-time comparison.

## Design tips
- Use consistent units and date filters.
- Label revenue as item revenue, not profit.
- Include a short insight title above each chart.
- Add a tooltip or footnote for metric definitions.
