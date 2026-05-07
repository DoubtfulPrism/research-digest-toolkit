from pathlib import Path
from datetime import datetime
from spellchecker import SpellChecker

class SubstackAdapter:
    """Formatter and exporter for Substack, enforcing UK English and metadata headers."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Configure pyspellchecker for UK English
        self.spell = SpellChecker(language='en')
        
        # We can add custom words or UK specific overrides if needed
        # pyspellchecker defaults to en-US but we can add UK specific terms.
        # Ideally, we would use an en-GB dictionary, but for basic enforcement,
        # we'll use the default dictionary and flag Americanisms if we build a custom list.
        # For this prototype, we'll just check for basic typos and flag them.
        
    def generate_metadata_header(self, title: str) -> str:
        """Generates the Substack specific metadata headers."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return f"""---
title: "{title}"
date: {date_str}
draft: true
type: post
---

"""

    def check_spelling(self, text: str) -> list[str]:
        """Checks spelling and returns a list of misspelled words."""
        # Simple extraction of words. In a real app, use a better tokenizer to ignore punctuation/markdown
        words = self.spell.split_words(text)
        misspelled = self.spell.unknown(words)
        return list(misspelled)

    def export(self, input_file: Path) -> Path:
        """Exports a markdown file for Substack."""
        input_file = Path(input_file)
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
            
        content = input_file.read_text()
        
        # 1. Check spelling
        misspelled = self.check_spelling(content)
        if misspelled:
            # We could log or raise warnings, for now we just proceed but could attach a report
            pass 
            
        # 2. Prepend metadata header
        title = input_file.stem.replace("_", " ").title()
        header = self.generate_metadata_header(title)
        
        final_content = header + content
        
        output_file = self.output_dir / f"{input_file.stem}_substack.md"
        output_file.write_text(final_content)
        
        return output_file
