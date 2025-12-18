#!/usr/bin/env python3
"""
YouTube Transcript Downloader
Downloads and formats YouTube video transcripts for NotebookLM.
"""

import argparse
import os
import re
import sys

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled
except ImportError:
    print("Required package not found. Install with:")
    print("  pip install youtube-transcript-api")
    sys.exit(1)


def extract_video_id(url_or_id: str) -> str:
    """
    Extract YouTube video ID from URL or validate video ID.

    Args:
        url_or_id: YouTube URL or video ID

    Returns:
        11-character video ID

    Raises:
        ValueError: If video ID cannot be extracted
    """
    patterns = [
        r"(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})",
        r"^([a-zA-Z0-9_-]{11})$",
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from: {url_or_id}")


def format_timestamp(seconds: float) -> str:
    """
    Format seconds into HH:MM:SS or MM:SS timestamp.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted timestamp string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def get_transcript(
    video_id: str, languages: list = None, include_timestamps: bool = False
) -> str:
    """
    Fetch and format transcript for a YouTube video.

    Args:
        video_id: YouTube video ID
        languages: List of preferred language codes (e.g., ['en', 'es'])
        include_timestamps: Whether to include timestamps in output

    Returns:
        Formatted transcript text

    Raises:
        TranscriptsDisabled: If transcripts are disabled for the video
        NoTranscriptFound: If no transcript is available
    """
    # Fetch transcript
    if languages:
        transcript_data = YouTubeTranscriptApi.get_transcript(
            video_id, languages=languages
        )
    else:
        # Try English first, then fall back to any available language
        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(
                video_id, languages=["en"]
            )
        except NoTranscriptFound:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)

    # Format transcript
    if include_timestamps:
        lines = []
        for entry in transcript_data:
            timestamp = format_timestamp(entry["start"])
            text = entry["text"].replace("\n", " ")
            lines.append(f"[{timestamp}] {text}")
        return "\n".join(lines)
    else:
        # Format as paragraphs for better readability
        texts = [entry["text"].replace("\n", " ") for entry in transcript_data]
        paragraphs = []
        current_paragraph = []

        for text in texts:
            current_paragraph.append(text)
            combined = " ".join(current_paragraph)

            # Start new paragraph if:
            # 1. Current paragraph is long (>100 words), OR
            # 2. Sentence ends with punctuation and has at least 3 segments
            if len(combined.split()) > 100 or (
                text.rstrip().endswith((".", "?", "!")) and len(current_paragraph) > 3
            ):
                paragraphs.append(combined)
                current_paragraph = []

        # Add remaining text
        if current_paragraph:
            paragraphs.append(" ".join(current_paragraph))

        return "\n\n".join(paragraphs)


def list_available_languages(video_id: str) -> None:
    """
    List all available transcript languages for a video.

    Args:
        video_id: YouTube video ID
    """
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    print(f"\nAvailable transcripts for video {video_id}:")
    print("-" * 50)

    # List manually created transcripts
    manual_transcripts = []
    auto_transcripts = []

    for transcript in transcript_list:
        info = f"  {transcript.language_code:5s} - {transcript.language}"
        if transcript.is_generated:
            auto_transcripts.append(info)
        else:
            manual_transcripts.append(info)

    if manual_transcripts:
        print("Manual transcripts:")
        for t in manual_transcripts:
            print(t)

    if auto_transcripts:
        print("\nAuto-generated transcripts:")
        for t in auto_transcripts:
            print(t)


def generate_filename(video_id: str, extension: str = "txt") -> str:
    """
    Generate a filename for the transcript.

    Args:
        video_id: YouTube video ID
        extension: File extension (default: txt)

    Returns:
        Generated filename
    """
    return f"transcript_{video_id}.{extension}"


def save_transcript(
    video_id: str,
    transcript: str,
    output_path: str = None,
    output_dir: str = "notebooklm_sources_yt",
) -> str:
    """
    Save transcript to file.

    Args:
        video_id: YouTube video ID
        transcript: Formatted transcript text
        output_path: Specific output file path
        output_dir: Output directory (used if output_path not specified)

    Returns:
        Path to saved file
    """
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    output = f"""# YouTube Video Transcript

**Video URL:** {video_url}
**Video ID:** {video_id}

---

{transcript}
"""

    if output_path:
        filepath = output_path
    else:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        filename = generate_filename(video_id)
        filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(output)

    return filepath


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Download YouTube transcripts for NotebookLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "https://youtube.com/watch?v=VIDEO_ID"
  %(prog)s VIDEO_ID -o transcript.txt
  %(prog)s VIDEO_ID --timestamps
  %(prog)s VIDEO_ID --language es
  %(prog)s VIDEO_ID --list-languages
  %(prog)s -f video_ids.txt
        """,
    )

    parser.add_argument("video", nargs="?", help="YouTube URL or video ID")

    parser.add_argument(
        "-o",
        "--output",
        help="Output file (default: auto-generated in output directory)",
    )

    parser.add_argument(
        "-d",
        "--output-dir",
        default="notebooklm_sources_yt",
        help="Output directory for auto-named files (default: notebooklm_sources_yt)",
    )

    parser.add_argument(
        "--timestamps", action="store_true", help="Include timestamps in output"
    )

    parser.add_argument(
        "--language", "-l", help="Preferred language code (e.g., en, es, fr)"
    )

    parser.add_argument(
        "--list-languages",
        action="store_true",
        help="List available transcript languages",
    )

    parser.add_argument(
        "-f", "--file", help="Read video IDs/URLs from file (one per line)"
    )

    args = parser.parse_args()

    # Collect video IDs
    video_inputs = []

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                video_inputs = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
        except IOError as e:
            print(f"Error reading file '{args.file}': {e}", file=sys.stderr)
            sys.exit(1)
    elif args.video:
        video_inputs = [args.video]
    else:
        parser.print_help()
        print(
            "\nError: No video provided. Use a video URL/ID or specify a file with -f",
            file=sys.stderr,
        )
        sys.exit(1)

    # Process videos
    success_count = 0
    languages = [args.language] if args.language else None

    for i, video_input in enumerate(video_inputs, 1):
        try:
            video_id = extract_video_id(video_input)

            if args.list_languages:
                list_available_languages(video_id)
                continue

            print(f"\n[{i}/{len(video_inputs)}] Processing: {video_id}")

            transcript = get_transcript(video_id, languages, args.timestamps)

            # For batch processing, ignore -o flag and auto-generate filenames
            output_path = args.output if len(video_inputs) == 1 else None

            if output_path or not args.output:
                filepath = save_transcript(
                    video_id, transcript, output_path, args.output_dir
                )
                print(f"  ✓ Saved to: {filepath}")
                success_count += 1
            else:
                # Print to stdout
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                print("\n# YouTube Video Transcript\n")
                print(f"**Video URL:** {video_url}")
                print(f"**Video ID:** {video_id}\n")
                print("---\n")
                print(transcript)

        except TranscriptsDisabled:
            print(
                f"  ✗ Error: Transcripts are disabled for {video_input}",
                file=sys.stderr,
            )
        except NoTranscriptFound:
            print(f"  ✗ Error: No transcript found for {video_input}", file=sys.stderr)
        except ValueError as e:
            print(f"  ✗ {e}", file=sys.stderr)
        except Exception as e:
            print(f"  ✗ Unexpected error with {video_input}: {e}", file=sys.stderr)

    if len(video_inputs) > 1:
        print(f"\n{'='*60}")
        print(f"Completed: {success_count}/{len(video_inputs)} transcripts saved")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
