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

Thanks to the new plugin architecture, adding a new scraper is the easiest way to contribute.

**1. Create Your Plugin File:**
- Create a new file in the `scrapers/` directory (e.g., `scrapers/mastodon_scraper.py`).

**2. Build the Scraper Class:**
- Your class must inherit from `scrapers.base.ScraperBase`.
- It must have a `name` attribute (which will be the key used in the config file).
- It must have a `run(self, config, output_dir)` method.

**Example Plugin (`scrapers/my_scraper.py`):**
```python
from .base import ScraperBase
from pathlib import Path
import utils
import database

class MyScraper(ScraperBase):
    def __init__(self, verbose=True):
        super().__init__(verbose)
        self.name = "MySource"

    def run(self, config: dict, output_dir: Path):
        if self.verbose:
            print(f"🔥 Scraping {self.name}...")
        
        # 1. Get settings from the config dict
        api_key = config.get("api_key")
        
        # 2. Fetch your data
        # ... your logic ...
        
        # 3. For each item, check if it's already in the DB
        unique_id = "some_unique_id_for_your_item"
        if database.item_exists(self.name.lower(), unique_id):
            # Skip it
            return

        # 4. Format content and save using utils
        title = "My Awesome Article"
        content = "Formatted markdown content..."
        filename = utils.generate_filename(self.name.lower(), title, unique_id)
        filepath = output_dir / self.name.lower() / filename
        utils.save_document(filepath, content, self.verbose)
        
        # 5. Add the new item's ID to the database
        database.add_item(self.name.lower(), unique_id)
```

**3. Add Configuration to `research_config.yaml`:**
- Add a new entry under the `scrapers` key in `research_config.yaml`. The key name must be the lowercase version of your class's `name`.

```yaml
scrapers:
  mysource:  # Corresponds to `name = "MySource"`
    enabled: true
    api_key: "your_secret_key"
  # ... other scrapers
```

That's it! The `research_digest.py` script will automatically discover and run your new plugin.

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
