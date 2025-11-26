import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import os

# --- Setup ---
st.set_page_config(page_title="AI Hotel Analytics Chatbot", layout="wide")
st.title("🏨 AI Hotel Chatbot powered by Vertex AI (Gemini 2.5)")

# ✅ Set your API key (or store it in Secret Manager)
os.environ["GOOGLE_CLOUD_API_KEY"] = "YOUR_API_KEY"

# Initialize Gemini client
client = genai.Client(vertexai=True, api_key=os.environ["GOOGLE_CLOUD_API_KEY"])

# --- Streamlit UI ---
user_input = st.text_area("💬 Ask your business question:")
uploaded_file = st.file_uploader("📂 Optional: Upload market or service data (CSV)", type=["csv"])

if st.button("Ask AI"):
    context_text = ""

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        context_text += f"Preview of uploaded data:\n{df.head(5).to_string(index=False)}\n\n"

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=f"""
            You are an AI Business Analyst for a hotel chain.
            Context:
            {context_text}
            Question:
            {user_input}
            Provide insightful, data-aware responses suitable for business executives.
            """)]
        ),
    ]

    config = types.GenerateContentConfig(
        temperature=0.8,
        top_p=0.9,
        max_output_tokens=2048,
        response_modalities=["TEXT"],
    )

    with st.spinner("Analyzing with Gemini..."):
        response_text = ""
        for chunk in client.models.generate_content_stream(
            model="gemini-2.0-flash",
            contents=contents,
            config=config,
        ):
            if hasattr(chunk, "text") and chunk.text:
                response_text += chunk.text

        st.subheader("🤖 AI Insight")
        st.write(response_text)
