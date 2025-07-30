from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from app.vectorstore import load_vectorstore
from app.llm import get_qa_chain

#Initialize FastAPI app and router
app = FastAPI()
router = APIRouter()

#Load vectorstore and initialize the QA chain
vectorstore = load_vectorstore()
qa_chain = get_qa_chain(vectorstore)

class QueryRequest(BaseModel):
    """
    Schema for the incoming POST request to the /query endpoint.
    
    Attributes:
        question (str): The user question to query the Confluence documentation.
    """
    question: str

@router.get("/")
def root():
    """
    Health check endpoint.

    Returns:
        dict: A simple confirmation message that the API is running.
    """
    return {"message": "Confluence Chat Assitant API is running."}

@router.post("/query")
def query_confluence(request: QueryRequest):
    """
    Endpoint to query the Confluence-based RAG system.

    Args:
        request (QueryRequest): Request object containing the user question.

    Returns:
        dict: A dictionary with the model's answer and a list of source document links.
    """
    try:
        # Query the QA chain with the user question
        result = qa_chain.invoke({"query": request.question})
        answer = result["result"]
        source_docs = result.get("source_documents", [])

        # Extract unique Confluence links from the source documents
        confluence_links = list({
            doc.metadata.get("link")
            for doc in source_docs
            if doc.metadata.get("link")
        })

        return {
            "answer": answer,
            "confluence_links": confluence_links
        }
    except Exception as e:
        # Handle errors and return diagnostics
        print("Error during query processing:", e)
        return {"error": "Internal server error", "details": str(e)}

#Include the router in the FastAPI application
app.include_router(router)