"""Example 2: Generate Structured Meeting Notes.

Extracts action items (task, owner, deadline), decisions,
and executive summary from an audio or video recording.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import run_pipeline


def main():
    recording_path = os.getenv("MEETING_RECORDING", "downloads/sample_meeting.mp4")

    if not os.path.exists(recording_path):
        print(f"File {recording_path} not found. Please provide a path to a meeting recording.")
        return

    print(f"Analyzing meeting recording: {recording_path}")
    result = run_pipeline(recording_path, language="english")

    print("\n" + "=" * 60)
    print("📋 ACTION ITEMS:")
    print(result["action_items"])
    print("\n🔑 KEY DECISIONS:")
    print(result["key_decisions"])
    print("\n❓ OPEN QUESTIONS:")
    print(result["open_questions"])
    print("=" * 60)


if __name__ == "__main__":
    main()
