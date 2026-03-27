from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


@dataclass
class CompareMapping:
    feature_column: str | None
    nominal_column: str | None
    measured_column: str | None
    tolerance_column: str | None


FEATURE_CANDIDATES = [
    "feature", "point", "name", "id", "dimension", "characteristic", "label", "item", "nom feature",
]
NOMINAL_CANDIDATES = [
    "nominal", "nom", "theoretical", "basic", "cad", "design", "target",
]
MEASURED_CANDIDATES = [
    "measured", "actual", "result", "value", "observed", "inspection result",
]
TOLERANCE_CANDIDATES = [
    "tolerance", "tol", "plusminus", "±tol", "total tolerance",
]
PLUS_CANDIDATES = ["plus tol", "upper tol", "utol", "+tol", "tol+"]
MINUS_CANDIDATES = ["minus tol", "lower tol", "ltol", "-tol", "tol-"]


def load_results_table(path: str) -> pd.DataFrame:
    lower = path.lower()
    if lower.endswith(".csv"):
        return pd.read_csv(path)
    if lower.endswith((".xlsx", ".xls", ".xlsm")):
        return pd.read_excel(path)
    if lower.endswith((".txt", ".tsv")):
        return _read_delimited_text(path)
    raise ValueError("Unsupported results file type. Use CSV, XLSX, TXT, or TSV.")


def _read_delimited_text(path: str) -> pd.DataFrame:
    raw = Path(path).read_text(encoding="utf-8", errors="replace")
    lines = [line for line in raw.splitlines() if line.strip()]
    if not lines:
        raise ValueError("Results file is empty.")

    sample = lines[0]
    if "\t" in sample:
        return pd.read_csv(path, sep="\t")
    if ";" in sample and sample.count(";") >= sample.count(","):
        return pd.read_csv(path, sep=";")
    return pd.read_csv(path)


def detect_mapping(df: pd.DataFrame) -> CompareMapping:
    cols = list(df.columns)
    feature_column = _find_by_name(cols, FEATURE_CANDIDATES, allow_non_numeric=True)
    nominal_column = _find_by_name(cols, NOMINAL_CANDIDATES, numeric_only=True, df=df)
    measured_column = _find_by_name(cols, MEASURED_CANDIDATES, numeric_only=True, df=df)
    tolerance_column = _find_by_name(cols, TOLERANCE_CANDIDATES, numeric_only=True, df=df)

    if nominal_column == measured_column:
        measured_column = _find_distinct_numeric(cols, df, exclude={nominal_column})

    return CompareMapping(
        feature_column=feature_column,
        nominal_column=nominal_column,
        measured_column=measured_column,
        tolerance_column=tolerance_column,
    )


def build_compare_dataframe(df: pd.DataFrame, mapping: CompareMapping) -> pd.DataFrame:
    if not mapping.nominal_column or not mapping.measured_column:
        raise ValueError("Could not detect both nominal and measured columns from the results table.")

    result = df.copy()
    result["Nominal"] = pd.to_numeric(result[mapping.nominal_column], errors="coerce")
    result["Measured"] = pd.to_numeric(result[mapping.measured_column], errors="coerce")
    result = result.loc[result["Nominal"].notna() & result["Measured"].notna()].copy()
    result["Deviation"] = result["Measured"] - result["Nominal"]
    result["AbsDeviation"] = result["Deviation"].abs()

    tol_series = _build_tolerance_series(result)
    if tol_series is not None:
        result["Tolerance"] = tol_series
        result["Status"] = result.apply(lambda row: "PASS" if row["AbsDeviation"] <= row["Tolerance"] else "FAIL", axis=1)
    elif mapping.tolerance_column and mapping.tolerance_column in result.columns:
        tol = pd.to_numeric(result[mapping.tolerance_column], errors="coerce").abs()
        result["Tolerance"] = tol
        result["Status"] = result.apply(
            lambda row: "PASS" if pd.notna(row["Tolerance"]) and row["AbsDeviation"] <= row["Tolerance"] else "", axis=1
        )
    else:
        result["Tolerance"] = ""
        result["Status"] = ""

    return result


def _build_tolerance_series(df: pd.DataFrame):
    plus_col = _find_by_name(df.columns, PLUS_CANDIDATES, numeric_only=True, df=df)
    minus_col = _find_by_name(df.columns, MINUS_CANDIDATES, numeric_only=True, df=df)
    if plus_col and minus_col:
        plus = pd.to_numeric(df[plus_col], errors="coerce").abs()
        minus = pd.to_numeric(df[minus_col], errors="coerce").abs()
        return plus.combine(minus, func=lambda a, b: max(a, b) if pd.notna(a) and pd.notna(b) else (a if pd.notna(a) else b))
    return None


def _find_by_name(columns: Iterable[str], candidates: list[str], allow_non_numeric: bool = False, numeric_only: bool = False, df: pd.DataFrame | None = None):
    for candidate in candidates:
        for column in columns:
            lowered = str(column).strip().lower()
            if candidate in lowered:
                if numeric_only and df is not None:
                    series = pd.to_numeric(df[column], errors="coerce")
                    if not series.notna().any():
                        continue
                if not allow_non_numeric and not numeric_only and df is not None:
                    series = pd.to_numeric(df[column], errors="coerce")
                    if not series.notna().any():
                        continue
                return column
    return None


def _find_distinct_numeric(columns: Iterable[str], df: pd.DataFrame, exclude: set[str | None]):
    for column in columns:
        if column in exclude:
            continue
        series = pd.to_numeric(df[column], errors="coerce")
        if series.notna().any():
            return column
    return None
