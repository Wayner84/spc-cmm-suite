from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd

from analytics import NUMERIC_METRICS, apply_simple_filters, calculate_capability, coerce_numeric, format_metric, load_dataset


class SPCPanel(ttk.Frame):
    def __init__(self, parent, shared_state=None):
        super().__init__(parent, padding=12)
         
        self.shared_state = shared_state
        self.source_df = pd.DataFrame()
        self.filtered_df = pd.DataFrame()
        self.metric_vars: dict[str, tk.StringVar] = {label: tk.StringVar(value="—") for label, _ in NUMERIC_METRICS}

        self.file_var = tk.StringVar(value="No dataset loaded")
        self.column_var = tk.StringVar()
        self.lsl_var = tk.StringVar()
        self.usl_var = tk.StringVar()
        self.min_filter_var = tk.StringVar()
        self.max_filter_var = tk.StringVar()
        self.drop_na_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Load a CSV or XLSX inspection file to begin.")

        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        toolbar = ttk.Frame(self)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        ttk.Button(toolbar, text="Import CSV/XLSX", command=self._load_file).pack(side="left")
        ttk.Button(toolbar, text="Use CAD/CMM compare results", command=self._load_compare_results).pack(side="left", padx=(8, 0))
        ttk.Label(toolbar, textvariable=self.file_var).pack(side="left", padx=(12, 0))

        controls = ttk.LabelFrame(self, text="Analysis controls", padding=10)
        controls.grid(row=1, column=0, sticky="nsw")

        ttk.Label(controls, text="Numeric feature column").grid(row=0, column=0, sticky="w")
        self.column_combo = ttk.Combobox(controls, textvariable=self.column_var, state="readonly", width=28)
        self.column_combo.grid(row=1, column=0, sticky="ew", pady=(2, 10))
        self.column_combo.bind("<<ComboboxSelected>>", lambda _e: self._refresh_view())

        ttk.Label(controls, text="Spec limits").grid(row=2, column=0, sticky="w")
        spec_row = ttk.Frame(controls)
        spec_row.grid(row=3, column=0, sticky="ew", pady=(2, 10))
        ttk.Label(spec_row, text="LSL").pack(side="left")
        ttk.Entry(spec_row, textvariable=self.lsl_var, width=10).pack(side="left", padx=(4, 12))
        ttk.Label(spec_row, text="USL").pack(side="left")
        ttk.Entry(spec_row, textvariable=self.usl_var, width=10).pack(side="left", padx=(4, 0))

        ttk.Label(controls, text="Data filter on selected column").grid(row=4, column=0, sticky="w")
        filt = ttk.Frame(controls)
        filt.grid(row=5, column=0, sticky="ew", pady=(2, 10))
        ttk.Label(filt, text="Min").grid(row=0, column=0, sticky="w")
        ttk.Entry(filt, textvariable=self.min_filter_var, width=10).grid(row=0, column=1, padx=(4, 10))
        ttk.Label(filt, text="Max").grid(row=0, column=2, sticky="w")
        ttk.Entry(filt, textvariable=self.max_filter_var, width=10).grid(row=0, column=3, padx=(4, 0))
        ttk.Checkbutton(controls, text="Drop non-numeric / blanks in selected column", variable=self.drop_na_var).grid(row=6, column=0, sticky="w", pady=(0, 10))

        ttk.Button(controls, text="Apply / Analyse", command=self._refresh_view).grid(row=7, column=0, sticky="ew")
        ttk.Button(controls, text="Reset filters", command=self._reset_filters).grid(row=8, column=0, sticky="ew", pady=(6, 0))

        metrics = ttk.LabelFrame(controls, text="Capability summary", padding=10)
        metrics.grid(row=9, column=0, sticky="ew", pady=(12, 0))
        for idx, (label, _) in enumerate(NUMERIC_METRICS):
            ttk.Label(metrics, text=label).grid(row=idx, column=0, sticky="w", padx=(0, 16))
            ttk.Label(metrics, textvariable=self.metric_vars[label], font=("Consolas", 10)).grid(row=idx, column=1, sticky="e")

        right = ttk.Notebook(self)
        right.grid(row=1, column=1, sticky="nsew", padx=(12, 0))

        overview = ttk.Frame(right, padding=10)
        plots = ttk.Frame(right, padding=10)
        data = ttk.Frame(right, padding=10)
        right.add(overview, text="Overview")
        right.add(plots, text="Plots")
        right.add(data, text="Data preview")

        self.summary_text = tk.Text(overview, height=14, wrap="word")
        self.summary_text.pack(fill="both", expand=True)
        self.summary_text.insert("1.0", "Import data to see analysis notes, filter effects, and capability interpretation.")
        self.summary_text.configure(state="disabled")

        self.figure = Figure(figsize=(8, 5), dpi=100)
        self.ax_hist = self.figure.add_subplot(211)
        self.ax_run = self.figure.add_subplot(212)
        self.figure.tight_layout(pad=2.2)
        self.canvas = FigureCanvasTkAgg(self.figure, master=plots)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.preview = ttk.Treeview(data, show="headings", height=18)
        self.preview.pack(fill="both", expand=True)

        ttk.Label(self, textvariable=self.status_var, foreground="#58677a").grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))

    def _load_file(self):
        path = filedialog.askopenfilename(title="Open inspection dataset", filetypes=[("Data files", "*.csv;*.xlsx;*.xls"), ("All files", "*.*")])
        if not path:
            return
        try:
            self.source_df = load_dataset(path)
        except Exception as exc:
            messagebox.showerror("Import failed", str(exc))
            return

        self.file_var.set(path)
        numeric_columns = [col for col in self.source_df.columns if coerce_numeric(self.source_df[col]).notna().any()]
        self.column_combo["values"] = numeric_columns
        if numeric_columns:
            self.column_var.set(numeric_columns[0])
        self.filtered_df = self.source_df.copy()
        self._refresh_view()

    def _load_compare_results(self):
        if self.shared_state is None or self.shared_state.compare_results.empty:
            self.status_var.set("No CAD/CMM compare results are available yet.")
            return

        self.source_df = self.shared_state.compare_results.copy()
        source_name = self.shared_state.compare_source_name or "compare results"
        self.file_var.set(f"From CAD/CMM compare: {source_name}")
        numeric_columns = [col for col in self.source_df.columns if coerce_numeric(self.source_df[col]).notna().any()]
        self.column_combo["values"] = numeric_columns
        preferred = ["Deviation", "AbsDeviation", "Measured", "Nominal"]
        selected = next((col for col in preferred if col in numeric_columns), numeric_columns[0] if numeric_columns else "")
        if selected:
            self.column_var.set(selected)
        if "Tolerance" in self.source_df.columns:
            tol_series = coerce_numeric(self.source_df["Tolerance"]).dropna()
            if not tol_series.empty:
                tol = float(tol_series.iloc[0])
                self.lsl_var.set(f"{-tol:g}")
                self.usl_var.set(f"{tol:g}")
        self.filtered_df = self.source_df.copy()
        self._refresh_view()

    def _parse_float(self, value: str):
        value = value.strip()
        if not value:
            return None
        return float(value)

    def _reset_filters(self):
        self.min_filter_var.set("")
        self.max_filter_var.set("")
        self.lsl_var.set("")
        self.usl_var.set("")
        self.drop_na_var.set(True)
        self._refresh_view()

    def _refresh_view(self):
        if self.source_df.empty or not self.column_var.get():
            return
        try:
            min_filter = self._parse_float(self.min_filter_var.get())
            max_filter = self._parse_float(self.max_filter_var.get())
            lsl = self._parse_float(self.lsl_var.get())
            usl = self._parse_float(self.usl_var.get())
            self.filtered_df = apply_simple_filters(
                self.source_df,
                target_column=self.column_var.get(),
                min_value=min_filter,
                max_value=max_filter,
                drop_na_target=self.drop_na_var.get(),
            )
            result = calculate_capability(self.filtered_df[self.column_var.get()], self.column_var.get(), lsl, usl)
        except Exception as exc:
            self.status_var.set(f"Analysis warning: {exc}")
            return

        for label, attr in NUMERIC_METRICS:
            self.metric_vars[label].set(format_metric(getattr(result, attr)))

        removed = len(self.source_df) - len(self.filtered_df)
        note = (
            f"Analysed column: {result.column}\n"
            f"Rows loaded: {len(self.source_df)}\n"
            f"Rows kept after filter: {len(self.filtered_df)}\n"
            f"Rows removed: {removed}\n\n"
            f"Capability indices use sample stdev for Cp/Cpk and population stdev for Pp/Ppk.\n"
            f"If only one spec limit or no valid spread is available, capability fields remain blank."
        )
        self.summary_text.configure(state="normal")
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("1.0", note)
        self.summary_text.configure(state="disabled")

        self._update_plots(lsl, usl)
        self._update_preview()
        self.status_var.set(f"Loaded {len(self.source_df)} rows. Active filtered set: {len(self.filtered_df)} rows.")

    def _update_plots(self, lsl, usl):
        values = coerce_numeric(self.filtered_df[self.column_var.get()]).dropna()
        self.ax_hist.clear()
        self.ax_run.clear()

        self.ax_hist.hist(values, bins=min(20, max(5, len(values) // 2 or 5)), color="#4f81bd", edgecolor="#23364a")
        self.ax_hist.set_title("Histogram")
        self.ax_hist.set_xlabel(self.column_var.get())
        self.ax_hist.set_ylabel("Count")
        if lsl is not None:
            self.ax_hist.axvline(lsl, color="#d9534f", linestyle="--", label="LSL")
        if usl is not None:
            self.ax_hist.axvline(usl, color="#5cb85c", linestyle="--", label="USL")
        if lsl is not None or usl is not None:
            self.ax_hist.legend(loc="best")

        self.ax_run.plot(range(1, len(values) + 1), values.tolist(), marker="o", linewidth=1.2, color="#f0ad4e")
        self.ax_run.set_title("Run chart")
        self.ax_run.set_xlabel("Observation")
        self.ax_run.set_ylabel(self.column_var.get())
        self.ax_run.grid(alpha=0.25)
        self.figure.tight_layout(pad=2.0)
        self.canvas.draw_idle()

    def _update_preview(self):
        preview_df = self.filtered_df.head(100)
        cols = list(preview_df.columns)
        self.preview.delete(*self.preview.get_children())
        self.preview["columns"] = cols
        for col in cols:
            self.preview.heading(col, text=col)
            self.preview.column(col, width=110, stretch=True)
        for _, row in preview_df.iterrows():
            values = ["" if pd.isna(value) else str(value) for value in row.tolist()]
            self.preview.insert("", "end", values=values)
