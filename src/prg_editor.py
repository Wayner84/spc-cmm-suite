from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class PRGEditorPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=12)
        self.file_path: Path | None = None
        self.find_var = tk.StringVar()
        self.replace_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Open a .PRG file to edit it.")
        self._build_ui()

    def _build_ui(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 8))
        ttk.Button(toolbar, text="Open", command=self.open_file).pack(side="left")
        ttk.Button(toolbar, text="Save", command=self.save_file).pack(side="left", padx=(6, 0))
        ttk.Button(toolbar, text="Save As", command=self.save_as).pack(side="left", padx=(6, 18))

        ttk.Label(toolbar, text="Find").pack(side="left")
        ttk.Entry(toolbar, textvariable=self.find_var, width=22).pack(side="left", padx=(4, 8))
        ttk.Button(toolbar, text="Next", command=self.find_next).pack(side="left")

        ttk.Label(toolbar, text="Replace").pack(side="left", padx=(18, 0))
        ttk.Entry(toolbar, textvariable=self.replace_var, width=22).pack(side="left", padx=(4, 8))
        ttk.Button(toolbar, text="Replace", command=self.replace_current).pack(side="left")
        ttk.Button(toolbar, text="Replace All", command=self.replace_all).pack(side="left", padx=(6, 0))

        editor_frame = ttk.Frame(self)
        editor_frame.pack(fill="both", expand=True)
        self.editor = tk.Text(editor_frame, wrap="none", undo=True, font=("Consolas", 10))
        y_scroll = ttk.Scrollbar(editor_frame, orient="vertical", command=self.editor.yview)
        x_scroll = ttk.Scrollbar(editor_frame, orient="horizontal", command=self.editor.xview)
        self.editor.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.editor.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        editor_frame.rowconfigure(0, weight=1)
        editor_frame.columnconfigure(0, weight=1)

        self.editor.insert("1.0", "// PC-DMIS PRG editor\n// Open, edit, find/replace, and save.\n")
        ttk.Label(self, textvariable=self.status_var, foreground="#58677a").pack(anchor="w", pady=(8, 0))

    def open_file(self):
        path = filedialog.askopenfilename(title="Open PRG", filetypes=[("PC-DMIS Program", "*.prg"), ("All files", "*.*")])
        if not path:
            return
        self._load_path(Path(path))

    def _load_path(self, path: Path):
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            messagebox.showerror("Open failed", str(exc))
            return
        self.file_path = path
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", content)
        self.status_var.set(f"Editing {path}")

    def save_file(self):
        if not self.file_path:
            self.save_as()
            return
        self._write_to(self.file_path)

    def save_as(self):
        path = filedialog.asksaveasfilename(title="Save PRG As", defaultextension=".prg", filetypes=[("PC-DMIS Program", "*.prg"), ("All files", "*.*")])
        if not path:
            return
        self.file_path = Path(path)
        self._write_to(self.file_path)

    def _write_to(self, path: Path):
        try:
            path.write_text(self.editor.get("1.0", "end-1c"), encoding="utf-8", errors="replace")
        except Exception as exc:
            messagebox.showerror("Save failed", str(exc))
            return
        self.status_var.set(f"Saved {path}")

    def find_next(self):
        needle = self.find_var.get()
        if not needle:
            messagebox.showwarning("Find", "Enter text to search for.")
            return
        start = self.editor.index("insert")
        pos = self.editor.search(needle, start, stopindex="end") or self.editor.search(needle, "1.0", stopindex=start)
        if not pos:
            messagebox.showinfo("Find", f"'{needle}' not found.")
            return
        end = f"{pos}+{len(needle)}c"
        self.editor.tag_remove("sel", "1.0", "end")
        self.editor.tag_add("sel", pos, end)
        self.editor.mark_set("insert", end)
        self.editor.see(pos)

    def replace_current(self):
        if self.editor.tag_ranges("sel"):
            self.editor.delete("sel.first", "sel.last")
            self.editor.insert("insert", self.replace_var.get())
        else:
            self.find_next()
            if self.editor.tag_ranges("sel"):
                self.replace_current()

    def replace_all(self):
        needle = self.find_var.get()
        if not needle:
            messagebox.showwarning("Replace", "Enter text to search for.")
            return
        content = self.editor.get("1.0", "end-1c")
        count = content.count(needle)
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", content.replace(needle, self.replace_var.get()))
        self.status_var.set(f"Replaced {count} occurrence(s).")
