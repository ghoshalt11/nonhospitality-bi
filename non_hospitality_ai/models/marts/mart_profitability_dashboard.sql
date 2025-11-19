{{ config(materialized='table') }}

SELECT
  service_category,
  city,
  date,
  total_revenue,
  total_sales_value,
  total_guests,
  avg_unit_price,
  CASE
    WHEN total_revenue >= 5000 THEN 'High Revenue'
    WHEN total_revenue BETWEEN 1000 AND 4999 THEN 'Moderate Revenue'
    ELSE 'Low Revenue'
  END AS revenue_band
FROM {{ ref('cur_service_summary') }}