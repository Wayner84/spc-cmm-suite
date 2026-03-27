from __future__ import annotations

import pandas as pd


class SharedState:
    def __init__(self):
        self.compare_results = pd.DataFrame()
        self.compare_source_name = ""
