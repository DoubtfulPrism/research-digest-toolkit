#!/usr/bin/env python3
"""Split large text files into smaller chunks.

Designed for preparing large documents for NotebookLM (400k char limit).
"""

import argparse
import os
import sys
from pathlib import Path

# Default settings
DEFAULT_MAX_CHARS = 400000  # NotebookLM limit
DEFAULT_INPUT_DIR = "files_to_split"
DEFAULT_OUTPUT_DIR = "notebooklm_sources_split"

# Supported text-based file extensions
SUPPORTED_EXTENSIONS = {
    ".txt",
    ".md",
    ".csv",
    ".log",
    ".json",
    ".xml",
    ".html",
    ".py",
    ".js",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".sh",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".conf",
    ".rst",
    ".tex",
}


def is_text_file(filepath: str, check_extensions: bool = True) -> bool:
    """Check if file is a supported text file.

    Args:
        filepath: Path to file
        check_extensions: Whether to check file extension

    Returns:
        True if file should be processed
    """
    if check_extensions:
        ext = Path(filepath).suffix.lower()
        return ext in SUPPORTED_EXTENSIONS
    return True


def split_file_by_words(
    input_path: str,
    output_dir: str,
    max_chars: int = DEFAULT_MAX_CHARS,
    verbose: bool = True,
) -> int:
    """Split a file into chunks by word boundaries.

    Args:
        input_path: Path to input file
        output_dir: Directory for output chunks
        max_chars: Maximum characters per chunk
        verbose: Whether to print progress

    Returns:
        Number of chunks created (0 if failed)
    """
    filename = os.path.basename(input_path)
    base_name, ext = os.path.splitext(filename)

    try:
        # Read file
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.strip():
            if verbose:
                print(f"  ⚠ Skipping empty file: {filename}")
            return 0

        # Split by words
        words = content.split()
        current_chunk = []
        current_char_count = 0
        file_count = 1
        chunks_created = 0

        for word in words:
            word_len = len(word)

            # Check if adding this word would exceed limit
            if current_chunk and (current_char_count + word_len + 1 > max_chars):
                # Write current chunk
                chunk_content = " ".join(current_chunk)
                output_filename = f"{base_name}_part{file_count:03d}{ext}"
                output_path = os.path.join(output_dir, output_filename)

                with open(output_path, "w", encoding="utf-8") as out_f:
                    out_f.write(chunk_content)

                chunks_created += 1
                current_chunk = [word]
                current_char_count = word_len
                file_count += 1
            else:
                current_chunk.append(word)
                current_char_count += word_len + (1 if current_chunk else 0)

        # Write remaining chunk
        if current_chunk:
            chunk_content = " ".join(current_chunk)
            output_filename = f"{base_name}_part{file_count:03d}{ext}"
            output_path = os.path.join(output_dir, output_filename)

            with open(output_path, "w", encoding="utf-8") as out_f:
                out_f.write(chunk_content)

            chunks_created += 1

        # Report results
        if chunks_created == 1:
            if verbose:
                print(f"  → {filename}: No split needed ({len(content):,} chars)")
        else:
            if verbose:
                print(
                    f"  ✓ {filename}: Split into {chunks_created} parts ({len(content):,} chars)"
                )

        return chunks_created

    except UnicodeDecodeError:
        print(
            f"  ✗ Error: {filename} is not a valid text file (encoding issue)",
            file=sys.stderr,
        )
        return 0
    except IOError as e:
        print(f"  ✗ Error reading {filename}: {e}", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"  ✗ Unexpected error with {filename}: {e}", file=sys.stderr)
        return 0


def split_file_by_lines(
    input_path: str,
    output_dir: str,
    max_chars: int = DEFAULT_MAX_CHARS,
    verbose: bool = True,
) -> int:
    """Split a file into chunks by line boundaries (preserves line structure).

    Args:
        input_path: Path to input file
        output_dir: Directory for output chunks
        max_chars: Maximum characters per chunk
        verbose: Whether to print progress

    Returns:
        Number of chunks created (0 if failed)
    """
    filename = os.path.basename(input_path)
    base_name, ext = os.path.splitext(filename)

    try:
        # Read file
        with open(input_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            if verbose:
                print(f"  ⚠ Skipping empty file: {filename}")
            return 0

        current_chunk = []
        current_char_count = 0
        file_count = 1
        chunks_created = 0
        total_chars = sum(len(line) for line in lines)

        for line in lines:
            line_len = len(line)

            # Check if adding this line would exceed limit
            if current_chunk and (current_char_count + line_len > max_chars):
                # Write current chunk
                chunk_content = "".join(current_chunk)
                output_filename = f"{base_name}_part{file_count:03d}{ext}"
                output_path = os.path.join(output_dir, output_filename)

                with open(output_path, "w", encoding="utf-8") as out_f:
                    out_f.write(chunk_content)

                chunks_created += 1
                current_chunk = [line]
                current_char_count = line_len
                file_count += 1
            else:
                current_chunk.append(line)
                current_char_count += line_len

        # Write remaining chunk
        if current_chunk:
            chunk_content = "".join(current_chunk)
            output_filename = f"{base_name}_part{file_count:03d}{ext}"
            output_path = os.path.join(output_dir, output_filename)

            with open(output_path, "w", encoding="utf-8") as out_f:
                out_f.write(chunk_content)

            chunks_created += 1

        # Report results
        if chunks_created == 1:
            if verbose:
                print(f"  → {filename}: No split needed ({total_chars:,} chars)")
        else:
            if verbose:
                print(
                    f"  ✓ {filename}: Split into {chunks_created} parts ({total_chars:,} chars)"
                )

        return chunks_created

    except UnicodeDecodeError:
        print(
            f"  ✗ Error: {filename} is not a valid text file (encoding issue)",
            file=sys.stderr,
        )
        return 0
    except IOError as e:
        print(f"  ✗ Error reading {filename}: {e}", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"  ✗ Unexpected error with {filename}: {e}", file=sys.stderr)
        return 0


def process_files(
    input_paths: list,
    output_dir: str,
    max_chars: int = DEFAULT_MAX_CHARS,
    split_by: str = "words",
    check_extensions: bool = True,
    verbose: bool = True,
) -> dict:
    """Process multiple files and split them.

    Args:
        input_paths: List of file paths to process
        output_dir: Output directory
        max_chars: Maximum characters per chunk
        split_by: 'words' or 'lines'
        check_extensions: Whether to filter by file extension
        verbose: Whether to print progress

    Returns:
        Dictionary with processing statistics
    """
    # Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        if verbose:
            print(f"Created output directory: {output_dir}\n")

    split_func = split_file_by_lines if split_by == "lines" else split_file_by_words

    stats = {
        "total_files": 0,
        "processed": 0,
        "skipped": 0,
        "failed": 0,
        "chunks_created": 0,
    }

    for input_path in input_paths:
        stats["total_files"] += 1

        # Check if file should be processed
        if not os.path.isfile(input_path):
            if verbose:
                print(f"  ⚠ Skipping non-file: {input_path}")
            stats["skipped"] += 1
            continue

        if check_extensions and not is_text_file(input_path):
            if verbose:
                print(
                    f"  ⚠ Skipping unsupported file type: {os.path.basename(input_path)}"
                )
            stats["skipped"] += 1
            continue

        # Process file
        chunks = split_func(input_path, output_dir, max_chars, verbose)

        if chunks > 0:
            stats["processed"] += 1
            stats["chunks_created"] += chunks
        else:
            stats["failed"] += 1

    return stats


def process_directory(
    input_dir: str,
    output_dir: str,
    max_chars: int = DEFAULT_MAX_CHARS,
    split_by: str = "words",
    recursive: bool = False,
    check_extensions: bool = True,
    verbose: bool = True,
) -> dict:
    """Process all files in a directory.

    Args:
        input_dir: Input directory
        output_dir: Output directory
        max_chars: Maximum characters per chunk
        split_by: 'words' or 'lines'
        recursive: Whether to process subdirectories
        check_extensions: Whether to filter by file extension
        verbose: Whether to print progress

    Returns:
        Dictionary with processing statistics
    """
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist", file=sys.stderr)
        sys.exit(1)

    # Collect files
    input_paths = []

    if recursive:
        for root, dirs, files in os.walk(input_dir):
            for filename in files:
                input_paths.append(os.path.join(root, filename))
    else:
        for filename in os.listdir(input_dir):
            filepath = os.path.join(input_dir, filename)
            if os.path.isfile(filepath):
                input_paths.append(filepath)

    if not input_paths:
        print(f"No files found in '{input_dir}'")
        return {
            "total_files": 0,
            "processed": 0,
            "skipped": 0,
            "failed": 0,
            "chunks_created": 0,
        }

    if verbose:
        print(f"Processing {len(input_paths)} file(s) from '{input_dir}'...")
        print(f"Output directory: {output_dir}")
        print(f"Max chars per chunk: {max_chars:,}")
        print(f"Split mode: {split_by}\n")

    return process_files(
        input_paths, output_dir, max_chars, split_by, check_extensions, verbose
    )


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Split large text files into smaller chunks for NotebookLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Process files_to_split/ directory
  %(prog)s -i myfile.txt            # Split single file
  %(prog)s -i docs/ -o output/     # Process directory
  %(prog)s -i file.txt -m 200000   # Use 200k char limit
  %(prog)s -i file.txt --lines     # Split by lines instead of words
  %(prog)s -i docs/ -r             # Process subdirectories recursively
  %(prog)s -i data/ --all          # Process all files (ignore extensions)
        """,
    )

    parser.add_argument(
        "-i", "--input", help="Input file or directory (default: files_to_split/)"
    )

    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )

    parser.add_argument(
        "-m",
        "--max-chars",
        type=int,
        default=DEFAULT_MAX_CHARS,
        help=f"Maximum characters per chunk (default: {DEFAULT_MAX_CHARS:,})",
    )

    parser.add_argument(
        "--lines",
        action="store_true",
        help="Split by lines instead of words (preserves line structure)",
    )

    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Process subdirectories recursively",
    )

    parser.add_argument(
        "--all", action="store_true", help="Process all files regardless of extension"
    )

    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Quiet mode - minimal output"
    )

    args = parser.parse_args()

    # Determine input
    input_path = args.input if args.input else DEFAULT_INPUT_DIR

    # Validate max_chars
    if args.max_chars < 1000:
        print("Error: max-chars must be at least 1000", file=sys.stderr)
        sys.exit(1)

    # Process files
    split_by = "lines" if args.lines else "words"
    verbose = not args.quiet

    if os.path.isfile(input_path):
        # Single file mode
        if verbose:
            print(f"Processing file: {input_path}")
            print(f"Output directory: {args.output}")
            print(f"Max chars per chunk: {args.max_chars:,}")
            print(f"Split mode: {split_by}\n")

        stats = process_files(
            [input_path], args.output, args.max_chars, split_by, not args.all, verbose
        )
    else:
        # Directory mode
        stats = process_directory(
            input_path,
            args.output,
            args.max_chars,
            split_by,
            args.recursive,
            not args.all,
            verbose,
        )

    # Print summary
    if verbose and stats["total_files"] > 0:
        print(f"\n{'='*60}")
        print("Summary:")
        print(f"  Total files: {stats['total_files']}")
        print(f"  Processed: {stats['processed']}")
        print(f"  Skipped: {stats['skipped']}")
        if stats["failed"] > 0:
            print(f"  Failed: {stats['failed']}")
        print(f"  Chunks created: {stats['chunks_created']}")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
