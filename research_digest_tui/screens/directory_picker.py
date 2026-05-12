from pathlib import Path
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import DirectoryTree, Button, Label

class DirectoryPicker(ModalScreen[str]):
    """A modal screen that allows the user to pick a directory."""

    def __init__(self, start_path: str = ".") -> None:
        super().__init__()
        self.start_path = start_path
        self.selected_path = start_path

    def compose(self) -> ComposeResult:
        with Vertical(id="dir-picker-dialog"):
            yield Label("Select Output Directory", id="dir-picker-title")
            yield DirectoryTree(self.start_path, id="dir-picker-tree")
            yield Label(f"Selected: {self.selected_path}", id="dir-picker-selected")
            with Horizontal(id="dir-picker-buttons"):
                yield Button("Select", id="dir-picker-select", variant="primary")
                yield Button("Cancel", id="dir-picker-cancel")

    def on_mount(self) -> None:
        tree = self.query_one("#dir-picker-tree", DirectoryTree)
        tree.focus()

    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        self.selected_path = str(event.path)
        self.query_one("#dir-picker-selected", Label).update(f"Selected: {self.selected_path}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "dir-picker-select":
            tree = self.query_one("#dir-picker-tree", DirectoryTree)
            if tree.cursor_node and tree.cursor_node.data:
                path = tree.cursor_node.data.path
                if path.is_dir():
                    self.selected_path = str(path)
                else:
                    self.selected_path = str(path.parent)
            self.dismiss(self.selected_path)
        elif event.button.id == "dir-picker-cancel":
            self.dismiss(None)
