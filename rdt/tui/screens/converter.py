from pathlib import Path
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Input, Select, Static, Log
from textual.containers import Vertical, Horizontal

class ConverterScreen(Screen):
    """Screen for converting local documents."""
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Static("Document Converter", classes="header-title"),
            Horizontal(
                Static("Input File: "),
                Input(placeholder="Enter path to .pdf or .docx file", id="input_file"),
                classes="input-row"
            ),
            Horizontal(
                Static("Output Dir: "),
                Input(value="./output", id="output_dir"),
                classes="input-row"
            ),
            Horizontal(
                Static("Destination: "),
                Select((("Obsidian", "obsidian"), ("Substack", "substack")), id="destination", value="obsidian"),
                classes="input-row"
            ),
            Button("Process Document", id="process_btn", variant="primary"),
            Log(id="log_view", classes="log-view"),
            classes="main-container"
        )
        yield Footer()
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "process_btn":
            self.process_document()
            
    def process_document(self) -> None:
        log_view = self.query_one("#log_view", Log)
        input_path_str = self.query_one("#input_file", Input).value
        output_dir_str = self.query_one("#output_dir", Input).value
        destination = self.query_one("#destination", Select).value
        
        if not input_path_str:
            log_view.write_line("[red]Error: Input file path is required.[/red]")
            return
            
        input_file = Path(input_path_str)
        output_dir = Path(output_dir_str)
        
        log_view.write_line(f"Starting conversion for {input_file} -> {output_dir}...")
        
        try:
            from rdt.core.converter import CoreIngestor
            ingestor = CoreIngestor(output_dir=output_dir)
            raw_md_path = ingestor.process_file(input_file)
            
            if destination == "substack":
                from rdt.adapters.substack import SubstackAdapter
                adapter = SubstackAdapter(output_dir=output_dir)
                final_path = adapter.export(raw_md_path)
                log_view.write_line(f"[green]Successfully converted and formatted for Substack: {final_path}[/green]")
            else:
                log_view.write_line(f"[green]Successfully converted and formatted for Obsidian: {raw_md_path}[/green]")
                
        except Exception as e:
            log_view.write_line(f"[red]Conversion failed: {e}[/red]")
