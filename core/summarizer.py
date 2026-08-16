"""Relent AI - Hierarchical Map-Reduce Video Summarizer.

Generates structured executive summaries, video titles, and subtitles
from transcript text using local LLMs.
"""

import os

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b-instruct")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def get_llm():
    from langchain_ollama import ChatOllama

    kwargs = {
        "model": OLLAMA_MODEL,
        "base_url": OLLAMA_BASE_URL,
        "temperature": 0.3,
    }
    num_gpu = os.getenv("OLLAMA_NUM_GPU")
    if num_gpu is not None and num_gpu != "":
        try:
            kwargs["num_gpu"] = int(num_gpu)
        except ValueError:
            pass

    return ChatOllama(**kwargs)


def split_transcript(transcript: str) -> list[str]:
    """Split long transcript into manageable chunks for map-reduce summarization."""
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,
            chunk_overlap=200,
        )
        return splitter.split_text(transcript)
    except ImportError:
        # Fallback simple split if langchain_text_splitters is not installed
        chunk_size = 3000
        return [
            transcript[i : i + chunk_size] for i in range(0, len(transcript), chunk_size - 200)
        ] or [""]


def summarize(transcript: str) -> str:
    """Generate a structured hierarchical executive summary using Map-Reduce."""
    if not transcript or not transcript.strip():
        return "No transcript content available to summarize."

    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate

    llm = get_llm()

    map_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert video summarizer. Summarize the following section of the video into concise bullet points while preserving important decisions, action items, and discussions.",
            ),
            ("human", "{text}"),
        ]
    )

    map_chain = map_prompt | llm | StrOutputParser()

    chunks = split_transcript(transcript)

    chunk_summaries = [map_chain.invoke({"text": chunk}) for chunk in chunks]

    combined_summary = "\n\n".join(chunk_summaries)

    reduce_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert video summarizer. This video is NOT necessarily a meeting —
it could be a tutorial, a case study, a review, a talk, a vlog, a news breakdown, or anything else.

Combine the following partial summaries into one final summary of the video.

Rules:
- Start with a short "Overview" section (2-4 sentences) describing what the video is about.
- Then choose 2-4 section headings that actually fit THIS video's content — do not force
  generic meeting headers like "Decisions Made" or "Action Items" onto content that isn't
  a meeting. For example: a tutorial might use "Steps Covered" / "Tools Used"; a case study
  might use "Key Points" / "Data & Examples"; a review might use "Pros" / "Cons" / "Verdict";
  a talk might use "Main Arguments" / "Examples Given". Pick whatever headings genuinely
  match what's actually in the video.
- End with a "Key Takeaways" section (bullet points).
- Keep it clear, concise, and well-structured. Do not invent headings with no real content
  behind them — only include a section if the video actually covers that kind of content.
""",
            ),
            ("human", "{text}"),
        ]
    )

    reduce_chain = reduce_prompt | llm | StrOutputParser()

    return reduce_chain.invoke({"text": combined_summary})


def generate_title(transcript: str) -> str:
    """Generate a concise title from the transcript."""
    if not transcript or not transcript.strip():
        return "Untitled Video"

    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate

    llm = get_llm()

    title_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Based on the video transcript, generate a short, catchy title that "
                "reflects what the video is actually about. "
                "The title should be at most 8 words. Return only the title and nothing else.",
            ),
            ("human", "{text}"),
        ]
    )

    title_chain = title_prompt | llm | StrOutputParser()

    title = title_chain.invoke({"text": transcript[:2000]})
    return title.strip().strip('"').strip("'")


def generate_subtitle(transcript: str) -> str:
    """A one-line subtitle describing the video generated from content."""
    if not transcript or not transcript.strip():
        return "No description available"

    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate

    llm = get_llm()

    subtitle_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Based on the video transcript, write ONE short subtitle line (max 20 words) "
                "that describes what this specific video covers. Do not repeat the title "
                "verbatim — add context (e.g. what topic, what angle, what the viewer will learn). "
                "Return only the subtitle line and nothing else.",
            ),
            ("human", "{text}"),
        ]
    )

    subtitle_chain = subtitle_prompt | llm | StrOutputParser()

    subtitle = subtitle_chain.invoke({"text": transcript[:2000]})
    return subtitle.strip().strip('"').strip("'")
