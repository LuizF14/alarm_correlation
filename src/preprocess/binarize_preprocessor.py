import polars as pl
import numpy as np
from dataclasses import dataclass

from src.repository.alarm_graph_repository import AlarmGraphRepository


@dataclass
class BinarizeResult:
    matrices:     list[np.ndarray]  # (T_i, N) por incidente
    var_names:    list[str]         # N alarm_types, ordem estável
    incident_ids: list[int]         # ID correspondente a cada matriz


class BinarizePreprocessor:

    def __init__(self, bin_size_seconds: int = 60, min_bins: int = 2):
        self.bin_size_seconds = bin_size_seconds
        self.min_bins = min_bins

    def filter_incidents(self, incidents, min_events=20, min_alert_types=2):
        filtered = []

        for df in incidents:
            if len(df) < min_events:
                continue

            n_types = (
                df
                .select(pl.col("alert_type").n_unique())
                .item()
            )

            if n_types < min_alert_types:
                continue

            filtered.append(df)

        return filtered
    
    def remove_stopword_types(self, incidents: list, min_idf: float = 0.7) -> list:
        total_incidents = len(incidents)

        presence = (
            pl.concat([df.select("alert_type").unique() for df in incidents])
            .group_by("alert_type")
            .len()
            .rename({"len": "doc_freq"})
            .with_columns(
                (pl.col("doc_freq") / total_incidents).alias("presence_pct")
            )
            .with_columns(
                (pl.lit(1) / pl.col("presence_pct")).log(base=2).alias("idf")
            )
        )

        stopwords = set(
            presence
            .filter(pl.col("idf") < min_idf)
            ["alert_type"]
            .to_list()
        )

        print(f"stopwords removidos ({len(stopwords)}): {stopwords}")

        return [
            df.filter(~pl.col("alert_type").is_in(stopwords))
            for df in incidents
        ]

    def binarize(self, incidents: list[pl.DataFrame]) -> BinarizeResult:
        var_names = sorted(
            pl.concat(incidents)["alert_type"]
            .drop_nulls()
            .unique()
            .to_list()
        )
        var_index = {v: i for i, v in enumerate(var_names)}
        N = len(var_names)

        matrices     = []
        incident_ids = []

        for incident in incidents:
            t_min = incident["start_time"].min()

            incident = incident.with_columns(
                ((pl.col("start_time") - t_min).dt.total_seconds() // self.bin_size_seconds)
                .cast(pl.Int32)
                .alias("bin_idx")
            )

            T = incident["bin_idx"].max() + 1

            if T < self.min_bins:
                continue

            mat = np.zeros((T, N), dtype=np.int32)
            bin_indices = incident["bin_idx"].to_numpy()
            col_indices = np.array([var_index[v] for v in incident["alert_type"].to_list()])
            mat[bin_indices, col_indices] = 1

            matrices.append(mat)
            incident_ids.append(incident["incident"][0])

        return BinarizeResult(
            matrices=matrices,
            var_names=var_names,
            incident_ids=incident_ids,
        )