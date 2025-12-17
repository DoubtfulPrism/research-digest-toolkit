# Contributing to Research Digest Toolkit

Thanks for your interest in contributing! This project was vibecoded (AI-assisted development), and we welcome contributions from both humans and human+AI collaborations.

## 🤖 Vibecoding Welcome

This project was built with AI assistance, and we **encourage** contributors to use AI tools if helpful:
- Claude, ChatGPT, GitHub Copilot, etc.
- Just be clear about what's AI-assisted vs. human-written
- Test thoroughly - AI can make mistakes!

## 🎯 How to Contribute

### Reporting Issues

**Found a bug?**
1. Check if it's already reported
2. Include:
   - Your OS and Python version
   - Steps to reproduce
   - Expected vs. actual behavior
   - Error messages (if any)

**Have a feature idea?**
1. Open an issue first to discuss
2. Explain the use case
3. Why it fits this project's scope

### Pull Requests

**Before starting:**
1. Open an issue to discuss major changes
2. Fork the repository
3. Create a branch: `git checkout -b feature/your-feature`

**While developing:**
- Follow existing code style (PEP 8 for Python)
- Add docstrings to functions
- Update documentation if needed
- Test on Linux (Fedora/Ubuntu preferred)

**When submitting:**
```bash
# Test your changes
./your_tool.py --help
./research_digest.py  # If you modified the digest

# Commit with clear messages
git commit -m "Add: Support for Mastodon scraping"

# Push and create PR
git push origin feature/your-feature
```

## 📝 Code Style

### Python
- Follow PEP 8
- Use type hints where helpful
- Docstrings for all public functions
- Error handling with specific exceptions

**Example:**
```python
def process_content(url: str, verbose: bool = True) -> dict:
    """
    Process content from URL.

    Args:
        url: Source URL
        verbose: Whether to print progress

    Returns:
        Dictionary with processed data

    Raises:
        ValueError: If URL is invalid
        RequestException: If fetch fails
    """
    # Implementation
```

### Shell Scripts
- Use `set -e` for safety
- Check for required commands
- Provide helpful error messages

### Documentation
- Update README.md if adding features
- Add examples to AUTOMATION_GUIDE.md
- Keep PROJECT_README.md current

## 🔍 Areas for Contribution

### High Priority
- [ ] New source integrations (Mastodon, arXiv, etc.)
- [ ] Bug fixes
- [ ] Documentation improvements
- [ ] Auto-tagging improvements for specific domains

### Medium Priority
- [ ] Additional output formats
- [ ] Performance optimizations
- [ ] Better error messages
- [ ] Unit tests

### Low Priority
- [ ] Web UI
- [ ] Docker container
- [ ] Additional language support

## 🧪 Testing

**Before submitting:**
```bash
# Test the tool independently
./your_tool.py --help
./your_tool.py [test inputs]

# Test integration with research digest
./research_digest.py --dry-run

# Check on actual content
./research_digest.py
```

No formal test suite yet (contributions welcome!), but:
- Test on real data
- Check error handling
- Verify file output format
- Test with/without native tools installed

## 📚 Adding New Sources

**Template for new scrapers:**

```python
#!/usr/bin/env python3
"""
Source Name Scraper - Brief description
"""

import argparse
import sys
from pathlib import Path

DEFAULT_OUTPUT_DIR = "notebooklm_sources_sourcename"

def fetch_content(url: str) -> dict:
    """Fetch content from source."""
    # Implementation
    pass

def format_content(data: dict, format_type: str = 'markdown') -> str:
    """Format for output."""
    # Implementation
    pass

def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(description='...')
    # Add arguments
    args = parser.parse_args()
    # Process

if __name__ == '__main__':
    main()
```

**Integration checklist:**
1. Create scraper tool with CLI interface
2. Add to `research_config.yaml` structure
3. Integrate into `research_digest.py`
4. Add documentation
5. Update README.md

## 🔐 Security

**If you find a security issue:**
- Do NOT open a public issue
- Email: [maintainer email] (replace with yours)
- Include details and potential impact

**For code submissions:**
- No credentials in code
- Use environment variables for sensitive data
- Validate all user inputs
- Be careful with `subprocess` calls

## 📋 Commit Messages

Use clear, descriptive messages:

```
Add: New feature description
Fix: Bug description
Update: Documentation improvements
Refactor: Code restructuring
```

Examples:
```
Add: Mastodon instance scraping support
Fix: PDF conversion failing on non-ASCII filenames
Update: AUTOMATION_GUIDE with systemd examples
Refactor: Extract common HTTP handling to utils
```

## 🤝 Code of Conduct

**Be respectful:**
- Respectful communication
- Constructive feedback
- Assume good intentions
- Help beginners

**Vibecoding specific:**
- It's OK to use AI tools
- Be transparent about AI assistance
- AI-generated code still needs human review
- Test thoroughly - don't trust AI blindly

## ❓ Questions?

- Open an issue for general questions
- Check existing documentation first
- Be specific about your use case

## 🙏 Recognition

Contributors will be:
- Listed in PROJECT_README.md
- Credited in release notes
- Appreciated! 🎉

---

**Development Approach**: This project embraces vibecoding (AI-assisted development). Whether you code solo, with AI, or collaborate with others, quality contributions are welcome!
