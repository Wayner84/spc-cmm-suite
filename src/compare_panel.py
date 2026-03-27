from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd

from cmm_import import build_compare_dataframe, detect_mapping, load_results_table


class ComparePanel(ttk.Frame):
    def __init__(self, parent, shared_state=None):
        super().__init__(parent, padding=12)
        self.shared_state = shared_state
        self.df = pd.DataFrame()
        self.result_df = pd.DataFrame()

        self.file_var = tk.StringVar(value="No compare dataset loaded")
        self.nominal_var = tk.StringVar()
        self.measured_var = tk.StringVar()
        self.feature_var = tk.StringVar()
        self.tol_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Load a CSV/XLSX file containing nominal and measured values.")

        self.summary_vars = {
            "rows": tk.StringVar(value="—"),
            "mean_dev": tk.StringVar(value="—"),
            "max_abs_dev": tk.StringVar(value="—"),
            "pass_rate": tk.StringVar(value="—"),
        }

        self.fail_only_var = tk.BooleanVar(value=False)

        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        toolbar = ttk.Frame(self)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        ttk.Button(toolbar, text="Import compare CSV/XLSX", command=self._load_file).pack(side="left")
        ttk.Button(toolbar, text="Import CMM results", command=self._load_cmm_results).pack(side="left", padx=(8, 0))
        ttk.Button(toolbar, text="Export result CSV", command=self._export_results).pack(side="left", padx=(8, 0))
        ttk.Label(toolbar, textvariable=self.file_var).pack(side="left", padx=(12, 0))

        controls = ttk.LabelFrame(self, text="Compare controls", padding=10)
        controls.grid(row=1, column=0, sticky="nsw")
        controls.columnconfigure(0, weight=1)

        ttk.Label(controls, text="Feature / point label column (optional)").grid(row=0, column=0, sticky="w")
        self.feature_combo = ttk.Combobox(controls, textvariable=self.feature_var, state="readonly", width=28)
        self.feature_combo.grid(row=1, column=0, sticky="ew", pady=(2, 10))
        self.feature_combo.bind("<<ComboboxSelected>>", lambda _e: self._refresh_view())

        ttk.Label(controls, text="Nominal column").grid(row=2, column=0, sticky="w")
        self.nominal_combo = ttk.Combobox(controls, textvariable=self.nominal_var, state="readonly", width=28)
        self.nominal_combo.grid(row=3, column=0, sticky="ew", pady=(2, 10))
        self.nominal_combo.bind("<<ComboboxSelected>>", lambda _e: self._refresh_view())

        ttk.Label(controls, text="Measured column").grid(row=4, column=0, sticky="w")
        self.measured_combo = ttk.Combobox(controls, textvariable=self.measured_var, state="readonly", width=28)
        self.measured_combo.grid(row=5, column=0, sticky="ew", pady=(2, 10))
        self.measured_combo.bind("<<ComboboxSelected>>", lambda _e: self._refresh_view())

        ttk.Label(controls, text="Symmetric tolerance (±)").grid(row=6, column=0, sticky="w")
        ttk.Entry(controls, textvariable=self.tol_var, width=14).grid(row=7, column=0, sticky="w", pady=(2, 10))
        ttk.Checkbutton(controls, text="Show FAIL rows only", variable=self.fail_only_var, command=self._refresh_view).grid(row=8, column=0, sticky="w", pady=(0, 6))
        ttk.Label(controls, text="Feature search contains").grid(row=9, column=0, sticky="w")
        search_entry = ttk.Entry(controls, textvariable=self.search_var, width=24)
        search_entry.grid(row=10, column=0, sticky="ew", pady=(2, 10))
        search_entry.bind("<KeyRelease>", lambda _e: self._refresh_view())

        ttk.Button(controls, text="Analyse compare", command=self._refresh_view).grid(row=11, column=0, sticky="ew")

        summary = ttk.LabelFrame(controls, text="Summary", padding=10)
        summary.grid(row=12, column=0, sticky="ew", pady=(12, 0))
        fields = [
            ("Rows", "rows"),
            ("Mean deviation", "mean_dev"),
            ("Max |deviation|", "max_abs_dev"),
            ("Pass rate", "pass_rate"),
        ]
        for idx, (label, key) in enumerate(fields):
            ttk.Label(summary, text=label).grid(row=idx, column=0, sticky="w", padx=(0, 12))
            ttk.Label(summary, textvariable=self.summary_vars[key], font=("Consolas", 10)).grid(row=idx, column=1, sticky="e")

        right = ttk.Notebook(self)
        right.grid(row=1, column=1, sticky="nsew", padx=(12, 0))

        overview = ttk.Frame(right, padding=10)
        plots = ttk.Frame(right, padding=10)
        data = ttk.Frame(right, padding=10)
        right.add(overview, text="Overview")
        right.add(plots, text="Plots")
        right.add(data, text="Results")

        self.summary_text = tk.Text(overview, height=14, wrap="word")
        self.summary_text.pack(fill="both", expand=True)
        self.summary_text.insert("1.0", "Load data to compare nominal vs measured dimensions, features, or point results.")
        self.summary_text.configure(state="disabled")

        self.figure = Figure(figsize=(8, 5), dpi=100)
        self.ax_dev = self.figure.add_subplot(211)
        self.ax_scatter = self.figure.add_subplot(212)
        self.figure.tight_layout(pad=2.2)
        self.canvas = FigureCanvasTkAgg(self.figure, master=plots)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.preview = ttk.Treeview(data, show="headings", height=18)
        self.preview.pack(fill="both", expand=True)

        ttk.Label(self, textvariable=self.status_var, foreground="#58677a").grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))

    def _load_file(self):
        path = filedialog.askopenfilename(title="Open compare dataset", filetypes=[("Data files", "*.csv;*.xlsx;*.xls"), ("All files", "*.*")])
        if not path:
            return
        try:
            if path.lower().endswith(".csv"):
                self.df = pd.read_csv(path)
            else:
                self.df = pd.read_excel(path)
        except Exception as exc:
            messagebox.showerror("Import failed", str(exc))
            return

        self.file_var.set(path)
        self._bind_columns_from_dataframe()
        self._refresh_view()

    def _load_cmm_results(self):
        path = filedialog.askopenfilename(title="Open CMM results", filetypes=[("Results files", "*.csv;*.xlsx;*.xls;*.txt;*.tsv"), ("All files", "*.*")])
        if not path:
            return
        try:
            self.df = load_results_table(path)
            mapping = detect_mapping(self.df)
        except Exception as exc:
            messagebox.showerror("CMM import failed", str(exc))
            return

        self.file_var.set(path)
        self._bind_columns_from_dataframe()
        self.feature_var.set(mapping.feature_column or "")
        if mapping.nominal_column:
            self.nominal_var.set(mapping.nominal_column)
        if mapping.measured_column:
            self.measured_var.set(mapping.measured_column)

        if mapping.tolerance_column and mapping.tolerance_column in self.df.columns:
            tol_series = pd.to_numeric(self.df[mapping.tolerance_column], errors="coerce").dropna().abs()
            if not tol_series.empty:
                self.tol_var.set(f"{float(tol_series.iloc[0]):g}")

        try:
            self.result_df = build_compare_dataframe(self.df, mapping)
            if self.fail_only_var.get() and "Status" in self.result_df.columns:
                self.result_df = self.result_df.loc[self.result_df["Status"].eq("FAIL")].copy()
            feature_col = self.feature_var.get().strip()
            search_text = self.search_var.get().strip().lower()
            if feature_col and search_text and feature_col in self.result_df.columns:
                self.result_df = self.result_df.loc[self.result_df[feature_col].astype(str).str.lower().str.contains(search_text, na=False)].copy()
            if self.shared_state is not None:
                self.shared_state.compare_results = self.result_df.copy()
                self.shared_state.compare_source_name = self.file_var.get()
            self._update_summary()
            self._update_plots()
            self._update_preview()
            self.status_var.set(f"Imported CMM results and compared {len(self.result_df)} valid rows.")
        except Exception:
            self._refresh_view()

    def _bind_columns_from_dataframe(self):
        cols = list(self.df.columns)
        numeric_cols = [col for col in cols if pd.to_numeric(self.df[col], errors="coerce").notna().any()]
        label_cols = ["", *cols]
        self.feature_combo["values"] = label_cols
        self.nominal_combo["values"] = numeric_cols
        self.measured_combo["values"] = numeric_cols

        if len(numeric_cols) >= 2:
            if not self.nominal_var.get() or self.nominal_var.get() not in numeric_cols:
                self.nominal_var.set(numeric_cols[0])
            if not self.measured_var.get() or self.measured_var.get() not in numeric_cols:
                self.measured_var.set(numeric_cols[1])
        elif len(numeric_cols) == 1:
            self.nominal_var.set(numeric_cols[0])
            self.measured_var.set(numeric_cols[0])

        if not self.feature_var.get() or self.feature_var.get() not in cols:
            guess_feature = next((c for c in cols if str(c).lower() in {"feature", "point", "name", "id", "dimension"}), "")
            self.feature_var.set(guess_feature)

    def _parse_tol(self):
        value = self.tol_var.get().strip()
        if not value:
            return None
        return abs(float(value))

    def _refresh_view(self):
        if self.df.empty:
            return
        nominal_col = self.nominal_var.get()
        measured_col = self.measured_var.get()
        if not nominal_col or not measured_col:
            self.status_var.set("Choose nominal and measured columns.")
            return

        try:
            nominal = pd.to_numeric(self.df[nominal_col], errors="coerce")
            measured = pd.to_numeric(self.df[measured_col], errors="coerce")
            result = self.df.copy()
            result["Nominal"] = nominal
            result["Measured"] = measured
            result = result.loc[result["Nominal"].notna() & result["Measured"].notna()].copy()
            result["Deviation"] = result["Measured"] - result["Nominal"]
            result["AbsDeviation"] = result["Deviation"].abs()

            tol = self._parse_tol()
            if tol is not None:
                result["Tolerance"] = tol
                result["Status"] = result["AbsDeviation"].apply(lambda v: "PASS" if v <= tol else "FAIL")
            else:
                result["Tolerance"] = ""
                result["Status"] = ""
        except Exception as exc:
            self.status_var.set(f"Compare warning: {exc}")
            return

        if self.fail_only_var.get() and "Status" in result.columns:
            result = result.loc[result["Status"].eq("FAIL")].copy()

        feature_col = self.feature_var.get().strip()
        search_text = self.search_var.get().strip().lower()
        if feature_col and search_text and feature_col in result.columns:
            result = result.loc[result[feature_col].astype(str).str.lower().str.contains(search_text, na=False)].copy()

        self.result_df = result
        if self.shared_state is not None:
            self.shared_state.compare_results = self.result_df.copy()
            self.shared_state.compare_source_name = self.file_var.get()
        self._update_summary()
        self._update_plots()
        self._update_preview()
        self.status_var.set(f"Compared {len(self.result_df)} valid rows.")

    def _update_summary(self):
        if self.result_df.empty:
            return
        tol = self._parse_tol()
        mean_dev = self.result_df["Deviation"].mean()
        max_abs_dev = self.result_df["AbsDeviation"].max()
        self.summary_vars["rows"].set(str(len(self.result_df)))
        self.summary_vars["mean_dev"].set(f"{mean_dev:,.4f}")
        self.summary_vars["max_abs_dev"].set(f"{max_abs_dev:,.4f}")
        if tol is not None and len(self.result_df):
            pass_rate = (self.result_df["Status"].eq("PASS").mean()) * 100
            self.summary_vars["pass_rate"].set(f"{pass_rate:,.1f}%")
        else:
            self.summary_vars["pass_rate"].set("—")

        feature_note = self.feature_var.get().strip() or "(none selected)"
        text = (
            f"Nominal column: {self.nominal_var.get()}\n"
            f"Measured column: {self.measured_var.get()}\n"
            f"Feature label column: {feature_note}\n"
            f"Rows compared: {len(self.result_df)}\n"
            f"Mean deviation: {mean_dev:,.4f}\n"
            f"Max absolute deviation: {max_abs_dev:,.4f}\n"
        )
        if tol is not None:
            fail_count = int(self.result_df["Status"].eq("FAIL").sum())
            text += f"Tolerance: ±{tol:,.4f}\nFail count: {fail_count}\n"
        else:
            text += "Tolerance: not set\n"

        self.summary_text.configure(state="normal")
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("1.0", text)
        self.summary_text.configure(state="disabled")

    def _update_plots(self):
        self.ax_dev.clear()
        self.ax_scatter.clear()

        if self.result_df.empty:
            self.canvas.draw_idle()
            return

        x = list(range(1, len(self.result_df) + 1))
        deviations = self.result_df["Deviation"].tolist()
        self.ax_dev.plot(x, deviations, marker="o", linewidth=1.2, color="#8e44ad")
        self.ax_dev.axhline(0.0, color="#34495e", linewidth=1)
        tol = self._parse_tol()
        if tol is not None:
            self.ax_dev.axhline(tol, color="#2ecc71", linestyle="--", label="+Tol")
            self.ax_dev.axhline(-tol, color="#e74c3c", linestyle="--", label="-Tol")
            self.ax_dev.legend(loc="best")
        self.ax_dev.set_title("Deviation by row")
        self.ax_dev.set_xlabel("Observation")
        self.ax_dev.set_ylabel("Measured - Nominal")
        self.ax_dev.grid(alpha=0.25)

        self.ax_scatter.scatter(self.result_df["Nominal"], self.result_df["Measured"], color="#2980b9", alpha=0.8)
        min_axis = min(self.result_df["Nominal"].min(), self.result_df["Measured"].min())
        max_axis = max(self.result_df["Nominal"].max(), self.result_df["Measured"].max())
        self.ax_scatter.plot([min_axis, max_axis], [min_axis, max_axis], linestyle="--", color="#7f8c8d")
        self.ax_scatter.set_title("Measured vs nominal")
        self.ax_scatter.set_xlabel("Nominal")
        self.ax_scatter.set_ylabel("Measured")
        self.ax_scatter.grid(alpha=0.25)

        self.figure.tight_layout(pad=2.0)
        self.canvas.draw_idle()

    def _update_preview(self):
        preview_df = self.result_df.head(200).copy()
        feature_col = self.feature_var.get().strip()
        preferred = [c for c in [feature_col, "Nominal", "Measured", "Deviation", "AbsDeviation", "Tolerance", "Status"] if c and c in preview_df.columns]
        remaining = [c for c in preview_df.columns if c not in preferred]
        preview_df = preview_df[preferred + remaining]

        cols = list(preview_df.columns)
        self.preview.delete(*self.preview.get_children())
        self.preview["columns"] = cols
        for col in cols:
            self.preview.heading(col, text=col)
            self.preview.column(col, width=120, stretch=True)

        for _, row in preview_df.iterrows():
            values = ["" if pd.isna(value) else str(value) for value in row.tolist()]
            self.preview.insert("", "end", values=values)

    def _export_results(self):
        if self.result_df.empty:
            messagebox.showinfo("Export", "No compare results available yet.")
            return
        path = filedialog.asksaveasfilename(title="Export compare results", defaultextension=".csv", filetypes=[("CSV", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        try:
            self.result_df.to_csv(path, index=False)
        except Exception as exc:
            messagebox.showerror("Export failed", str(exc))
            return
        self.status_var.set(f"Exported compare results to {path}")
