import polars as pl
from datetime import timedelta
from typing import Generator
from .correlation_strategy import CorrelationStrategy

class TemporalThresholdEvents(CorrelationStrategy):
    name = "TemporalThresholdEvents"

    def __init__(self, threshold: timedelta = timedelta(minutes=5)):
        self.threshold = threshold

    def prepare(self, node_df: pl.DataFrame) -> list[dict]:
        return (
            node_df
            .sort("Alert Occurrence")
            .select(["Alert ID", "Alert Occurrence"])  # só o necessário para o algoritmo
            .to_dicts()
        )

    def correlate(self, rows: list[dict]) -> Generator[dict, None, None]:
        n = len(rows)
        j = 0

        for i in range(n):
            a = rows[i]

            while j < n and rows[j]["Alert Occurrence"] <= a["Alert Occurrence"] + self.threshold:
                j += 1

            for k in range(i + 1, j):
                b = rows[k]
                yield {
                    "src_id": a["Alert ID"],
                    "dst_id": b["Alert ID"],
                    "algorithm": self.name,
                }