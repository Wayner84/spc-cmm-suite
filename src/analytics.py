from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd


@dataclass
class CapabilityResult:
    column: str
    count: int
    mean: float
    std_sample: float
    std_population: float
    minimum: float
    maximum: float
    cp: Optional[float]
    cpk: Optional[float]
    pp: Optional[float]
    ppk: Optional[float]


NUMERIC_METRICS = (
    ("n", "count"),
    ("mean", "mean"),
    ("std (sample)", "std_sample"),
    ("std (population)", "std_population"),
    ("min", "minimum"),
    ("max", "maximum"),
    ("Cp", "cp"),
    ("Cpk", "cpk"),
    ("Pp", "pp"),
    ("Ppk", "ppk"),
)


def load_dataset(path: str) -> pd.DataFrame:
    lower = path.lower()
    if lower.endswith(".csv"):
        return pd.read_csv(path)
    if lower.endswith((".xlsx", ".xlsm", ".xls")):
        return pd.read_excel(path)
    raise ValueError("Unsupported file type. Use CSV or XLSX.")



def coerce_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")



def apply_simple_filters(
    df: pd.DataFrame,
    target_column: Optional[str] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    drop_na_target: bool = False,
) -> pd.DataFrame:
    filtered = df.copy()
    if target_column and target_column in filtered.columns:
        numeric = coerce_numeric(filtered[target_column])
        if drop_na_target:
            filtered = filtered.loc[numeric.notna()].copy()
            numeric = coerce_numeric(filtered[target_column])
        if min_value is not None:
            filtered = filtered.loc[numeric >= min_value].copy()
            numeric = coerce_numeric(filtered[target_column])
        if max_value is not None:
            filtered = filtered.loc[numeric <= max_value].copy()
    return filtered



def calculate_capability(series: pd.Series, column: str, lsl: Optional[float], usl: Optional[float]) -> CapabilityResult:
    numeric = coerce_numeric(series).dropna()
    count = int(numeric.count())
    if count == 0:
        raise ValueError("No numeric values available after filtering.")

    mean = float(numeric.mean())
    minimum = float(numeric.min())
    maximum = float(numeric.max())
    std_population = float(numeric.std(ddof=0)) if count >= 1 else float("nan")
    std_sample = float(numeric.std(ddof=1)) if count >= 2 else float("nan")

    cp = cpk = pp = ppk = None
    if lsl is not None and usl is not None and usl > lsl:
        width = usl - lsl
        if std_sample and not np.isnan(std_sample) and std_sample > 0:
            cp = width / (6 * std_sample)
            cpk = min((usl - mean) / (3 * std_sample), (mean - lsl) / (3 * std_sample))
        if std_population and not np.isnan(std_population) and std_population > 0:
            pp = width / (6 * std_population)
            ppk = min((usl - mean) / (3 * std_population), (mean - lsl) / (3 * std_population))

    return CapabilityResult(
        column=column,
        count=count,
        mean=mean,
        std_sample=std_sample,
        std_population=std_population,
        minimum=minimum,
        maximum=maximum,
        cp=cp,
        cpk=cpk,
        pp=pp,
        ppk=ppk,
    )



def format_metric(value: Optional[float | int]) -> str:
    if value is None:
        return "—"
    if isinstance(value, int):
        return str(value)
    if np.isnan(value):
        return "—"
    return f"{value:,.4f}"
