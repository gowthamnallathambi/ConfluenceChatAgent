from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
import os

load_dotenv()   

def get_qa_chain(vectorstore):
    """
    Creates a Retrieval-Augmented Generation (RAG) QA chain using LangChain with the Groq-hosted LLaMA model.

    Args:
        vectorstore: A vector store (e.g., FAISS, Chroma) containing embedded Confluence documents.
    
    Returns:
        RetrievalQA: A LangChain RetrievalQA pipeline that retrieves relevant documents and answers questions.
    """
    # Define the prompt that guides the LLM's behavior
    prompt_template = PromptTemplate.from_template("""
You are a helpful assistant answering questions from Confluence documentation.

If you don't know the answer or if the question is unrelated to the documents, say:
"I don't know the answer to that. Please ask a question based on the Confluence documents."

Use the following context:
{context}

Question: {question}
Answer (with brief explanation):
""")
    # Initialize the LLM via Groq (using the llama3-8b-8192 model)
    llm = ChatGroq(
        model="llama3-8b-8192",
        temperature=0.2,
        api_key=os.getenv("GROQ_API_KEY"),
    )
    #Convert vectorstore into a retriever for document similarity search
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )
    # Create a RetrievalQA chain that connects the retriever with the LLM
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt_template},
        return_source_documents=True
    )