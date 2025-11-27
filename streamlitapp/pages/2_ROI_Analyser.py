import streamlit as st
import pandas as pd
from google.genai import types
from google.cloud import bigquery
from vertex_utils import get_vertex_client


st.title("📊 ROI Analyzer")
st.write("Upload market competitor and launch cost data for ROI forecasting.")


client = get_vertex_client()
bq_client = bigquery.Client()


uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])


user_query = st.text_area(
"Enter your (ROI) query:",
placeholder="e.g., Estimate ROI for new gym and gaming service launches next quarter",
height=120,
)

# --- BigQuery source table ---
ROI_TABLE = "nonhospitality-bi.sales_tran.semantic_business_roi"


# if st.button("Run Analysis"):
if st.button("🚀 Run Analysis"):
        try:
            # 🟦 Step 1: Pull historical data from BigQuery
            with st.spinner("Fetching ROI historical data from BigQuery..."):
                query = f"""
                SELECT *
                FROM `{ROI_TABLE}`
                WHERE year IS NOT NULL
                ORDER BY year DESC, month DESC
                LIMIT 100
            """
            historical_df = bq_client.query(query).to_dataframe()
            
        # 🟨 Step 2: If user uploaded a file
            uploaded_context = ""
            if uploaded_file is not None:
                df = pd.read_csv(uploaded_file)
                st.success("✅ Uploaded Data Preview:")
                st.dataframe(df.head())
                uploaded_context = f"\nUploaded user data sample:\n{df.head(5).to_string(index=False)}"
            
        # 🟩 Step 3: Build context prompt
            context = f"""
            You are an AI Hotel Financial Strategist.
            Use the historical data and/or uploaded dataset to provide a detailed ROI analysis.

            Historical ROI KPIs:
            {historical_df.head(15).to_markdown()}

            User Question:
            {user_query or "No query provided."}
            {uploaded_context}

            Please provide:
            1. Predicted ROI and revenue uplift.
            2. Risk and sensitivity analysis.
            3. Executive summary with key KPIs.
            4. If possible, suggest next best business actions.
            """

        # 🟧 Step 4: Call Vertex AI Gemini model
            contents = [types.Content(role="user", parts=[types.Part.from_text(text=context)])]
            config = types.GenerateContentConfig(
            temperature=0.7,
            top_p=0.9,
            max_output_tokens=2048,
            response_modalities=["TEXT"],
        )
            with st.spinner("🔍 Analyzing ROI insights ..."):
                response_text = ""
                for chunk in client.models.generate_content_stream(
                    model="gemini-2.0-flash",
                    contents=contents,
                    config=config,
                    ):
                    if hasattr(chunk, "text") and chunk.text:
                        response_text += chunk.text


        # 🟦 Step 5: Display Results
            st.subheader("📈 ROI Analysis Summary")
            st.info(response_text)

        # Optional chart display
            st.subheader("📊 Historical ROI Trend")
            st.line_chart(historical_df, x="month", y="roi_estimate_percent", color="service_category")

        except Exception as e:
            st.error(f"⚠️ Error: {e}")
#     if uploaded_file is not None and user_query:
#             df = pd.read_csv(uploaded_file)
#             st.dataframe(df.head())
#             context = f"Data sample:\n{df.head(5).to_string(index=False)}"


#             contents = [
#                  types.Content(
#                       role="user",
#                       parts=[types.Part.from_text(text=f"""
#                                                   You are an AI Hotel Business Analyst.
#                                                   Use the uploaded data to evaluate ROI, risk, and profitability trends.
#                                                   Question: {user_query}
#         {context}
# Provide summary with key metrics and recommendations.
# """)]
# ),
# ]
            
#             config = types.GenerateContentConfig(
# temperature=0.7,
# top_p=0.9,
# max_output_tokens=2048,
# response_modalities=["TEXT"],
# )
#             with st.spinner("Analyzing ROI insights..."):
#                  response_text = ""
#                  for chunk in client.models.generate_content_stream(
# model="gemini-2.0-flash",
# contents=contents,
# config=config,
# ):
#                       if hasattr(chunk, "text") and chunk.text:
#                            response_text += chunk.text
#                            st.subheader("📈 ROI Analysis Summary")
#                            st.info(response_text)
                    
#     else:
#         st.warning("Please upload a dataset and enter a query.")