import json
import pandas as pd
from datetime import datetime

def make_json_safe(df):
    out = []
    for r in df.to_dict(orient="records"):
        clean = {}
        for k, v in r.items():
            if isinstance(v, pd.Timestamp):
                clean[k] = v.isoformat()
            elif pd.isna(v):
                clean[k] = None
            elif hasattr(v, "item"):
                try:
                    clean[k] = v.item()
                except:
                    clean[k] = str(v)
            else:
                clean[k] = v
        out.append(clean)
    return out


def summarize_results_with_llm(client, user_query, df):

    safe_data = make_json_safe(df)
    today = datetime.now().strftime("%Y-%m-%d")

    prompt = f"""
You are a business analyst.

CURRENT DATE: {today}

USER QUESTION:
{user_query}

DATA (DO NOT HALLUCINATE):
{json.dumps(safe_data, indent=2)}

TASK:
- Provide insights
- Explain trends, anomalies
- Avoid hallucination
- Use ONLY data provided
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config={"temperature": 0.3}
    )

    return response.text
