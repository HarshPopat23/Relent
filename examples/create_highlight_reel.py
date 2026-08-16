"""Example 3: Create Automated Highlight Reels from Prompts.

Uses verbatim speech segment selection and FFmpeg cutting to create
a highlight video matching exact user-specified durations.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import run_pipeline, run_reel_pipeline


def main():
    source = "https://youtu.be/11Y3B33oCLE"
    print(f"Step 1: Processing video {source}...")
    result = run_pipeline(source, language="english")

    prompt = "Create a 2-minute highlight reel summarizing the product announcement"
    print(f"\nStep 2: Generating reel with prompt: '{prompt}'...")
    reel_result = run_reel_pipeline(result, prompt)

    if reel_result["error"]:
        print(f"Error: {reel_result['error']}")
    else:
        print("\n" + "=" * 60)
        print("🎬 Verbatim Highlight Reel Script:")
        print(reel_result["script"])
        print(f"\n✅ Reel MP4 generated at: {reel_result['reel_path']}")
        print("=" * 60)


if __name__ == "__main__":
    main()
