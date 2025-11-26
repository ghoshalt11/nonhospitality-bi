import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import os

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Revenue Advisor",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS for professional UI ---
st.markdown("""
<style>
body {
    background-color: #F8FAFC;
}
h1, h2, h3 {
    color: #003366;
    font-family: 'Poppins', sans-serif;
}
.stButton>button {
    border-radius: 8px;
    background-color: #003366;
    color: white;
    font-weight: 600;
    padding: 10px 25px;
}
.stButton>button:hover {
    background-color: #004c99;
}
.block-container {
    padding-top: 2rem;
}
.upload-section {
    background-color: #ffffff;
    padding: 1rem 2rem;
    border-radius: 10px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
.output-box {
    background-color: #f4f6f8;
    border-left: 5px solid #004c99;
    padding: 1.5rem;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# --- Vertex AI Gemini Setup ---
os.environ["GOOGLE_CLOUD_API_KEY"] = "AQ.Ab8RN6Ku11MlnrqOjUkD9ouPBe68j6kmWH4l_4YmnVSsiUjU_A"
client = genai.Client(vertexai=True, api_key=os.environ["GOOGLE_CLOUD_API_KEY"])

# --- Main Layout ---
st.markdown("## 🧠 Revenue Advisor")
st.write("Gain insights on service profitability, forecast trends, and optimize business strategies across your hospitality portfolio.")

col1, col2 = st.columns([2, 1])

with col1:
    user_input = st.text_area("💬 Ask your business question:", placeholder="e.g., What is the expected ROI for launching a new spa service next quarter?", height=130)

with col2:
    st.markdown("<div class='upload-section'>📂 <b>Upload Optional Data (CSV)</b></div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["csv"])

if st.button("🚀 Run Analysis"):
    if not user_input:
        st.warning("Please enter a question.")
    else:
        context_text = ""
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            context_text = f"Here is a sample of uploaded data:\n{df.head(5).to_string(index=False)}"

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=f"""
                You are an AI business analyst for a hotel group.
                Context: {context_text}
                Question: {user_input}
                Give a professional business insight in less than 200 words.
                """)]
            ),
        ]

        config = types.GenerateContentConfig(
            temperature=0.7,
            top_p=0.9,
            max_output_tokens=2048,
            response_modalities=["TEXT"]
        )

        with st.spinner("Analyzing business data..."):
            response_text = ""
            for chunk in client.models.generate_content_stream(
                model="gemini-2.0-flash",
                contents=contents,
                config=config,
            ):
                if hasattr(chunk, "text") and chunk.text:
                    response_text += chunk.text

        st.markdown("### 🧾 Insight Summary")
        st.markdown(f"<div class='output-box'>{response_text}</div>", unsafe_allow_html=True)
