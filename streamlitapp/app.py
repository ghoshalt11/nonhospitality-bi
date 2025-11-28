import streamlit as st
import pandas as pd
import time
from google.cloud import bigquery
import vertexai
from vertexai.generative_models import GenerativeModel
from google.genai import types
from vertex_utils import get_vertex_client

# ---------------------------
# 1. KPI DELTA COMPUTATION
# ---------------------------

client = bigquery.Client()
# --- PAGE CONFIG ---
st.set_page_config(page_title="Ancillary Insights Suite", layout="wide")

# --- PAGE HEADER ---
st.markdown("""
    <h1 style='text-align:center; font-size:45px; margin-bottom:5px;'>
        🏨 Ancillary Decision Intelligence Hub
    </h1>
    <p style='text-align:center; font-size:18px; color:gray; margin-top:-10px;'>
        A Data-Driven Intelligence for Non-Hospitality Revenue Optimization
    </p>
    <hr style='margin-top:15px;'>
""", unsafe_allow_html=True)


start_time = time.time()
with st.spinner("⏳ Loading Live KPIs..."):
    df_kpis = client.query("""
    SELECT service_category, city, year, month, roi_percent, profit_margin_pct, total_revenue, total_guest_count
    FROM `nonhospitality-bi.analytics.monthly_service_kpis`
""").to_dataframe()

load_time = time.time() - start_time

def compute_kpi_deltas(df):
    df = df.sort_values(["year", "month"])

    roi_now, roi_prev = df.iloc[-1]["roi_percent"], df.iloc[-2]["roi_percent"]
    margin_now, margin_prev = df.iloc[-1]["profit_margin_pct"], df.iloc[-2]["profit_margin_pct"]
    rev_now, rev_prev = df.iloc[-1]["total_revenue"], df.iloc[-2]["total_revenue"]
    guests_now, guests_prev = df.iloc[-1]["total_guest_count"], df.iloc[-2]["total_guest_count"]

    return {
        "roi": (roi_now, roi_now - roi_prev),
        "margin": (margin_now, margin_now - margin_prev),
        "revenue": (rev_now, rev_now - rev_prev),
        "guests": (guests_now, guests_now - guests_prev),
    }



kpis = compute_kpi_deltas(df_kpis)

def arrow(delta):
    return "▲" if delta > 0 else "▼"

def color(delta):
    return "green" if delta > 0 else "red"


# --------------------------------------
# 2. FETCH CATEGORY PERFORMANCE INSIGHTS
# --------------------------------------
# category_df = client.query("""
#     SELECT service_category, AVG(roi_percent) AS avg_roi
#     FROM `nonhospitality-bi.analytics.monthly_service_kpis`
#     GROUP BY service_category
# """).to_dataframe()
category_df = (
    df_kpis.groupby("service_category")["roi_percent"]
    .mean()
    .reset_index()
    .rename(columns={"roi_percent": "avg_roi"})
    .sort_values("avg_roi", ascending=False)
)

top_service = category_df.iloc[0]
worst_service = category_df.iloc[-1]

##---
# City Performance
##
city_df = (
    df_kpis.groupby("city")["roi_percent"]
    .mean()
    .reset_index()
    .rename(columns={"roi_percent": "avg_roi"})
    .sort_values("avg_roi", ascending=False)
)



# top_service = category_df.sort_values("avg_roi", ascending=False).iloc[0]
# worst_service = category_df.sort_values("avg_roi", ascending=True).iloc[0]

icons = {
    "Events": "🎉",
    "Cab/Shuttle": "🚗",
    "F&B": "🍽️",
    "Retail": "🛍️",
    "Gaming": "🎮",
    "Wellness & Spa": "💆",
}


# ---------------------------
# 3. EXECUTIVE SUMMARY (AI)
# ---------------------------
def generate_executive_summary(df_kpis, category_df, city_df, kpis):
    roi_now, roi_delta = kpis["roi"]
    margin_now, margin_delta = kpis["margin"]
    rev_now, rev_delta = kpis["revenue"]
    guests_now, guests_delta = kpis["guests"]

    # Identify top & worst service
    top_service = category_df.iloc[0]
    worst_service = category_df.iloc[-1]

    # Identify top & worst city
    top_city = city_df.iloc[0]
    worst_city = city_df.iloc[-1]

    summary = f"""
### 📊 Executive Business Overview

- **ROI this month:** {roi_now:.2f}% ({'▲' if roi_delta>0 else '▼'} {roi_delta:.2f}%)  
- **Margin:** {margin_now:.2f}% ({'▲' if margin_delta>0 else '▼'} {margin_delta:.2f}%)  
- **Revenue:** ${rev_now/1e6:.2f}M ({'▲' if rev_delta>0 else '▼'} {rev_delta/1e6:.2f}M)  
- **Guests:** {guests_now/1000:.2f}K ({'▲' if guests_delta>0 else '▼'} {guests_delta/1000:.2f}K)  

### 🏆 High-Level Insights
- **Top-performing service:** {top_service['service_category']}  
  → Avg ROI: **{top_service['avg_roi']:.2f}%**

- **Underperforming service:** {worst_service['service_category']}  
  → Avg ROI: **{worst_service['avg_roi']:.2f}%**

### 🌍 City Performance
- **Best city:** {top_city['city']}  
  → Avg ROI: **{top_city['avg_roi']:.2f}%**

- **City needing attention:** {worst_city['city']}  
  → Avg ROI: **{worst_city['avg_roi']:.2f}%**

### 🧭 Overall Summary
ROI is showing a **{'positive' if roi_delta>0 else 'negative'} trend**, driven by strong performance in  
**{top_service['service_category']}** services and thriving markets such as **{top_city['city']}**.  
However, **{worst_service['service_category']}** and weak ROI in **{worst_city['city']}**  
indicate operational challenges that require immediate focus.
"""

    return summary

executive_summary = generate_executive_summary(df_kpis, category_df, city_df, kpis)


# ---------------------------
# 4. UI & MODERN DESIGNS
# ---------------------------
st.markdown("""
<style>

.kpi-card {
    padding: 18px 22px;
    border-radius: 16px;
    background: white;
    border: 1px solid #e3e3e3;
    box-shadow: 0 3px 10px rgba(0,0,0,0.08);
    transition: 0.2s;
}

.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 18px rgba(0,0,0,0.12);
}

.service-card {
    padding: 14px 18px;
    border-radius: 14px;
    background: white;
    border-left: 6px solid #4F8BF9;
    margin-bottom: 10px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}

.badge-good {
    background: #e6f8ef;
    color: #0b8a43;
    padding: 4px 10px;
    border-radius: 8px;
}

.badge-bad {
    background: #fdecea;
    color: #d93025;
    padding: 4px 10px;
    border-radius: 8px;
}

.metric-value {
    font-size: 26px;
    font-weight: 600;
}

.metric-delta {
    font-size: 16px;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------
# 5. EXECUTIVE OVERVIEW
# ---------------------------
# st.subheader("✨ Executive Business Overview")
st.markdown(executive_summary)

st.markdown("---")

# ---------------------------
# 6. KPI CARDS
# ---------------------------
roi_now, roi_delta = kpis["roi"]
margin_now, margin_delta = kpis["margin"]
rev_now, rev_delta = kpis["revenue"]
guests_now, guests_delta = kpis["guests"]

st.subheader("📊 Key KPIs This Month")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class='kpi-card'>
        <strong>📈 ROI</strong>
        <div class='metric-value'>{roi_now:.2f}%</div>
        <div class='metric-delta' style='color:{color(roi_delta)};'>{arrow(roi_delta)} {roi_delta:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class='kpi-card'>
        <strong>💹 Margin</strong>
        <div class='metric-value'>{margin_now:.2f}%</div>
        <div class='metric-delta' style='color:{color(margin_delta)};'>{arrow(margin_delta)} {margin_delta:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class='kpi-card'>
        <strong>💰 Revenue</strong>
        <div class='metric-value'>${rev_now/1e6:.2f}M</div>
        <div class='metric-delta' style='color:{color(rev_delta)};'>{arrow(rev_delta)} {rev_delta/1e6:.2f}M</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class='kpi-card'>
        <strong>👥 Guests</strong>
        <div class='metric-value'>{guests_now/1000:.2f}K</div>
        <div class='metric-delta' style='color:{color(guests_delta)};'>{arrow(guests_delta)} {guests_delta/1000:.2f}K</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")


# ---------------------------
# 7. SERVICE PERFORMANCE
# ---------------------------
st.subheader("🏆 Service Categories Performance Snapshot")

# Top Service
st.markdown(f"""
<div class='service-card'>
    <h4>{icons.get(top_service['service_category'], '⭐')} {top_service['service_category']}
    <span class='badge-good'>Top Performer</span></h4>
    <p>Avg ROI: <strong>{top_service['avg_roi']:.2f}%</strong></p>
</div>
""", unsafe_allow_html=True)

# Worst Service
st.markdown(f"""
<div class='service-card' style='border-left: 6px solid #e84c3c;'>
    <h4>{icons.get(worst_service['service_category'], '⚠️')} {worst_service['service_category']}
    <span class='badge-bad'>Needs Attention</span></h4>
    <p>Avg ROI: <strong>{worst_service['avg_roi']:.2f}%</strong></p>
</div>
""", unsafe_allow_html=True)

# ---------------------------
# 8. CITY PERFORMANCE SNAPSHOT
# ---------------------------
st.subheader("🌍 City Performance Snapshot")

city_icons = {
    "Singapore": "🇸🇬",
    "Tokyo": "🇯🇵",
    "Paris": "🇫🇷",
    "Dubai": "🇦🇪",
    "New York": "🇺🇸",
    "Mumbai": "🇮🇳",
    "London": "🇬🇧",
}

best_city = city_df.iloc[0]
worst_city = city_df.iloc[-1]

# Best City
st.markdown(f"""
<div class='service-card'>
    <h4>{city_icons.get(best_city['city'], '⭐')} {best_city['city']}
    <span class='badge-good'>Top City</span></h4>
    <p>Avg ROI: <strong>{best_city['avg_roi']:.2f}%</strong></p>
</div>
""", unsafe_allow_html=True)

# Worst City
st.markdown(f"""
<div class='service-card' style='border-left: 6px solid #e84c3c;'>
    <h4>{city_icons.get(worst_city['city'], '⚠️')} {worst_city['city']}
    <span class='badge-bad'>Needs Attention</span></h4>
    <p>Avg ROI: <strong>{worst_city['avg_roi']:.2f}%</strong></p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ---------------------------
# 9. TWO MAIN NAVIGATION TILES
# ---------------------------
st.subheader("🧭 What Do You Want To Explore Next?")

t1, t2 = st.columns(2)

with t1:
    st.markdown("""
    <div class='service-card' style='cursor:pointer; border-left: 6px solid #0984e3;'>
        <h3>📊 Detailed Insights & Next-Quarter Predictions</h3>
        <p>Explore ROI trends, service and city performance, charts, 
        recommendations, and upcoming quarter predictions.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Performance Dashboard ➜"):
        st.switch_page("pages/Performance Dashboard.py")

with t2:
    st.markdown("""
    <div class='service-card' style='cursor:pointer; border-left: 6px solid #6c5ce7;'>
        <h3>🧪 Launch / Upgrade New Service</h3>
        <p>Upload market research data and analyze ROI impact of new 
        or upgraded services with predictive intelligence.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to ROI Analyzer ➜"):
        st.switch_page("pages/ROI Analyser.py")

