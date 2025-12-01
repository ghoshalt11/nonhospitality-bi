import json
from vertex_utils import get_vertex_client

from schema_loader import load_all_schemas
from sql_prompt_builder import build_sql_prompt
from sql_executor import run_llm_sql_generation, run_bigquery_sql
from summary_engine import summarize_results_with_llm


schemas = load_all_schemas()


def answer_user_query(user_query):
    client = get_vertex_client()

    result = {
        "sql": None,
        "dataframe": None,
        "summary": None,
        "uses_market_data": False,
        "uses_ml_prediction": False,
        "error": None
    }

    # Step 1 — SQL Prompt
    try:
        sql_prompt = build_sql_prompt(user_query, schemas)
    except Exception as e:
        result["error"] = f"Prompt Build Error: {e}"
        return result

    # Step 2 — LLM SQL Generation
    try:
        sql, use_market, use_ml = run_llm_sql_generation(client, sql_prompt)

        result["sql"] = sql
        result["uses_market_data"] = use_market
        result["uses_ml_prediction"] = use_ml

        if not sql:
            raise ValueError("Generated SQL was empty.")

    except Exception as e:
        result["error"] = f"SQL Generation Error: {e}"
        return result

    # Step 3 — Run SQL
    try:
        df = run_bigquery_sql(sql)
        result["dataframe"] = df

        if df is None or df.empty:
            result["summary"] = "No data available for this query."
            return result

    except Exception as e:
        result["error"] = f"BigQuery Execution Error: {e}"
        return result

    # Step 4 — Summary
    try:
        result["summary"] = summarize_results_with_llm(client, user_query, df)
    except Exception as e:
        result["error"] = f"Summary Error: {e}"

    return result
