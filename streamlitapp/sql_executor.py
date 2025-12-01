import json
from google.cloud import bigquery

# -----------------------------
# LLM → SQL
# -----------------------------
def run_llm_sql_generation(client, sql_prompt):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=sql_prompt,
        config={
            "temperature": 0.0,
            "max_output_tokens": 512,
            "response_mime_type": "application/json"
        }
    )

    data = json.loads(response.text)

    return (
        data.get("sql"),
        data.get("uses_market_data", False),
        data.get("uses_ml_prediction", False)
    )

# -----------------------------
# Execute SQL in BigQuery
# -----------------------------
def run_bigquery_sql(sql):
    bq = bigquery.Client()
    return bq.query(sql).to_dataframe()
