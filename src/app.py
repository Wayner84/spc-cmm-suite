from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from cmm_panel import AngleIJKPanel, QualityPlaceholderPanel
from compare_panel import ComparePanel
from logo import LogoBadge
from prg_editor import PRGEditorPanel
from shared_state import SharedState
from spc_panel import SPCPanel


class SPCCMMSuiteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SPC CMM Suite")
        self.geometry("1420x860")
        self.minsize(1200, 760)
        self.shared_state = SharedState()
        self._configure_style()
        self._build_ui()

    def _configure_style(self):
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Nav.TButton", font=("Segoe UI", 11, "bold"), padding=(12, 10), anchor="w")

    def _build_ui(self):
        shell = ttk.Frame(self, padding=10)
        shell.pack(fill="both", expand=True)
        shell.columnconfigure(1, weight=1)
        shell.rowconfigure(0, weight=1)

        nav = ttk.Frame(shell, padding=(8, 8, 14, 8))
        nav.grid(row=0, column=0, sticky="nsw")
        self.content = ttk.Frame(shell)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.rowconfigure(1, weight=1)
        self.content.columnconfigure(0, weight=1)

        LogoBadge(nav).pack(anchor="w", pady=(2, 18))
        ttk.Label(nav, text="Tool groups", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))

        self.section_title = tk.StringVar(value="SPC")
        self.section_subtitle = tk.StringVar(value="Capability analysis, quick plots, and inspection data cleanup.")

        self.sections = {
            "SPC": self._build_spc_section,
            "CMM": self._build_cmm_section,
            "Quality": self._build_quality_section,
        }
        for name in self.sections:
            ttk.Button(nav, text=name, style="Nav.TButton", command=lambda n=name: self._show_section(n)).pack(fill="x", pady=4)

        header = ttk.Frame(self.content, padding=(0, 0, 0, 10))
        header.grid(row=0, column=0, sticky="ew")
        ttk.Label(header, textvariable=self.section_title, font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(header, textvariable=self.section_subtitle, foreground="#5e6b79").pack(anchor="w", pady=(2, 0))

        self.section_host = ttk.Frame(self.content)
        self.section_host.grid(row=1, column=0, sticky="nsew")
        self.section_host.rowconfigure(0, weight=1)
        self.section_host.columnconfigure(0, weight=1)

        self._show_section("SPC")

    def _clear_section(self):
        for child in self.section_host.winfo_children():
            child.destroy()

    def _show_section(self, name: str):
        self._clear_section()
        self.sections[name]()

    def _build_spc_section(self):
        self.section_title.set("SPC")
        self.section_subtitle.set("Capability analysis, quick plots, and inspection data cleanup.")
        notebook = ttk.Notebook(self.section_host)
        notebook.grid(row=0, column=0, sticky="nsew")
        notebook.add(SPCPanel(notebook, shared_state=self.shared_state), text="Capability Workbench")

        guidance = ttk.Frame(notebook, padding=14)
        notebook.add(guidance, text="Workflow Notes")
        tk.Message(
            guidance,
            width=900,
            text=(
                "Use the workbench to load CSV/XLSX data, choose a numeric feature, optionally trim min/max ranges, "
                "set LSL/USL, and inspect histogram plus run chart output. This phase focuses on fast practical analysis."
            ),
        ).pack(anchor="w")

    def _build_cmm_section(self):
        self.section_title.set("CMM")
        self.section_subtitle.set("Shop-floor helper tools for vector setup and PRG editing.")
        notebook = ttk.Notebook(self.section_host)
        notebook.grid(row=0, column=0, sticky="nsew")
        notebook.add(AngleIJKPanel(notebook), text="Angle → IJK")
        notebook.add(PRGEditorPanel(notebook), text="PRG Editor")

        notebook.add(ComparePanel(notebook, shared_state=self.shared_state), text="CAD / CMM Compare")

    def _build_quality_section(self):
        self.section_title.set("Quality")
        self.section_subtitle.set("Reserved area for reporting and broader quality workflows.")
        notebook = ttk.Notebook(self.section_host)
        notebook.grid(row=0, column=0, sticky="nsew")
        notebook.add(QualityPlaceholderPanel(notebook), text="Roadmap")
