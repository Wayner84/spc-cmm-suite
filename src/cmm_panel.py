from __future__ import annotations

import math
import tkinter as tk
from tkinter import ttk


class AngleIJKPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=12)
        self.xy_angle = tk.DoubleVar(value=0.0)
        self.z_angle = tk.DoubleVar(value=0.0)
        self.i_value = tk.StringVar(value="1.000")
        self.j_value = tk.StringVar(value="0.000")
        self.k_value = tk.StringVar(value="0.000")
        self.magnitude_value = tk.StringVar(value="1.000")
        self._build_ui()
        self._update_vector()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        controls = ttk.Frame(self)
        controls.grid(row=0, column=0, sticky="ew")
        controls.columnconfigure(1, weight=1)

        ttk.Label(controls, text="XY angle (°)").grid(row=0, column=0, sticky="w")
        ttk.Scale(controls, from_=-180, to=180, variable=self.xy_angle, command=lambda _v: self._update_vector()).grid(row=0, column=1, sticky="ew", padx=10)
        ttk.Label(controls, textvariable=self.xy_angle, width=8).grid(row=0, column=2, sticky="e")

        ttk.Label(controls, text="Z angle (°)").grid(row=1, column=0, sticky="w", pady=(10, 0))
        ttk.Scale(controls, from_=-90, to=90, variable=self.z_angle, command=lambda _v: self._update_vector()).grid(row=1, column=1, sticky="ew", padx=10, pady=(10, 0))
        ttk.Label(controls, textvariable=self.z_angle, width=8).grid(row=1, column=2, sticky="e", pady=(10, 0))

        output = ttk.LabelFrame(self, text="Direction cosines", padding=10)
        output.grid(row=1, column=0, sticky="ew", pady=12)
        for idx, (label, var) in enumerate((("I", self.i_value), ("J", self.j_value), ("K", self.k_value), ("|V|", self.magnitude_value))):
            ttk.Label(output, text=label, font=("Segoe UI", 10, "bold")).grid(row=0, column=idx * 2, sticky="w", padx=(0, 6))
            ttk.Label(output, textvariable=var, font=("Consolas", 12)).grid(row=0, column=idx * 2 + 1, sticky="w", padx=(0, 18))

        self.canvas = tk.Canvas(self, width=560, height=360, bg="#0e1621", highlightthickness=0)
        self.canvas.grid(row=2, column=0, sticky="nsew")

        ttk.Label(self, text="Live vector preview with simple projected axes for quick setup checks.", foreground="#58677a").grid(row=3, column=0, sticky="w", pady=(10, 0))

    def _update_vector(self):
        xy = math.radians(self.xy_angle.get())
        z = math.radians(self.z_angle.get())
        r = math.cos(z)
        i = r * math.cos(xy)
        j = r * math.sin(xy)
        k = math.sin(z)
        magnitude = math.sqrt(i * i + j * j + k * k)
        self.i_value.set(f"{i:.3f}")
        self.j_value.set(f"{j:.3f}")
        self.k_value.set(f"{k:.3f}")
        self.magnitude_value.set(f"{magnitude:.3f}")
        self._draw_vector(i, j, k)

    def _project(self, x, y, z, ox, oy, scale):
        return ox + x * scale - y * scale * 0.45, oy - z * scale + y * scale * 0.28

    def _draw_vector(self, i, j, k):
        c = self.canvas
        c.delete("all")
        w = int(c["width"])
        h = int(c["height"])
        ox, oy, scale = w // 2, h // 2 + 40, 120

        c.create_text(ox, 24, text="Angle → IJK live preview", fill="#e7edf5", font=("Segoe UI", 13, "bold"))
        for end, color, label in [((1, 0, 0), "#ff6b6b", "X"), ((0, 1, 0), "#4dd599", "Y"), ((0, 0, 1), "#5aa9ff", "Z")]:
            ex, ey = self._project(*end, ox, oy, scale)
            c.create_line(ox, oy, ex, ey, fill=color, width=3, arrow="last")
            c.create_text(ex + 12, ey + 6, text=label, fill=color, font=("Segoe UI", 10, "bold"))

        px, py = self._project(i, j, k, ox, oy, scale)
        c.create_line(ox, oy, px, py, fill="#ffc857", width=4, arrow="last")
        c.create_oval(ox - 5, oy - 5, ox + 5, oy + 5, fill="#ffffff", outline="")
        c.create_text(ox, h - 22, text=f"({i:.3f}, {j:.3f}, {k:.3f})", fill="#d8dee9", font=("Consolas", 12))


class QualityPlaceholderPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        ttk.Label(self, text="Quality tools placeholder", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(
            self,
            text=(
                "Reserved for layered quality workflows: FAIR packs, gage study helpers, non-conformance tracking, "
                "and reporting/export features. The navigation shell is in place so this section can grow cleanly next."
            ),
            wraplength=900,
            justify="left",
        ).pack(anchor="w", pady=(8, 0))
