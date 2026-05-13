import typer
from pathlib import Path

from rdt.tui.services.update_service import UpdateService
from rdt import digest

def version_callback(value: bool):
    if value:
        from rdt.core.version import get_local_version
        typer.echo(f"RDT v{get_local_version()}")
        raise typer.Exit()

# Initialise Typer app
app = typer.Typer(help="Research Digest Toolkit (RDT) CLI")

@app.callback()
def common(
    version: bool = typer.Option(None, "--version", "-v", callback=version_callback, help="Show version and exit"),
):
    pass

@app.command()
def check():
    """Verify system dependencies (pdftotext, pandoc)."""
    from rdt.core.validator import DependencyValidator
    
    validator = DependencyValidator()
    typer.echo("🔍 Checking system dependencies…")
    
    results = validator.check_all()
    all_found = True
    
    for dep in results:
        status_icon = "✅" if dep.found else "❌"
        typer.echo(f"{status_icon} {dep.name}: {dep.path}")
        if not dep.found:
            all_found = False
            typer.secho(f"   💡 {dep.install_hint}", fg=typer.colors.YELLOW)
            
    if all_found:
        typer.secho("\n✅ All core dependencies found. Ready to initialise conversion.", fg=typer.colors.GREEN)
    else:
        typer.secho("\n❌ Some dependencies are missing. Please install them to ensure full functionality.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

@app.command()
def convert(
    input_file: Path = typer.Argument(..., help="Path to the PDF or DOCX file to convert"),
    output_dir: Path = typer.Option(Path("./output"), "--output-dir", "-o", help="Directory to save the converted markdown"),
    destination: str = typer.Option("obsidian", help="Destination format: 'obsidian' or 'substack'")
):
    """Convert a document to markdown for a specific destination."""
    from rdt.core.converter import CoreIngestor
    from rdt.adapters.substack import SubstackAdapter
    import rdt.shared.obsidian as obsidian_adapter
    
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

@app.command()
def update(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation and update immediately"),
):
    """Check for updates and upgrade RDT to the latest version."""
    service = UpdateService()
    typer.echo("Checking for updates…")
    result = service.check_for_update()

    if result.error:
        typer.secho(f"Could not check for updates: {result.error}", fg=typer.colors.YELLOW)
        raise typer.Exit(code=0)

    if not result.available:
        typer.secho(
            f"✅ You're on the latest version (v{result.local_version}).",
            fg=typer.colors.GREEN,
        )
        raise typer.Exit(code=0)

    typer.echo(f"Update available: v{result.local_version} → v{result.remote_version}")

    if not yes:
        if not typer.confirm("Do you want to update now?"):
            typer.echo("Update skipped.")
            raise typer.Exit(code=0)

    typer.echo("Updating…")
    outcome = service.perform_update()

    if outcome.success:
        typer.secho(
            f"✅ Updated via {outcome.method}! Restart RDT to use the new version.",
            fg=typer.colors.GREEN,
        )
    else:
        typer.secho(f"❌ Update failed: {outcome.error}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

@app.command()
def scrape(
    config: str = typer.Option(
        "research_config.yaml",
        "--config",
        "-c",
        help="Config file path",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Quiet mode, minimal output",
    ),
    schedule: str = typer.Option(
        None,
        "--schedule",
        "-s",
        help="Run the digest on a schedule (e.g., 'every 4 hours').",
    ),
    scraper: str = typer.Option(
        None,
        "--scraper",
        help="Run only this scraper by config key (hackernews, rss, reddit, arxiv).",
    ),
):
    """Run the automated research aggregation pipeline."""
    # This calls the main logic in digest.py
    digest.main(config=config, quiet=quiet, schedule_str=schedule, scraper=scraper)

if __name__ == "__main__":
    app()

