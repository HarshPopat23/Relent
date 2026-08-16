"""Relent AI - Semantic RAG Engine.

Provides vector retrieval and grounded conversational intelligence
over meeting and video transcripts using Chroma and Ollama.
"""

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


OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:3b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def get_llm():
    from langchain_ollama import ChatOllama
    return ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.3, num_gpu=0)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


SYSTEM_RAG_PROMPT = """You are a transcript-only video assistant.

Your job is to answer the user's request using ONLY the meeting/video transcript context below.
Do not use outside knowledge.
Do not add facts, examples, definitions, or explanations that are not present in the transcript.

Most important rule:
- Preserve the same sequence in which the information appears in the transcript/video.
- Do not reorder points by importance.
- Do not combine unrelated parts unless the transcript connects them.

If the user asks for a script:
- Return only the script text.
- Do not write a title.
- Do not write "Here is the script".
- Do not write "Based on the transcript".
- Do not add bullet points unless the user asks for bullet points.
- Write in a natural spoken style.
- Keep the script in the same order as the transcript/video.

Length guidance for script requests:
- 1 minute script: about 130 to 160 words.
- 2 minute script: about 260 to 320 words.
- 3 minute script: about 390 to 480 words.

If the user asks about a topic, include only transcript parts related to that topic.
For example, if the user asks for a GSoC script, use only the GSoC-related transcript content and keep it in video order.

If the requested topic or answer is not found in the transcript context, say exactly:
I could not find this information in the meeting transcript.

Transcript context in video order:
{context}"""


def build_rag_chain(transcript: str):
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnableLambda, RunnablePassthrough
    from core.vector_store import build_vector_store, get_retriever

    vector_store = build_vector_store(transcript=transcript)
    retriever = get_retriever(vector_store, k=4)
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_RAG_PROMPT),
            ("human", "{question}"),
        ]
    )

    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def load_rag_chain():
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnableLambda, RunnablePassthrough
    from core.vector_store import get_retriever, load_vector_store

    vector_store = load_vector_store()
    retriever = get_retriever(vector_store)
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_RAG_PROMPT),
            ("human", "{question}"),
        ]
    )

    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def ask_question(rag_chain, question: str) -> str:
    safe_print(f"Question : {question}")
    answer = rag_chain.invoke(question)
    safe_print(f"answer :{answer}")
    return answer