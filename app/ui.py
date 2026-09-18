import os

import streamlit as st
import requests

API_URL = os.getenv("API_URL", "http://localhost:8000/ask")

st.title("Simple RAG Demo")

file = st.file_uploader("Choose a file", type=["pdf"])

if st.button("submit"):
    if file is not None:
        st.success("File uploaded successfully!")
    else:
        st.write("No file uploaded")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question"):
    st.session_state.messages.append({"role":"user", "content":prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    response = requests.post(API_URL, json={"query": prompt})
    answer = response.json().get("answer")
    sources = response.json().get("sources")

    st.session_state.messages.append({"role":"assistant", "content":answer})

    with st.chat_message("assistant"):
        st.markdown(answer)
   
    with st.expander("Sources"):
        for source in sources:
            st.markdown(f"**Score**: {source['score']:.4f}")
            st.markdown(f"**Chunk**: {source['chunk'][:200]}...")
