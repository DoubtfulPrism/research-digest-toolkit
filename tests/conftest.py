#!/usr/bin/env python3
"""
Shared pytest configuration and fixtures.
"""

import sys
from pathlib import Path

import pytest

# Add parent directory to Python path for all tests
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def project_root():
    """Returns the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def sample_html():
    """Fixture providing sample HTML for testing HTML cleaning."""
    return """
    <div class="article">
        <h1>Test Article</h1>
        <p>This is a <a href="https://example.com">link</a> in a paragraph.</p>
        <p>Special characters: &amp; &lt; &gt; &quot; &#x27;</p>
    </div>
    """


@pytest.fixture
def sample_markdown():
    """Fixture providing sample markdown content."""
    return """# Test Article

## Introduction

This is a test article with some content.

## Code Example

```python
def hello():
    print("Hello, World!")
```

## Conclusion

That's all folks!
"""
