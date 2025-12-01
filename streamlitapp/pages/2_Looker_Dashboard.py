import streamlit as st

st.set_page_config(page_title="Dashboard", layout="wide")

st.title("📊 Detail Analytics Dashboard")

st.markdown("""
Use this embedded dashboard to explore your key performance metrics,key actionable insights, recommendations etc.
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
