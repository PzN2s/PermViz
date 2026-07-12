#!/usr/bin/env python3
import os
import stat
import subprocess
import sys

def ensure_deps():
    try:
        import textual
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "--version"],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            print("Error: pip not found. Install it first:")
            print("  Ubuntu/Debian: sudo apt install python3-pip")
            print("  Fedora:        sudo dnf install python3-pip")
            print("  Arch:          sudo pacman -S python-pip")
            print("  NixOS:         use nix-shell")
            sys.exit(1)
        print("Installing textual...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "textual"])

ensure_deps()

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Label, Checkbox, Button, Static
from textual.containers import Horizontal, Vertical


class PermVizApp(App):
    CSS = """
    Screen {
        background: #1a1b26;
        align: center middle;
    }
    Header {
        background: #1a1b26;
        color: #a9b1d6;
    }
    Footer {
        background: #1a1b26;
        color: #565f89;
    }
    #body {
        width: auto;
        height: auto;
        align: center middle;
    }
    #controls {
        width: auto;
        height: auto;
        align: center middle;
        margin: 0 4 0 0;
    }
    #preview_box {
        width: 30;
        height: 12;
        border: round #3b4261;
        padding: 0 1;
        color: #565f89;
        overflow: hidden;
        margin: 0 0 0 4;
        background: #1e2030;
    }
    #filepath {
        text-style: bold;
        color: #c0caf5;
    }
    Label {
        color: #a9b1d6;
    }
    #octal {
        text-style: bold;
        color: #9ece6a;
        padding: 1 0;
    }
    .section {
        text-style: bold;
        margin: 1 0 0 0;
        color: #e0af68;
        width: auto;
    }
    .perm_row { height: auto; width: auto; align: center middle; }
    .perm_row Checkbox {
        margin: 0 2 0 0;
        color: #a9b1d6;
    }
    #apply {
        margin: 1 0 0 0;
        width: auto;
        background: #9ece6a;
        color: #1a1b26;
    }
    #apply:hover {
        background: #bb9af7;
    }
    #explanation {
        width: 60;
        margin: 1 0 0 0;
        padding: 1;
        border: tall #3b4261;
        color: #a9b1d6;
    }
    #warning {
        width: 60;
        margin: 1 0 0 0;
        padding: 0 1;
        color: #f7768e;
        text-style: bold;
        display: none;
    }
    """
    TITLE = "DEV:Reham | PermViz"

    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
        self.original = stat.S_IMODE(os.stat(filepath).st_mode)
        self.perm_bits = self._read(self.original)

    @staticmethod
    def _read(mode):
        return {
            "owner_r": bool(mode & stat.S_IRUSR), "owner_w": bool(mode & stat.S_IWUSR),
            "owner_x": bool(mode & stat.S_IXUSR), "group_r": bool(mode & stat.S_IRGRP),
            "group_w": bool(mode & stat.S_IWGRP), "group_x": bool(mode & stat.S_IXGRP),
            "other_r": bool(mode & stat.S_IROTH), "other_w": bool(mode & stat.S_IWOTH),
            "other_x": bool(mode & stat.S_IXOTH),
        }

    def _preview_text(self):
        try:
            if os.path.isdir(self.filepath):
                items = os.listdir(self.filepath)[:10]
                return "\n".join(items) if items else "(empty folder)"
            with open(self.filepath, "r", errors="replace") as f:
                lines = [next(f, "") for _ in range(10)]
            text = "".join(lines).strip()
            return text if text else "(empty file)"
        except Exception:
            return "(binary or unreadable)"

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="body"):
            with Vertical(id="controls"):
                yield Label(f"{self.filepath}", id="filepath")
                yield Label(f"Current: {oct(self.original)[2:].zfill(3)}")
                yield Label("New: 644", id="octal")

                for name, keys in [("Owner", ["owner_r", "owner_w", "owner_x"]),
                                    ("Group", ["group_r", "group_w", "group_x"]),
                                    ("Other", ["other_r", "other_w", "other_x"])]:
                    yield Label(name, classes="section")
                    with Horizontal(classes="perm_row"):
                        for k in keys:
                            label = k.split("_")[1].upper()
                            yield Checkbox(label, self.perm_bits[k], id=k)

                yield Button("Apply", id="apply", variant="success")
                yield Static("", id="explanation")
                yield Static("", id="warning")

            yield Static(self._preview_text(), id="preview_box")
        yield Footer()

    def on_mount(self):
        self._update()

    def on_checkbox_changed(self, event):
        self.perm_bits[event.checkbox.id] = event.value
        self._update()

    def compute_mode(self):
        bits = [("owner_r", stat.S_IRUSR), ("owner_w", stat.S_IWUSR), ("owner_x", stat.S_IXUSR),
                ("group_r", stat.S_IRGRP), ("group_w", stat.S_IWGRP), ("group_x", stat.S_IXGRP),
                ("other_r", stat.S_IROTH), ("other_w", stat.S_IWOTH), ("other_x", stat.S_IXOTH)]
        m = 0
        for k, b in bits:
            if self.perm_bits[k]:
                m |= b
        return m

    def _describe(self, who, r, w, x):
        val = (4 if r else 0) + (2 if w else 0) + (1 if x else 0)
        perms = ""
        if r: perms += "r"
        else: perms += "-"
        if w: perms += "w"
        else: perms += "-"
        if x: perms += "x"
        else: perms += "-"
        parts = []
        if r: parts.append("4 read")
        if w: parts.append("2 write")
        if x: parts.append("1 execute")
        if not parts:
            return f"  {who} ({perms}) = {val}  (no access)"
        return f"  {who} ({perms}) = {val}  ({' + '.join(parts)})"

    def _update(self):
        m = self.compute_mode()
        o = oct(m)[2:].zfill(3)
        self.query_one("#octal").update(f"New: {o}")

        lines = [
            self._describe("Owner", self.perm_bits["owner_r"], self.perm_bits["owner_w"], self.perm_bits["owner_x"]),
            self._describe("Group", self.perm_bits["group_r"], self.perm_bits["group_w"], self.perm_bits["group_x"]),
            self._describe("Other users", self.perm_bits["other_r"], self.perm_bits["other_w"], self.perm_bits["other_x"]),
        ]
        self.query_one("#explanation", Static).update("\n".join(lines))

        warning_box = self.query_one("#warning", Static)
        if not self.perm_bits["owner_r"]:
            warning_box.update("Warning: you (the owner) won't be able to open or read this file.")
            warning_box.styles.display = "block"
        elif self.perm_bits["other_w"] and self.perm_bits["other_x"]:
            warning_box.update("Warning: any user on this system could edit and run this file.")
            warning_box.styles.display = "block"
        else:
            warning_box.styles.display = "none"

    def on_button_pressed(self, event):
        if event.button.id == "apply":
            m = self.compute_mode()
            os.chmod(self.filepath, m)
            self.exit(message=f"Set to {oct(m)[2:].zfill(3)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <filepath>")
        sys.exit(1)
    PermVizApp(sys.argv[1]).run()
