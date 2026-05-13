from pathlib import Path
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Input, Select, Static, Log, DirectoryTree
from textual.containers import Vertical, Horizontal, Container

from ..widgets.browser import FilteredDirectoryTree

class ConverterScreen(Screen):
    """Screen for converting local documents in a three-pane research workspace."""
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="workspace_container"):
            with Horizontal():
                with Vertical(id="left_pane"):
                    yield Static("📂 Source Files", classes="pane-title")
                    yield FilteredDirectoryTree("./", id="file_browser")
                
                with Vertical(id="center_pane"):
                    yield Static("⚙️ Ingestion Settings", classes="pane-title")
                    with Vertical(classes="settings-group"):
                        yield Static("Input Path", classes="label")
                        yield Input(placeholder="Select a file or enter path", id="input_file")
                        
                        yield Static("Output Directory", classes="label")
                        yield Input(value="./output", id="output_dir")
                        
                        yield Static("Destination Format", classes="label")
                        yield Select((("Obsidian", "obsidian"), ("Substack", "substack")), id="destination", value="obsidian")
                    
                    yield Button("Process Document", id="process_btn", variant="primary")
                
                with Vertical(id="right_pane"):
                    yield Static("📋 Conversion Log", classes="pane-title")
                    yield Log(id="log_view", classes="log-view")
                    
        yield Footer()

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle file selection in the browser."""
        self.query_one("#input_file", Input).value = str(event.path)
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "process_btn":
            self.process_document()
            
    def process_document(self) -> None:
        log_view = self.query_one("#log_view", Log)
        input_path_str = self.query_one("#input_file", Input).value
        output_dir_str = self.query_one("#output_dir", Input).value
        destination = self.query_one("#destination", Select).value
        
        if not input_path_str:
            log_view.write_line("[red]Error: Please select a file or directory first.[/red]")
            return
            
        input_path = Path(input_path_str)
        output_dir = Path(output_dir_str)
        
        log_view.write_line(f"🚀 Initialising ingestion: [bold]{input_path}[/bold]")
        
        def on_progress(current: int, total: int, file_path: Path, status: str):
            prefix = f"[{current}/{total}]"
            if status == "PROCESSING":
                log_view.write_line(f"{prefix} ⏳ Processing: {file_path.name}…")
            elif status == "SUCCESS":
                log_view.write_line(f"{prefix} ✅ [green]Done:[/green] {file_path.name}")
            elif status.startswith("FAILED"):
                log_view.write_line(f"{prefix} ❌ [red]Failed:[/red] {file_path.name} - {status}")

        try:
            from rdt.core.converter import CoreIngestor
            ingestor = CoreIngestor(output_dir=output_dir)
            
            # Use a worker for batch processing to keep TUI responsive
            self.run_worker(
                lambda: self._run_batch(ingestor, [input_path], destination, on_progress),
                thread=True
            )
                
        except Exception as e:
            log_view.write_line(f"[red]Fatal Error: {e}[/red]")

    def _run_batch(self, ingestor, paths, destination, callback):
        log_view = self.query_one("#log_view", Log)
        result = ingestor.process_batch(paths, on_progress=callback)
        
        # Post-processing for Substack if needed
        if destination == "substack" and result.successes:
            from rdt.adapters.substack import SubstackAdapter
            adapter = SubstackAdapter(output_dir=ingestor.output_dir)
            log_view.write_line("\n🎨 [bold]Applying Substack formatting…[/bold]")
            for md_path in result.successes:
                # We need to find the .md file created. process_file returns it.
                # Here we assume it's in output_dir with same name.
                target_md = ingestor.output_dir / f"{md_path.stem}.md"
                if target_md.exists():
                    adapter.export(target_md)
        
        summary = f"\n🏁 [bold]Ingestion Complete[/bold]\n   ✅ Success: {len(result.successes)}\n   ❌ Failed:  {len(result.failures)}"
        log_view.write_line(summary)
