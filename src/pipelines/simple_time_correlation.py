import os

from src.pipelines.correlation_base import CorrelationBase
from src.graphing.temporal_threshold_events import TemporalThresholdEvents
from src.preprocess.history_preprocessor import HistoryPreprocessor
from src.preprocess.active_preprocessor import ActivePreprocessor
from src.repository.alarm_graph_repository import AlarmGraphRepository
from src.graphing.temporal_threshold_periods import TemporalThresholdPeriods

from tqdm import tqdm

class SimpleTimeCorrelationActive(CorrelationBase):
    @staticmethod
    def train(data, threshold_minutes=5, db_path=os.getenv("ACTIVE_DB_PATH")): 
        graph_repo = AlarmGraphRepository(db_path)
        data = ActivePreprocessor.select_features(data)
        data = ActivePreprocessor.clean_data(data)

        data = data.collect()

        strategy = TemporalThresholdPeriods(threshold_minutes=threshold_minutes)
        try:
            partitions = data.partition_by("Node ID")
            for node_df in tqdm(partitions, desc="Processando nós", unit="nó", total=len(partitions)):
                physical_node_id = node_df["Node ID"][0]
                graph_repo.save_alarm_nodes(node_df, physical_node_id)

                rows = strategy.prepare(node_df)
                edge_gen = strategy.correlate(rows)
                graph_repo.save_temporal_edges(edge_gen, physical_node_id)

        finally:
            graph_repo.close()

class SimpleTimeCorrelationHistory(CorrelationBase):
    @staticmethod
    def train(data, threshold_minutes=5, db_path=os.getenv("HISTORY_DB_PATH")): 
        graph_repo = AlarmGraphRepository(db_path, batch_size=35_000_000)
        data = HistoryPreprocessor.select_features(data)
        data = HistoryPreprocessor.clean_data(data)

        data = data.collect()

        strategy = TemporalThresholdEvents(threshold_minutes=threshold_minutes)
        try:
            partitions = data.partition_by("Node ID")
            for node_df in tqdm(partitions, desc="Processando nós", unit="nó", total=len(partitions)):
                physical_node_id = node_df["Node ID"][0]
                graph_repo.save_alarm_nodes(node_df, physical_node_id)

                rows = strategy.prepare(node_df)
                edge_gen = strategy.correlate(rows)
                graph_repo.save_temporal_edges(edge_gen, physical_node_id)

        finally:
            graph_repo.close()
        