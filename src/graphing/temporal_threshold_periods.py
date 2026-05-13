from datetime import timedelta
from typing import Generator
from .correlation_strategy import CorrelationStrategy
import polars as pl

class TemporalThresholdPeriods(CorrelationStrategy):
    name = "TemporalThresholdPeriods"

    def __init__(self, threshold_minutes: int = 5):
        self.threshold = timedelta(minutes=threshold_minutes)

    def prepare(self, node_df: pl.DataFrame) -> list[dict]:
        return node_df.sort("First Occurrence").to_dicts()

    def correlate(self, rows: list[dict]) -> Generator[dict, None, None]:
        j = 0
        n = len(rows)

        for i in range(n):
            a = rows[i]

            while j < n and rows[j]["First Occurrence"] <= a["Last Occurrence"] + self.threshold:
                j += 1

            for k in range(i + 1, j):
                b = rows[k]
                yield {
                    "src_id": a["Alert ID"],
                    "dst_id": b["Alert ID"],
                    "algorithm": self.name,
                }