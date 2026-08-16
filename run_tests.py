"""Relent AI - Standalone Automated Test Runner.

Executes all unit and integration tests with clear pass/fail output.
"""

import os
import sys

# Limit OpenBLAS threads to prevent Windows memory exhaustion
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tests.conftest import (
    get_sample_segments,
    get_sample_transcript,
    get_sample_pipeline_result,
)
from tests.test_audio_processor import (
    test_audio_only_extensions,
    test_download_dir_exists,
    test_ensure_ffmpeg,
    test_convert_to_wav_missing_file,
)
from tests.test_transcriber import (
    test_segments_to_text_concatenation,
    test_segments_to_text_empty,
    test_unload_transcribers,
)
from tests.test_summarizer import (
    test_split_transcript,
    test_summarizer_empty_guards,
)
from tests.test_extractor import (
    test_extractor_empty_guards,
)
from tests.test_script_generator import (
    test_parse_target_seconds,
    test_find_int_list_anywhere,
    test_extract_id_list_ordered,
    test_trim_to_duration,
    test_build_script_text,
    test_format_segments_for_prompt,
)
from tests.test_video_clipper import (
    test_clipper_directories_exist,
    test_get_ffmpeg_path,
    test_build_reel_missing_video,
)
from tests.test_rag_engine import (
    test_format_docs,
    test_ask_question_mock,
)
from tests.test_cli import (
    test_format_markdown_report,
    test_cli_version,
)


def run_all_tests():
    print("=" * 70)
    print("           🎬 Relent AI Automated Test Suite")
    print("=" * 70)

    fixtures_segments = get_sample_segments()
    fixtures_transcript = get_sample_transcript(fixtures_segments)
    fixtures_result = get_sample_pipeline_result(fixtures_segments, fixtures_transcript)

    tests = [
        # Audio Processor
        ("test_audio_only_extensions", lambda: test_audio_only_extensions()),
        ("test_download_dir_exists", lambda: test_download_dir_exists()),
        ("test_ensure_ffmpeg", lambda: test_ensure_ffmpeg()),
        ("test_convert_to_wav_missing_file", lambda: test_convert_to_wav_missing_file()),
        # Transcriber
        ("test_segments_to_text_concatenation", lambda: test_segments_to_text_concatenation(fixtures_segments)),
        ("test_segments_to_text_empty", lambda: test_segments_to_text_empty()),
        ("test_unload_transcribers", lambda: test_unload_transcribers()),
        # Summarizer
        ("test_split_transcript", lambda: test_split_transcript()),
        ("test_summarizer_empty_guards", lambda: test_summarizer_empty_guards()),
        # Extractor
        ("test_extractor_empty_guards", lambda: test_extractor_empty_guards()),
        # Script Generator
        ("test_parse_target_seconds", lambda: test_parse_target_seconds()),
        ("test_find_int_list_anywhere", lambda: test_find_int_list_anywhere()),
        ("test_extract_id_list_ordered", lambda: test_extract_id_list_ordered()),
        ("test_trim_to_duration", lambda: test_trim_to_duration(fixtures_segments)),
        ("test_build_script_text", lambda: test_build_script_text(fixtures_segments)),
        ("test_format_segments_for_prompt", lambda: test_format_segments_for_prompt(fixtures_segments)),
        # Video Clipper
        ("test_clipper_directories_exist", lambda: test_clipper_directories_exist()),
        ("test_get_ffmpeg_path", lambda: test_get_ffmpeg_path()),
        ("test_build_reel_missing_video", lambda: test_build_reel_missing_video()),
        # RAG Engine
        ("test_format_docs", lambda: test_format_docs()),
        ("test_ask_question_mock", lambda: test_ask_question_mock()),
        # CLI
        ("test_format_markdown_report", lambda: test_format_markdown_report(fixtures_result)),
        ("test_cli_version", lambda: test_cli_version()),
    ]

    # Try API Server tests if dependencies are available
    try:
        from tests.test_api_server import (
            test_clean_pdf_text,
            test_api_health,
            test_api_process_missing_source,
            test_api_chat_no_active_video,
            test_api_reel_no_active_video,
            test_api_download_endpoints,
            test_api_serve_media_forbidden_and_not_found,
        )
        from starlette.testclient import TestClient
        from server import app

        client = TestClient(app)
        tests.extend([
            ("test_clean_pdf_text", lambda: test_clean_pdf_text()),
            ("test_api_health", lambda: test_api_health(client)),
            ("test_api_process_missing_source", lambda: test_api_process_missing_source(client)),
            ("test_api_chat_no_active_video", lambda: test_api_chat_no_active_video(client)),
            ("test_api_reel_no_active_video", lambda: test_api_reel_no_active_video(client)),
            ("test_api_download_endpoints", lambda: test_api_download_endpoints(client, fixtures_result)),
            ("test_api_serve_media_forbidden_and_not_found", lambda: test_api_serve_media_forbidden_and_not_found(client)),
        ])
    except ImportError as e:
        print(f"ℹ️ Skipping server endpoint tests (missing optional server package: {e})")

    passed = 0
    failed = 0

    for name, func in tests:
        try:
            func()
            print(f"  ✅ [PASS] {name}")
            passed += 1
        except Exception as e:
            print(f"  ❌ [FAIL] {name}: {e}")
            failed += 1

    print("-" * 70)
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests.")
    print("=" * 70)

    if failed > 0:
        sys.exit(1)
    else:
        print("🎉 All tests passed successfully! [OK]")


if __name__ == "__main__":
    run_all_tests()
