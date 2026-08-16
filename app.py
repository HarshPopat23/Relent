import os
import sys
import tempfile
from io import BytesIO

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from dotenv import load_dotenv
load_dotenv()

import streamlit as st

from core.rag_engine import ask_question
from main import run_pipeline, run_reel_pipeline

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🎥",
    layout="wide",
)

st.title("AI Video Assistant")
st.write("Summarize any video, chat with it, and cut reels — no meeting required.")

# ----------------------------
# Session State
# ----------------------------
if "result" not in st.session_state:
    st.session_state.result = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "reel_result" not in st.session_state:
    st.session_state.reel_result = None


def clean_pdf_text(text: str) -> str:
    """Make text safe for ReportLab Paragraph rendering (latin-1 safe for Helvetica)."""
    if text is None:
        return ""

    # Replace XML entities
    safe = (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )
    # Ensure characters fit in standard font encoding without crashing
    return safe.encode("latin-1", "replace").decode("latin-1")


def add_pdf_section(elements, styles, heading: str, content: str) -> None:
    elements.append(Paragraph(clean_pdf_text(heading), styles["Heading2"]))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(clean_pdf_text(content), styles["BodyText"]))
    elements.append(Spacer(1, 14))


def build_meeting_pdf(result: dict, chat_history: list[dict]) -> bytes:
    """Create a PDF containing meeting output plus full chat conversation."""
    buffer = BytesIO()

    try:
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("AI Video Assistant Report", styles["Title"]))
        elements.append(Spacer(1, 16))

        add_pdf_section(elements, styles, "Video Title", result.get("title", ""))
        add_pdf_section(elements, styles, "Subtitle", result.get("subtitle", ""))
        add_pdf_section(elements, styles, "Summary", result.get("summary", ""))
        add_pdf_section(elements, styles, "Action Items", result.get("action_items", ""))
        add_pdf_section(elements, styles, "Key Decisions", result.get("key_decisions", ""))
        add_pdf_section(elements, styles, "Open Questions", result.get("open_questions", ""))

        elements.append(PageBreak())
        add_pdf_section(elements, styles, "Full Transcript", result.get("transcript", ""))

        elements.append(PageBreak())
        elements.append(Paragraph("Chat Conversation", styles["Heading2"]))
        elements.append(Spacer(1, 8))

        if chat_history:
            for index, chat in enumerate(chat_history, start=1):
                question = chat.get("question", "")
                answer = chat.get("answer", "")

                elements.append(Paragraph(f"Question {index}", styles["Heading3"]))
                elements.append(Paragraph(clean_pdf_text(question), styles["BodyText"]))
                elements.append(Spacer(1, 6))
                elements.append(Paragraph("Answer", styles["Heading3"]))
                elements.append(Paragraph(clean_pdf_text(answer), styles["BodyText"]))
                elements.append(Spacer(1, 12))
        else:
            elements.append(Paragraph("No chat conversation yet.", styles["BodyText"]))

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
    except Exception as e:
        pdf_bytes = b""
    finally:
        buffer.close()

    return pdf_bytes

# ----------------------------
# Input
# ----------------------------
input_mode = st.radio(
    "Input source",
    ["YouTube URL", "Local file path", "Upload video/audio file"],
    horizontal=True,
)

source = ""
uploaded_file = None

if input_mode == "YouTube URL":
    source = st.text_input(
        "YouTube URL",
        placeholder="https://youtu.be/...",
    )
elif input_mode == "Local file path":
    source = st.text_input(
        "Local audio/video file path",
        placeholder=r"C:\Users\YourName\Videos\meeting.mp4",
    )
else:
    uploaded_file = st.file_uploader(
        "Upload an audio or video file",
        type=["mp3", "wav", "m4a", "aac", "flac", "mp4", "mkv", "mov", "avi", "webm"],
    )

language = st.selectbox(
    "Language",
    ["english", "hinglish"],
)

# ----------------------------
# Run Pipeline
# ----------------------------
if st.button("Generate Video Report", use_container_width=True):
    if input_mode == "Upload video/audio file":
        if uploaded_file is None:
            st.warning("Please upload a valid audio or video file.")
        else:
            suffix = os.path.splitext(uploaded_file.name)[1]

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                source = tmp_file.name

            with st.spinner("Processing video... This may take a few minutes."):
                try:
                    st.session_state.result = run_pipeline(
                        source=source,
                        language=language,
                    )
                    st.session_state.chat_history = []
                    st.session_state.reel_result = None
                    st.success("Video processed successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        if not source.strip():
            st.warning("Please enter a valid YouTube URL or local file path.")
        else:
            with st.spinner("Processing video... This may take a few minutes."):
                try:
                    st.session_state.result = run_pipeline(
                        source=source,
                        language=language,
                    )
                    st.session_state.chat_history = []
                    st.session_state.reel_result = None
                    st.success("Video processed successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")

# ----------------------------
# Display Results
# ----------------------------
if st.session_state.result:
    result = st.session_state.result

    st.header("📌 " + result["title"])
    st.caption(result.get("subtitle", ""))

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Summary",
            "Transcript",
            "Action Items",
            "Key Decisions",
            "Open Questions",
        ]
    )

    with tab1:
        st.markdown(result["summary"])

    with tab2:
        st.text_area(
            "Transcript",
            result["transcript"],
            height=400,
        )

    with tab3:
        st.markdown(result["action_items"])

    with tab4:
        st.markdown(result["key_decisions"])

    with tab5:
        st.markdown(result["open_questions"])

    # ----------------------------
    # Downloads
    # ----------------------------
    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
        "Download Summary",
        result["summary"],
        file_name="video_summary.txt",
        mime="text/plain",
    )

    with col2:
        st.download_button(
        "Download Transcript",
        result["transcript"],
        file_name="transcript.txt",
        mime="text/plain",
    )

    with col3:
        pdf_bytes = build_meeting_pdf(
            result=result,
            chat_history=st.session_state.chat_history,
        )
        if pdf_bytes:
            st.download_button(
                "Download Full PDF",
                data=pdf_bytes,
                file_name="video_report_and_conversation.pdf",
                mime="application/pdf",
            )

    # ----------------------------
    # Reel Generation
    # ----------------------------
    st.divider()
    st.header("🎬 Generate a Reel")
    st.caption(
        "Describe what you want (topic + optional length). The script is built "
        "only from words that actually appear in the video, in the order they "
        "appear — then the matching clips are cut and merged automatically."
    )

    if not result.get("video_path"):
        st.info(
            "No video track was available for this source (it looks like an "
            "audio-only input), so reels can't be generated for it."
        )
    else:
        reel_request = st.text_input(
            "What do you want the reel to be about?",
            placeholder="e.g. I want a script regarding GSoC of 2 minutes",
            key="reel_request",
        )

        if st.button("Generate Reel"):
            if not reel_request.strip():
                st.warning("Please describe what you want the reel to be about.")
            else:
                with st.spinner("Selecting matching moments and cutting the video..."):
                    try:
                        st.session_state.reel_result = run_reel_pipeline(
                            result, reel_request
                        )
                    except Exception as e:
                        st.error(f"Error: {e}")

        if st.session_state.reel_result:
            reel_result = st.session_state.reel_result

            if reel_result["error"]:
                st.warning(reel_result["error"])
            else:
                st.subheader("Script (verbatim from the video, in video order)")
                st.markdown(reel_result["script"])

                st.video(reel_result["reel_path"])

                with open(reel_result["reel_path"], "rb") as f:
                    st.download_button(
                        "Download Reel",
                        data=f.read(),
                        file_name="reel.mp4",
                        mime="video/mp4",
                    )

    # ----------------------------
    # Chat
    # ----------------------------
    st.divider()
    st.header("💬 Chat with the video")

    question = st.text_input(
        "Ask a question about the video...",
        key="question",
    )

    if st.button("Ask"):
        if question.strip():
            answer = ask_question(
                result["rag_chain"],
                question,
            )

            st.session_state.chat_history.append(
                {
                    "question": question,
                    "answer": answer,
                }
            )

    if st.session_state.chat_history:
        st.subheader("Conversation")

        for chat in st.session_state.chat_history:
            st.markdown(f"**🧑 You:** {chat['question']}")
            st.markdown(f"**🤖 Assistant:** {chat['answer']}")
            st.divider()