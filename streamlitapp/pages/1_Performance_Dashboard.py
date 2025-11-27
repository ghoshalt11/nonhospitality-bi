import streamlit as st

st.set_page_config(page_title="Hotel Analytics Dashboard", layout="wide")

st.title("📊 Quick Analytics Dashboard (Looker Studio)")

st.markdown("""
Use this embedded dashboard to explore your key performance metrics,
while the AI Chatbot helps you interpret results or simulate scenarios.
""")


looker_url="https://lookerstudio.google.com/embed/reporting/6ac5449e-032f-4ed7-90d2-0e67050bec89/page/Y83gF"

st.markdown(
    f"""
    <iframe src="{looker_url}" 
            width="100%" 
            height="900" 
            style="border:none;"
            allowfullscreen></iframe>
    """,
    unsafe_allow_html=True,
)
