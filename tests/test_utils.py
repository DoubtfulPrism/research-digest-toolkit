#!/usr/bin/env python3
"""
Tests for utils.py - Shared utility functions.
"""

import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import utils


@pytest.mark.unit
class TestGenerateFilename:
    """Tests for generate_filename function."""

    def test_basic_filename_generation(self):
        """Test basic filename generation with simple inputs."""
        filename = utils.generate_filename("hn", "Test Article", "item123")

        assert filename.startswith("hn_")
        assert filename.endswith(".md")
        assert "test_article" in filename
        assert "item123" in filename

    def test_sanitizes_special_characters_in_title(self):
        """Test that special characters are removed from titles."""
        filename = utils.generate_filename(
            "rss", 'Article: "Special" & <Chars>!', "url123"
        )

        # Should not contain special characters
        assert '"' not in filename
        assert "<" not in filename
        assert ">" not in filename
        assert "&" not in filename
        assert ":" not in filename

    def test_truncates_long_titles(self):
        """Test that very long titles are truncated."""
        long_title = "A" * 200  # 200 character title

        filename = utils.generate_filename("hn", long_title, "id123")

        # Title portion should be truncated (max 50 chars)
        # Total filename should be reasonable length
        assert len(filename) < 120  # source + id + title + extension

    def test_handles_empty_title(self):
        """Test handling of empty or None title."""
        filename = utils.generate_filename("reddit", "", "post456")

        assert "untitled" in filename
        assert filename.endswith(".md")

    def test_handles_none_title(self):
        """Test handling of None title."""
        filename = utils.generate_filename("rss", None, "article789")

        assert "untitled" in filename
        assert filename.endswith(".md")

    def test_sanitizes_unique_id(self):
        """Test that unique IDs with special characters are sanitized."""
        # URL as unique ID
        filename = utils.generate_filename(
            "rss", "Test", "https://example.com/article?id=123&param=value"
        )

        # Should not contain URL special characters
        assert "/" not in filename
        assert "?" not in filename
        assert "=" not in filename
        assert "&" not in filename
        assert ":" not in filename

    def test_truncates_long_unique_id(self):
        """Test that very long unique IDs are truncated."""
        long_id = "https://example.com/" + "a" * 200

        filename = utils.generate_filename("hn", "Article", long_id)

        # Should have reasonable length
        assert len(filename) < 150

    def test_replaces_spaces_with_underscores(self):
        """Test that spaces are replaced with underscores."""
        filename = utils.generate_filename("hn", "This Has Spaces", "id123")

        assert " " not in filename
        assert "this_has_spaces" in filename

    def test_different_sources(self):
        """Test that different sources are reflected in filenames."""
        title = "Same Title"
        unique_id = "same_id"

        hn_file = utils.generate_filename("hn", title, unique_id)
        rss_file = utils.generate_filename("rss", title, unique_id)
        reddit_file = utils.generate_filename("reddit", title, unique_id)

        assert hn_file.startswith("hn_")
        assert rss_file.startswith("rss_")
        assert reddit_file.startswith("reddit_")

    def test_lowercase_normalization(self):
        """Test that title is normalized to lowercase."""
        filename = utils.generate_filename("hn", "UPPERCASE TITLE", "id123")

        assert "uppercase_title" in filename
        assert "UPPERCASE" not in filename


@pytest.mark.unit
class TestSaveDocument:
    """Tests for save_document function."""

    def test_saves_file_successfully(self, tmp_path):
        """Test that a file is saved successfully."""
        filepath = tmp_path / "test_file.md"
        content = "# Test Content\n\nThis is a test."

        utils.save_document(filepath, content, verbose=False)

        assert filepath.exists()
        assert filepath.read_text(encoding="utf-8") == content

    def test_creates_parent_directories(self, tmp_path):
        """Test that parent directories are created if they don't exist."""
        filepath = tmp_path / "subdir" / "nested" / "test_file.md"
        content = "Test content"

        utils.save_document(filepath, content, verbose=False)

        assert filepath.exists()
        assert filepath.parent.exists()
        assert filepath.read_text(encoding="utf-8") == content

    def test_overwrites_existing_file(self, tmp_path):
        """Test that existing files are overwritten."""
        filepath = tmp_path / "existing.md"

        # Write initial content
        filepath.write_text("Old content", encoding="utf-8")

        # Overwrite with new content
        new_content = "New content"
        utils.save_document(filepath, new_content, verbose=False)

        assert filepath.read_text(encoding="utf-8") == new_content

    def test_handles_unicode_content(self, tmp_path):
        """Test that unicode content is saved correctly."""
        filepath = tmp_path / "unicode.md"
        content = "# Test\n\nUnicode: 你好 🎉 Привет"

        utils.save_document(filepath, content, verbose=False)

        assert filepath.exists()
        assert filepath.read_text(encoding="utf-8") == content

    def test_verbose_output(self, tmp_path, capsys):
        """Test that verbose mode produces output."""
        filepath = tmp_path / "test.md"
        content = "Test"

        utils.save_document(filepath, content, verbose=True)

        captured = capsys.readouterr()
        assert "test.md" in captured.out
        assert "✓" in captured.out or "Saved" in captured.out.lower()

    def test_silent_mode(self, tmp_path, capsys):
        """Test that verbose=False suppresses output."""
        filepath = tmp_path / "test.md"
        content = "Test"

        utils.save_document(filepath, content, verbose=False)

        captured = capsys.readouterr()
        assert captured.out == ""


@pytest.mark.unit
class TestCleanHTML:
    """Tests for clean_html function."""

    def test_returns_empty_string_for_none(self):
        """Test that None input returns empty string."""
        result = utils.clean_html(None)
        assert result == ""

    def test_returns_empty_string_for_empty_input(self):
        """Test that empty string input returns empty string."""
        result = utils.clean_html("")
        assert result == ""

    def test_decodes_html_entities(self):
        """Test that common HTML entities are decoded."""
        html = "It&#x27;s &quot;quoted&quot; &amp; <tagged>"

        result = utils.clean_html(html)

        assert "It's" in result
        assert '"quoted"' in result
        assert "&" in result
        assert "&amp;" not in result
        assert "&#x27;" not in result
        assert "&quot;" not in result

    def test_removes_paragraph_tags(self):
        """Test that <p> tags are removed and converted to line breaks."""
        html = "<p>Paragraph 1</p><p>Paragraph 2</p>"

        result = utils.clean_html(html)

        assert "<p>" not in result
        assert "</p>" not in result
        assert "Paragraph 1" in result
        assert "Paragraph 2" in result

    def test_handles_links(self):
        """Test that links are converted to text + URL format."""
        html = 'Check out <a href="https://example.com">this link</a>'

        result = utils.clean_html(html)

        assert "<a" not in result
        assert "this link" in result
        assert "https://example.com" in result

    def test_removes_all_html_tags(self):
        """Test that all HTML tags are removed."""
        html = "<div><span>Text with <strong>bold</strong> and <em>italic</em></span></div>"

        result = utils.clean_html(html)

        assert "<" not in result
        assert ">" not in result
        assert "Text with bold and italic" in result

    def test_normalizes_whitespace(self):
        """Test that excessive whitespace is normalized."""
        html = "Text\n\n\n\nwith\n\n\n\nmultiple\n\n\n\nlinebreaks"

        result = utils.clean_html(html)

        # Should not have more than 2 consecutive newlines
        assert "\n\n\n" not in result

    def test_strips_leading_trailing_whitespace(self):
        """Test that leading and trailing whitespace is removed."""
        html = "\n\n  Some content  \n\n"

        result = utils.clean_html(html)

        assert not result.startswith("\n")
        assert not result.endswith("\n")
        assert not result.startswith(" ")
        assert not result.endswith(" ")

    def test_complex_html_cleaning(self):
        """Test cleaning of complex HTML with multiple elements."""
        html = """
        <div>
            <h1>Title</h1>
            <p>This is a <a href="https://example.com">link</a> in a paragraph.</p>
            <p>Special chars: &amp; &lt; &gt; &quot; &#x27;</p>
        </div>
        """

        result = utils.clean_html(html)

        # Should contain text content
        assert "Title" in result
        assert "link" in result
        assert "https://example.com" in result
        assert "Special chars:" in result

        # Should not contain HTML
        assert "<" not in result or result.count("<") == result.count("&lt;")
        assert "</p>" not in result
        assert "<div>" not in result

        # Entities should be decoded
        assert "&amp;" not in result
        assert "&" in result

    def test_handles_malformed_html(self):
        """Test that malformed HTML doesn't cause errors."""
        html = "<p>Unclosed paragraph<div>Mixed <span>nesting</p></div>"

        # Should not raise an exception
        result = utils.clean_html(html)

        assert "Unclosed paragraph" in result
        assert "Mixed nesting" in result

    def test_preserves_code_blocks(self):
        """Test that content within code-like text is preserved."""
        html = "<p>Use the command <code>git status</code> to check.</p>"

        result = utils.clean_html(html)

        # Tags should be removed but content preserved
        assert "git status" in result
        assert "<code>" not in result

    def test_gt_lt_entity_decoding(self):
        """Test that &gt; and &lt; are decoded correctly."""
        html = "if (x &gt; 5 &amp;&amp; x &lt; 10)"

        result = utils.clean_html(html)

        assert ">" in result
        assert "<" in result
        assert "&gt;" not in result
        assert "&lt;" not in result
        assert "&amp;" not in result


@pytest.mark.integration
class TestUtilsWorkflow:
    """Integration tests for typical utility workflows."""

    def test_filename_and_save_workflow(self, tmp_path):
        """Test generating a filename and saving a document."""
        # Generate filename
        filename = utils.generate_filename(
            "hn",
            "Great Article About Testing",
            "https://news.ycombinator.com/item?id=123456",
        )

        # Create filepath
        filepath = tmp_path / filename

        # Create content
        content = "# Great Article About Testing\n\nThis is the content."

        # Save document
        utils.save_document(filepath, content, verbose=False)

        # Verify
        assert filepath.exists()
        assert "hn_" in filepath.name
        assert filepath.name.endswith(".md")
        assert filepath.read_text(encoding="utf-8") == content

    def test_html_cleaning_and_save_workflow(self, tmp_path):
        """Test cleaning HTML and saving the result."""
        # Raw HTML content
        raw_html = """
        <div>
            <h1>Article Title</h1>
            <p>This is a <a href="https://example.com">link</a>.</p>
            <p>Special: &amp; &quot;quoted&quot;</p>
        </div>
        """

        # Clean HTML
        clean_content = utils.clean_html(raw_html)

        # Generate filename
        filename = utils.generate_filename("rss", "Article Title", "article123")

        # Save
        filepath = tmp_path / filename
        utils.save_document(filepath, clean_content, verbose=False)

        # Verify
        saved_content = filepath.read_text(encoding="utf-8")
        assert "Article Title" in saved_content
        assert "link" in saved_content
        assert "<" not in saved_content or saved_content.count("<") == 0
        assert "&amp;" not in saved_content
