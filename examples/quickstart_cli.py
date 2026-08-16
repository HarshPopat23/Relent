"""Example 1: Quickstart Video Processing Pipeline.

Demonstrates how to run the end-to-end Relent AI intelligence pipeline
on a YouTube video or local media file programmatically.
"""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import run_pipeline, format_markdown_report


def main():
    # Replace with any YouTube URL or local file path
    sample_source = "https://youtu.be/11Y3B33oCLE"

    print(f"Ingesting & processing: {sample_source}")
    result = run_pipeline(sample_source, language="english")

    print("\n" + "=" * 60)
    print(f"Title: {result['title']}")
    print(f"Subtitle: {result['subtitle']}")
    print("=" * 60)
    print("\nExecutive Summary:")
    print(result["summary"])

    # Export report to markdown
    output_file = "sample_video_intelligence.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(format_markdown_report(result))

    print(f"\nReport written to: {output_file}")


if __name__ == "__main__":
    main()
