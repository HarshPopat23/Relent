"""Relent AI Core Package.

Provides neural video intelligence, multi-engine transcription,
hierarchical summarization, semantic RAG search, and automated highlight reel creation.
"""

__version__ = "0.1.0"
__author__ = "Relent AI Community"
__license__ = "MIT"

from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import ask_question, build_rag_chain, load_rag_chain
from core.script_generator import build_script_text, select_segments_for_request
from core.summarizer import generate_subtitle, generate_title, summarize
from core.transcriber import segments_to_text, transcribe_all
from core.vector_store import build_vector_store, get_retriever, load_vector_store
from core.video_clipper import build_reel

__all__ = [
    "__version__",
    "extract_action_items",
    "extract_key_decisions",
    "extract_questions",
    "ask_question",
    "build_rag_chain",
    "load_rag_chain",
    "build_script_text",
    "select_segments_for_request",
    "generate_subtitle",
    "generate_title",
    "summarize",
    "segments_to_text",
    "transcribe_all",
    "build_vector_store",
    "get_retriever",
    "load_vector_store",
    "build_reel",
]
