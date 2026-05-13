import shutil
from typing import Dict, List, NamedTuple

class DependencyStatus(NamedTuple):
    name: str
    found: bool
    path: str = ""
    install_hint: str = ""

class DependencyValidator:
    """Validates external system dependencies required for document conversion."""
    
    DEPENDENCIES = {
        "pdftotext": "Install 'poppler-utils' using your package manager (e.g., sudo dnf install poppler-utils)",
        "pandoc": "Install 'pandoc' using your package manager (e.g., sudo dnf install pandoc)"
    }

    def check_all(self) -> List[DependencyStatus]:
        """Check all required external dependencies."""
        results = []
        for name, hint in self.DEPENDENCIES.items():
            path = shutil.which(name)
            results.append(DependencyStatus(
                name=name,
                found=path is not None,
                path=path or "NOT FOUND",
                install_hint=hint
            ))
        return results

    def is_conversion_possible(self) -> bool:
        """Verify if at least basic conversion tools are available."""
        # We need pandoc for DOCX, and either pdftotext or PyMuPDF (fitz) for PDF.
        # CoreIngestor handles the fitz check internally, but we check system tools here.
        check = self.check_all()
        return all(d.found for d in check)
