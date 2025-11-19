{{ config(materialized='table') }}

SELECT
  service_category,
  city,
  DATE(transaction_date) AS date,
  SUM(total_amount_usd) AS total_revenue,
  SUM(quantity * unit_price_usd) AS total_sales_value,
  COUNT(DISTINCT guest_id) AS total_guests,
  AVG(unit_price_usd) AS avg_unit_price
FROM {{ ref('stg_sales_tran') }}
GROUP BY 1, 2, 3