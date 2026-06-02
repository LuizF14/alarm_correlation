from datetime import timedelta
import polars as pl

class SlidingWindowClustering():
    name = "SlidingWindowClustering"

    def __init__(self, threshold_minutes: int = 5):
        self.threshold = timedelta(minutes=threshold_minutes)

    def prepare(self, node_df: pl.DataFrame) -> list[dict]:
        return (
            node_df
            .sort("Alert Occurrence")
            .select(["Alert ID", "Alert Occurrence"])
            .to_dicts()
        )

    def clusterize(self, rows: list[dict]) -> list[list[str]]:
        if not rows:
            return []

        incidents = []
        current = [rows[0]["Alert ID"]]

        for i in range(1, len(rows)):
            gap = rows[i]["Alert Occurrence"] - rows[i - 1]["Alert Occurrence"]
            if gap > self.threshold:
                incidents.append(current)
                current = []
            current.append(rows[i]["Alert ID"])

        incidents.append(current)
        return incidents