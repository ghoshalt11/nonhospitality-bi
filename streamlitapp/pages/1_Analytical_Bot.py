import streamlit as st
from nlp_engine import answer_user_query

st.title("📊 Analytical Chatbot - AMA")

query = st.text_input("Ask your business question:")

if st.button("Ask"):

    if not query.strip():
        st.warning("Enter a question.")
        st.stop()

    with st.spinner("🔎 Analyzing using Gemini + BigQuery..."):
        result = answer_user_query(query)

    if result["error"]:
        st.error(result["error"])
        st.stop()

    st.subheader("📜 Generated SQL")
    st.code(result["sql"], language="sql")

    if result["dataframe"] is not None:
        st.dataframe(result["dataframe"])

    st.subheader("🧠 AI Summary")
    st.write(result["summary"])
