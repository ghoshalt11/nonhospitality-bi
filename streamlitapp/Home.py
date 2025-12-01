import streamlit as st
import pandas as pd
import numpy as np
from google.cloud import bigquery
import vertexai
from vertexai.generative_models import GenerativeModel
import calendar


# -----------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------
st.set_page_config(page_title="Ancillary Intelligence Hub", layout="wide")
client = bigquery.Client()


# -----------------------------------------------------
# INIT VERTEX AI
# -----------------------------------------------------
vertexai.init(project="nonhospitality-bi", location="us-central1")
gemini = GenerativeModel("gemini-2.0-flash")


# -----------------------------------------------------
# AI INSIGHT GENERATOR (SHORT + BULLET POINTS)
# -----------------------------------------------------
def generate_ai_insight(service, city, roi_value, trend, mom, yoy, revenue_drop, margin_drop):
    prompt = f"""
You are a senior revenue optimization analyst.

Provide a VERY SHORT business insight for the weakest service–city pair.
STRICT: 5 bullet points, each max 12 words.

Context:
- Service: {service}
- City: {city}
- Avg ROI (3M): {roi_value:.2f}%
- ROI Trend: {trend}
- MoM ROI: {mom:.2f}%
- YoY ROI: {yoy:.2f}%
- Revenue Drop: {revenue_drop:.2f}
- Margin Drop: {margin_drop:.2f}

Deliver EXACTLY:
1. Root cause hint
2. Operational bottleneck
3. Pricing/demand issue
4. Quick action
5. Risk if not fixed

Tone: Sharp, diagnostic, no long paragraphs.
"""
    return gemini.generate_content(prompt).text


# -----------------------------------------------------
# HEADER
# -----------------------------------------------------
st.markdown("""
<h1 style='text-align:center; font-size:45px;'>
🏨 Ancillary Decision Intelligence Hub
</h1>
<p style='text-align:center; font-size:18px; color:gray; margin-top:-10px;'>
A Data-Driven Intelligence for Non-Hospitality Revenue Optimization
</p>
<hr>
""", unsafe_allow_html=True)


# -----------------------------------------------------
# FETCH DATA
# -----------------------------------------------------
with st.spinner("⏳ Loading KPIs..."):
    df = client.query("""
        SELECT service_category, city, year, month,
               roi_percent, profit_margin_pct, total_revenue,
               total_guest_count, marketing_spend_month
        FROM `nonhospitality-bi.analytics.monthly_service_kpis`
    """).to_dataframe()

df = df.sort_values(["year", "month"])
df["ym"] = df["year"] * 100 + df["month"]


# -----------------------------------------------------
# GLOBAL KPI CALCULATIONS
# -----------------------------------------------------
def compute_global_kpis(df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    yoy = df.iloc[-13] if len(df) > 12 else None

    return {
        "roi": {
            "current": latest["roi_percent"],
            "mom": latest["roi_percent"] - prev["roi_percent"],
            "yoy": (latest["roi_percent"] - yoy["roi_percent"]) if yoy is not None else None
        }
    }


kpis = compute_global_kpis(df)

# helpers
def arrow(x): return "▲" if x and x > 0 else "▼"
def color(x): return "green" if x and x > 0 else "red"


# -----------------------------------------------------
# BUSINESS SUMMARY
# -----------------------------------------------------
summary = f"""
## 🧭 Business Performance Summary

ROI trend is **{'positive' if kpis['roi']['mom'] > 0 else 'negative'}**.

Strengths:
➡ Best Service: **{df.groupby('service_category')['roi_percent'].mean().idxmax()}**  
➡ Best City: **{df.groupby('city')['roi_percent'].mean().idxmax()}**

Weak Areas:
⚠ Weakest Service: **{df.groupby('service_category')['roi_percent'].mean().idxmin()}**  
⚠ Weakest City: **{df.groupby('city')['roi_percent'].mean().idxmin()}**
"""

st.markdown(summary, unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)


# -----------------------------------------------------
# KPI CARDS (FULLY FIXED)
# -----------------------------------------------------
st.markdown("<h2>📊 Key KPIs This Month</h2>", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)

latest = df.iloc[-1]
prev = df.iloc[-2]

latest_label = f"{calendar.month_name[latest['month']]} {latest['year']}"
prev_label = f"{calendar.month_name[prev['month']]} {prev['year']}"

# MER (Marketing Efficiency Ratio)
latest_mer = latest["total_revenue"] / (latest["marketing_spend_month"] or 1)
prev_mer = prev["total_revenue"] / (prev["marketing_spend_month"] or 1)
mer_mom = latest_mer - prev_mer

with c1:
    st.markdown(f"""
    <div style='padding:20px; background:white; border-radius:14px; box-shadow:0 3px 8px rgba(0,0,0,0.08);'>
        <h4>📈 ROI</h4>
        <div style='font-size:28px; font-weight:700'>{kpis['roi']['current']:.2f}%</div>
        <p style='color:{color(kpis['roi']['mom'])}'>
            {arrow(kpis['roi']['mom'])} MoM: {kpis['roi']['mom']:.2f}%</p>
        <p style='color:{color(kpis['roi']['yoy'])}'>
            {arrow(kpis['roi']['yoy'])} YoY: {kpis['roi']['yoy']:.2f}%</p>
    </div>
    """, unsafe_allow_html=True)

# Margin
# with c2:
#     st.markdown(f"""
#     <div style='padding:20px; background:white; border-radius:14px;'>
#         <h4>💹 Margin</h4>
#         <div style='font-size:28px; font-weight:700'>{kpis['margin']['current']:.2f}%</div>
#         <p style='color:{color(kpis['margin']['mom'])}'>{arrow(kpis['margin']['mom'])} MoM: {kpis['margin']['mom']:.2f}%</p>
#         <p style='color:{color(kpis['margin']['yoy'])}'>{arrow(kpis['margin']['yoy'])} YoY: {kpis['margin']['yoy']:.2f}%</p>
#     </div>
#     """, unsafe_allow_html=True)



# ROI CARD
# with c1:
#     st.markdown(f"""
#     <div style='padding:20px; background:white; border-radius:14px;
#                 box-shadow:0 3px 8px rgba(0,0,0,0.08);'>

#         <h4>📈 ROI</h4>

#         <div style='font-size:28px; font-weight:700'>
#             {kpis['roi']['current']:.2f}%
#             <span style='font-size:14px; color:gray'>({latest_label})</span>
#         </div>

#         <p style='color:{color(kpis['roi']['mom'])};'>
#             {arrow(kpis['roi']['mom'])} MoM vs {prev_label}: {kpis['roi']['mom']:.2f}%<br>
#             <span style='font-size:12px; color:gray'>
#                 {"Improving 👍" if kpis['roi']['mom'] > 0 else "Declining ⚠️"}
#             </span>
#         </p>

#         <p style='color:{color(kpis['roi']['yoy'])};'>
#             {arrow(kpis['roi']['yoy'])} YoY: {kpis['roi']['yoy']:.2f}%<br>
#             <span style='font-size:12px; color:gray'>
#                 {"Better than last year 💹" if kpis['roi']['yoy'] and kpis['roi']['yoy'] > 0 else "Worse vs last year 🚨"}
#             </span>
#         </p>

        

#     </div>
#     """, unsafe_allow_html=True)
# with c1:
#     roi_current = f"{kpis['roi']['current']:.2f}%"
#     roi_mom = f"{kpis['roi']['mom']:.2f}%"
#     roi_yoy = f"{kpis['roi']['yoy']:.2f}%"
#     mer_current = f"{latest_mer:.2f}"
#     mer_mom_val = f"{mer_mom:.2f}"

#     roi_mom_text = "Improving 👍" if kpis['roi']['mom'] > 0 else "Declining ⚠️"
#     roi_yoy_text = "Better than last year 💹" if kpis['roi']['yoy'] and kpis['roi']['yoy'] > 0 else "Worse vs last year 🚨"
#     mer_mom_text = "More efficient marketing 👍" if mer_mom > 0 else "Marketing efficiency declined ⚠️"

#     st.markdown(
#         f"""
#         <div style='padding:20px; background:white; border-radius:14px;
#                     box-shadow:0 3px 8px rgba(0,0,0,0.08);'>

#             <h4>📈 ROI</h4>
#             <div style='font-size:28px; font-weight:700'>
#                 {roi_current}
#                 <span style='font-size:14px; color:gray'>({latest_label})</span>
#             </div>

#             <p style='color:{color(kpis['roi']['mom'])};'>
#                 {arrow(kpis['roi']['mom'])} MoM vs {prev_label}: {roi_mom}<br>
#                 <span style='font-size:12px; color:gray'>
#                     {roi_mom_text}
#                 </span>
#             </p>

#             <p style='color:{color(kpis['roi']['yoy'])};'>
#                 {arrow(kpis['roi']['yoy'])} YoY: {roi_yoy}<br>
#                 <span style='font-size:12px; color:gray'>
#                     {roi_yoy_text}
#                 </span>
#             </p>

#             <hr style='margin:8px 0;'>

#             <h4>📊 MER</h4>
#             <div style='font-size:22px; font-weight:600'>
#                 {mer_current}
#                 <span style='font-size:13px; color:gray'>Revenue per $1 spent</span>
#             </div>

#             <p style='color:{color(mer_mom)};'>
#                 {arrow(mer_mom)} MoM MER Change: {mer_mom_val}<br>
#                 <span style='font-size:12px; color:gray'>
#                     {mer_mom_text}
#                 </span>
#             </p>

#         </div>
#         """,
#         unsafe_allow_html=True,
#     )



st.markdown("<hr>", unsafe_allow_html=True)


# -----------------------------------------------------
# WEAKEST SERVICE–CITY PAIR (3M)
# -----------------------------------------------------
st.subheader("⛔ Weakest Service–City Pair (Last 3 Months)")

latest_ym = df["ym"].max()
last_three = df[df["ym"] >= latest_ym - 2]

weak_pair = (
    last_three.groupby(["service_category", "city"])["roi_percent"]
    .mean()
    .reset_index()
    .sort_values("roi_percent")
    .iloc[0]
)

svc = weak_pair["service_category"]
city = weak_pair["city"]
roi_val = weak_pair["roi_percent"]

recent = last_three[(last_three["service_category"] == svc) & (last_three["city"] == city)]
mom = recent["roi_percent"].iloc[-1] - recent["roi_percent"].iloc[-2]
yoy = mom
rev_drop = recent["total_revenue"].iloc[-1] - recent["total_revenue"].iloc[-2]
margin_drop = recent["profit_margin_pct"].iloc[-1] - recent["profit_margin_pct"].iloc[-2]
trend = "Upward" if mom > 0 else "Declining"

st.markdown(f"""
<div style="padding:18px; background:white; border-left:6px solid #E74A3B;
            border-radius:16px; box-shadow:0 3px 10px rgba(0,0,0,0.1);">
    <h4>⛔ Weakest Pair: <b>{svc}</b> in <b>{city}</b></h4>
    <p><strong>Avg ROI (3M):</strong> {roi_val:.2f}%</p>
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------
# AI RECOMMENDATIONS (SHORT BULLETS)
# -----------------------------------------------------
st.subheader("🤖 AI Recommendation for Weakest Pair")

with st.spinner("Generating AI insights..."):
    ai_text = generate_ai_insight(
        svc, city, roi_val, trend, mom, yoy, rev_drop, margin_drop
    )

st.markdown(f"""
<div style='padding:16px; background:#fdfdfd; border-radius:14px;
            border-left:6px solid #6c63ff; box-shadow:0 2px 8px rgba(0,0,0,0.05);'>
    <h4>📌 Strategic Insights</h4>
    {ai_text}
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------
# SERVICE LIFECYCLE + MINI FORECAST
# -----------------------------------------------------
st.subheader("🔍 Service Lifecycle Recommendations")

forecast_df = client.query("""
    SELECT service_category, city, ds,
           actual_roi_percent,
           forecasted_roi_percent
    FROM `nonhospitality-bi.analytics.monthly_service_kpis_forecasts`
    ORDER BY service_category, city, ds
""").to_dataframe()

forecast_df['date'] = pd.to_datetime(forecast_df['ds']).dt.date

actual_df = df.copy()
actual_df['date'] = pd.to_datetime(
    actual_df['year'].astype(str) + "-" +
    actual_df['month'].astype(str) + "-01"
).dt.date

latest_actual_date = actual_df['date'].max()

combined = pd.concat([
    actual_df[['service_category', 'city', 'date', 'roi_percent']].rename(columns={'roi_percent': 'roi'}),
    forecast_df[['service_category', 'city', 'date', 'actual_roi_percent']].rename(columns={'actual_roi_percent': 'roi'}),
    forecast_df[['service_category', 'city', 'date', 'forecasted_roi_percent']].rename(columns={'forecasted_roi_percent': 'roi'})
], ignore_index=True)

combined = combined.dropna(subset=['roi']).sort_values(['service_category', 'city', 'date'])


def classify_lifecycle(values):
    if len(values) < 3:
        return "Insufficient Data", "Not enough ROI history."
    t1, t2, t3 = values[-3], values[-2], values[-1]
    if t1 < 0 and t2 < 0 and t3 < 0:
        return "High Risk", "Consistently negative ROI."
    if t3 > t2 > t1:
        return "Growth", "Demand accelerating."
    if t3 < t2 < t1:
        return "Decline", "ROI falling — investigate."
    return "Stable", "Watch for movement."


unique_pairs = combined[['service_category', 'city']].drop_duplicates()

for _, row in unique_pairs.iterrows():
    svc = row['service_category']
    city = row['city']

    sub = combined[(combined['service_category'] == svc) &
                   (combined['city'] == city)].sort_values('date')

    roi_series = sub['roi'].tolist()
    stage, advice = classify_lifecycle(roi_series)

    badge_color = {
        "Growth": "#28a745",
        "Decline": "#dc3545",
        "Stable": "#6c757d",
        "High Risk": "#b30000"
    }.get(stage, "#6c757d")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown(f"""
        <div style='padding:12px; border-radius:12px; background:white;
                    border-left:6px solid {badge_color};
                    margin-bottom:14px;
                    box-shadow:0 2px 6px rgba(0,0,0,0.05);'>
            <strong>{svc} ({city}) →
                <span style="color:{badge_color}">{stage}</span>
            </strong>
            <br>{advice}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        chart_df = sub[['date', 'roi']].copy()
        chart_df['type'] = np.where(
            chart_df['date'] <= latest_actual_date, 'Actual', 'Forecast'
        )

        st.line_chart(chart_df, x='date', y='roi', color='type', height=160)

st.markdown("---")
