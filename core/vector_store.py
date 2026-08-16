import os
import sys

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def safe_print(text: str = "") -> None:
    try:
        print(text)
    except Exception:
        try:
            encoding = sys.stdout.encoding or "utf-8"
            print(str(text).encode(encoding, errors="replace").decode(encoding, errors="replace"))
        except Exception:
            pass


from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHROMA_DIR = "vector_db"
COLLECTION_NAME = "meeting_transcript"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

os.makedirs(CHROMA_DIR, exist_ok=True)


def get_embeddings():
    """Load the embedding model."""
    try:
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        device = "cpu"

    from langchain_huggingface import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": device},
        encode_kwargs={"normalize_embeddings": True},
    )


def build_vector_store(transcript: str) -> Chroma:
    """Create and persist a Chroma vector store from a transcript."""

    safe_print("Building vector store...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )

    chunks = splitter.split_text(transcript) if transcript.strip() else ["No transcript available."]

    documents = [
        Document(
            page_content=chunk,
            metadata={"chunk_index": i},
        )
        for i, chunk in enumerate(chunks)
    ]

    embeddings = get_embeddings()

    # Reset existing collection if it exists to ensure fresh context for the new video
    try:
        existing = Chroma(
            collection_name=COLLECTION_NAME,
            persist_directory=CHROMA_DIR,
            embedding_function=embeddings,
        )
        existing.delete_collection()
    except Exception:
        pass

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DIR,
    )

    safe_print(f"Vector store created with {len(documents)} chunks.")

    return vector_store


def load_vector_store() -> Chroma:
    """Load an existing Chroma vector store."""

    embeddings = get_embeddings()

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
    )

    return vector_store


def get_retriever(
    vector_store: Chroma,
    k: int = 4,
) -> BaseRetriever:
    """Return a retriever for similarity search."""

    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )