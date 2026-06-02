from src.clustering.sliding_window_clustering import SlidingWindowClustering
from src.preprocess.history_preprocessor import HistoryPreprocessor
from src.repository.alarm_graph_repository import AlarmGraphRepository

from tqdm import tqdm
import polars as pl

class SimpleTimeClustering():
    @staticmethod
    def train(data, graph_repo: AlarmGraphRepository, threshold_minutes=5, verbose=True):
        data = HistoryPreprocessor.select_features(data)
        data = HistoryPreprocessor.clean_data(data)
        data = data.collect()

        partitions = data.partition_by("Node ID")

        strategy = SlidingWindowClustering(threshold_minutes=threshold_minutes)
        global_counter = 0

        for node_df in tqdm(partitions, desc="Processando nós", unit="nó", total=len(partitions), leave=True, disable=not verbose):
            physical_node_id = node_df["Node ID"][0]

            rows   = strategy.prepare(node_df)
            groups = strategy.clusterize(rows)

            incident_map = {
                alert_id: global_counter + i
                for i, group in enumerate(groups)
                for alert_id in group
            }
            global_counter += len(groups)

            node_df = node_df.with_columns(
                pl.col("Alert ID").cast(pl.String)
                .replace(incident_map)
                .cast(pl.Int32)
                .alias("incident")
            )

            graph_repo.save_alarm_nodes(node_df, physical_node_id)
            # graph_repo.save_alarm_nodes(node_df, physical_node_id)

            # rows = strategy.prepare(node_df)
            # groups = strategy.correlate(rows)

            # incidents = [(global_counter + i, alert_ids) for i, alert_ids in enumerate(groups)]
            # global_counter += len(groups)

            # graph_repo.write_down_incidents(incidents)