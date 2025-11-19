{{ config(materialized='view') }}

SELECT
  SAFE_CAST(Transaction_ID AS STRING) AS transaction_id,
  SAFE_CAST(Guest_ID AS STRING) AS guest_id,
  DATE(Transaction_Date) AS transaction_date,
  SAFE_CAST(Transaction_Time AS TIME) AS transaction_time,
  INITCAP(City) AS city,
  INITCAP(Service_Category) AS service_category,
  INITCAP(Service_Item) AS service_item,
  SAFE_CAST(Quantity AS INT64) AS quantity,
  SAFE_CAST(Unit_Price_USD AS FLOAT64) AS unit_price_usd,
  SAFE_CAST(Total_Amount_USD AS FLOAT64) AS total_amount_usd,
  INITCAP(Payment_Method) AS payment_method,
  SAFE_CAST(Is_Guest AS BOOL) AS is_guest,
  INITCAP(Guest_Type) AS guest_type,
  CURRENT_TIMESTAMP() AS load_timestamp
FROM {{ source('sales_tran', 'sales_tran') }}
WHERE Total_Amount_USD IS NOT NULL