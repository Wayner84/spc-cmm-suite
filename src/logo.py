from __future__ import annotations

from pathlib import Path
from typing import Optional

import tkinter as tk
from tkinter import ttk


SEARCH_PATHS = (
    Path(__file__).resolve().parents[2] / "company-site" / "assets" / "img" / "logo.png",
    Path(__file__).resolve().parents[2] / "company-site" / "assets" / "img" / "logo-large.png",
    Path(__file__).resolve().parents[1] / "assets" / "logo.png",
)


class LogoBadge(ttk.Frame):
    def __init__(self, parent, text: str = "SPC CMM Suite"):
        super().__init__(parent)
        self._image: Optional[tk.PhotoImage] = None
        logo_path = next((path for path in SEARCH_PATHS if path.exists()), None)
        if logo_path:
            try:
                self._image = tk.PhotoImage(file=str(logo_path))
            except tk.TclError:
                self._image = None
        if self._image:
            ttk.Label(self, image=self._image).pack(anchor="w")
        else:
            canvas = tk.Canvas(self, width=180, height=56, bg="#0f1722", highlightthickness=0)
            canvas.pack(anchor="w")
            canvas.create_round = None
            canvas.create_rectangle(0, 0, 180, 56, fill="#0f1722", outline="#274062", width=2)
            canvas.create_text(18, 28, text="S", fill="#f8b84e", font=("Segoe UI", 28, "bold"), anchor="w")
            canvas.create_text(56, 28, text=text, fill="#ecf2fa", font=("Segoe UI", 13, "bold"), anchor="w")
            canvas.create_text(57, 43, text="Logo hook ready", fill="#90a6bf", font=("Segoe UI", 8), anchor="w")
