#Run on backend FASTAPI server

import streamlit as st
import requests

# Backend URL
API_URL = "http://127.0.0.1:8000/query"

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

st.set_page_config(page_title="Confluence Chat Assistant", layout="centered")
st.title("📘 Confluence Q&A Assistant")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input box
if user_input := st.chat_input("Ask a question from Confluence documnets"):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call FastAPI backend
    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = requests.post(API_URL, json={"question": user_input})
                data = response.json()

                answer = data.get("answer", "No answer found.")
                links = data.get("confluence_links", [])

                # Format answer with sources
                formatted_response = f"{answer}"
                if links:
                    formatted_response += "\n\n---\n**🔗 Related Pages:**\n"
                    for link in links:
                        formatted_response += f"- [View Page]({link})\n"

                st.markdown(formatted_response)
                st.session_state.messages.append({"role": "assistant", "content": formatted_response})
    except Exception as e:
        st.error(f"❌ Error: {e}")

