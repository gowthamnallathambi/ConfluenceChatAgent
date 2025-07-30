
import streamlit as st
from app.vectorstore import load_vectorstore
from app.llm import get_qa_chain

st.set_page_config(page_title="Confluence RAG", layout="centered")
st.title("📘 Confluence Q&A Assistant")

# 🔄 Load vectorstore and chain
@st.cache_resource
def generate_vectorstore():
    """
    Loads the vector store containing Confluence documents and 
    initializes the QA chain using an LLM. Caches the result for efficiency.
    
    Returns:
        chain (Runnable): The initialized QA chain ready to handle user queries.
    """
    vs = load_vectorstore()
    chain = get_qa_chain(vs)
    return chain

qa_chain = generate_vectorstore()

# 💬 Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# 📜 Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 📝 Chat input
if user_input := st.chat_input("Ask a question from Confluence documents"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = qa_chain.invoke({"query": user_input})
                answer = result["result"]
                source_docs = result.get("source_documents", [])

                # 🧠 Fallback if answer isn't confident or sources are missing
                # 🔎 If no relevant documents returned
                if not source_docs or not answer.strip() or any(
                    phrase in answer.lower() for phrase in [
                        "no relevant", 
                        "i don't know", 
                        "does not mention", 
                        "no information", 
                        "cannot find", 
                        "not found"
                    ]
                ):
                    fallback_response = (
                        " *No relevant Confluence document found.*\n\n"
                        "Please ask a question based on the Confluence documentation."
                    )
                    st.markdown(fallback_response)
                    st.session_state.messages.append({"role": "assistant", "content": fallback_response})
                else:
                    formatted_response = f"{answer}\n\n---\n** Sources:**\n"
                    for doc in source_docs:
                        link = doc.metadata.get("link", "#")
                        source = doc.metadata.get("source", "Document")
                        formatted_response += f"- [{source}]({link})\n"

                    st.markdown(formatted_response)
                    st.session_state.messages.append({"role": "assistant", "content": formatted_response})
                
            except Exception as e:
                error_msg = f"Error: {e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})