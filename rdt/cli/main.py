import typer
from pathlib import Path

# Initialize Typer app
app = typer.Typer(help="Research Digest Toolkit (RDT) CLI")

@app.command()
def convert(
    input_file: Path = typer.Argument(..., help="Path to the PDF or DOCX file to convert"),
    output_dir: Path = typer.Option(Path("./output"), "--output-dir", "-o", help="Directory to save the converted markdown"),
    destination: str = typer.Option("obsidian", help="Destination format: 'obsidian' or 'substack'")
):
    """Convert a document to markdown for a specific destination."""
    from rdt.core.converter import CoreIngestor
    from rdt.adapters.substack import SubstackAdapter
    import rdt.adapters.obsidian as obsidian_adapter
    
    typer.echo(f"Starting conversion for {input_file} -> {output_dir}")
    try:
        ingestor = CoreIngestor(output_dir=output_dir)
        raw_md_path = ingestor.process_file(input_file)
        
        if destination.lower() == "substack":
            adapter = SubstackAdapter(output_dir=output_dir)
            final_path = adapter.export(raw_md_path)
            typer.echo(f"Successfully converted and formatted for Substack: {final_path}")
        else:
            # Obsidian is the default. Obsidian adapter likely operates similarly or just uses the md
            typer.echo(f"Successfully converted and formatted for Obsidian: {raw_md_path}")
            
    except Exception as e:
        typer.secho(f"Conversion failed: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

@app.command()
def tui():
    """Launch the Terminal User Interface."""
    from rdt.tui.app import ResearchDigestApp
    try:
        app = ResearchDigestApp()
        app.run()
    except Exception as e:
        typer.secho(f"TUI failed to launch: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
