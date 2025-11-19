{{ config(materialized='table') }}

WITH base AS (
    SELECT
        service_category,
        city,
        DATE(transaction_date) AS date,
        SUM(total_amount_usd) AS total_revenue,
        SUM(quantity * unit_price_usd) AS total_sales_value,
        COUNT(DISTINCT guest_id) AS total_guests,
        AVG(unit_price_usd) AS avg_unit_price
    FROM {{ ref('stg_sales_tran') }}
    GROUP BY 1,2,3
),

-- simulate cost or maintenance expenditure per service
costs AS (
    SELECT
        service_category,
        city,
        date,
        -- assume 60% of revenue as cost baseline (to be replaced with real cost table later)
        SUM(total_revenue * 0.60) AS total_cost
    FROM base
    GROUP BY 1,2,3
)

SELECT
    b.service_category,
    b.city,
    b.date,
    b.total_revenue,
    c.total_cost,
    (b.total_revenue - c.total_cost) AS net_profit,
    SAFE_DIVIDE((b.total_revenue - c.total_cost), c.total_cost) * 100 AS profit_margin_percent
FROM base b
LEFT JOIN costs c
  ON b.service_category = c.service_category
  AND b.city = c.city
  AND b.date = c.date
