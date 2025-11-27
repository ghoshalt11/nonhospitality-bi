import streamlit as st




# Gradient background CSS
gradient_css = """
<style>
    body {
        background: linear-gradient(to bottom right, white, black);
        color: white;
    }

    /* Streamlit main block */
    .stApp {
        background: linear-gradient(to bottom right, white, black) !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #ffffff, #000000) !important;
    }
</style>
"""

# st.markdown(gradient_css, unsafe_allow_html=True)
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(135deg, #dbeafe 0%, #ffffff 60%);
            background-attachment: fixed;
        }
    </style>
    """,
    unsafe_allow_html=True
)


#"🏨"


st.set_page_config(page_title="AI Hotel Business Suite",  layout="wide")


st.title("🏨 Hotel Ancillary Suite")
st.markdown("""
Welcome to your **Hotel Intelligence Hub**, powered by **Vertex AI (Gemini 2.5)**.


Use the sidebar to switch between:
- **📊 ROI Analyzer** — Upload new market data, costs, and forecast ROI
- **💬 AI Chat Assistant** — Ask conversational business questions
""")
# --- Embed Looker Dashboard directly here ---
st.markdown("---")
st.subheader("📈 Quick Business Performance Overview")

looker_url = "https://lookerstudio.google.com/embed/reporting/f222b53e-1d1d-480a-b800-1adf25c5c407/page/y54fF"

st.markdown(
    f"""
    <iframe src="{looker_url}"
            width="100%"
            height="900"
            style="border:none; border-radius:10px;"
            allowfullscreen
            sandbox="allow-storage-access-by-user-activation allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox">
    </iframe>
    """,
    unsafe_allow_html=True,
)