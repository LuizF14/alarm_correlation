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

    def filter(self, incidents: list[pl.DataFrame], min_alarms: int = 5) -> list[pl.DataFrame]:
        return [i for i in incidents if len(i) >= min_alarms]

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