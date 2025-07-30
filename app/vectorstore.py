from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import os

def build_vectorstore_from_docs(docs, metadata_list):
    """
    Builds a FAISS vector store from a list of text documents and their metadata.

    Args:
        docs (List[str]): Raw text documents to embed and index.
        metadata_list (List[dict]): Metadata corresponding to each document (same order as `docs`).

    Returns:
        FAISS: A vector store containing embedded chunks for similarity search.
    """

    # Split large documents into smaller overlapping chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100)
    documents = []
    for text, meta in zip(docs, metadata_list):
        # Split each document into chunks and associate with metadata
        for chunk in splitter.split_text(text):
            documents.append(Document(page_content=chunk, metadata=meta))
    # Initialize sentence embedding model (MPNet)
    embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    return FAISS.from_documents(documents, embedder)

def save_vectorstore(vectorstore):
    """
    Saves the FAISS vector store to the local file system.

    Args:
        vectorstore (FAISS): The FAISS vector store instance to save.
    """
    vectorstore.save_local("faiss_index")

def load_vectorstore():
    """
    Loads the FAISS vector store from local disk with the same embedding model.

    Returns:
        FAISS: Loaded FAISS vector store, ready for similarity search.
    """
    embedder = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )
    # allow_dangerous_deserialization is required if metadata includes arbitrary Python objects
    return FAISS.load_local("faiss_index", embedder,allow_dangerous_deserialization=True)