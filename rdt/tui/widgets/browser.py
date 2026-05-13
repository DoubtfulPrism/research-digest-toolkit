from pathlib import Path
from textual.widgets import DirectoryTree

class FilteredDirectoryTree(DirectoryTree):
    """A DirectoryTree that filters for research-relevant files (.pdf, .docx, .md)."""
    
    def filter_paths(self, paths: list[Path]) -> list[Path]:
        """Filter paths to only show directories and relevant document types."""
        allowed_extensions = {".pdf", ".docx", ".md"}
        return [
            path for path in paths
            if path.is_dir() or path.suffix.lower() in allowed_extensions
        ]
