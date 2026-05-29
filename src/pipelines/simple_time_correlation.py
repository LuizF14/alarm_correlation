import polars as pl

from src.pipelines.correlation_base import CorrelationBase
from src.graphing.temporal_threshold_events import TemporalThresholdEvents
from src.preprocess.history_preprocessor import HistoryPreprocessor
from src.preprocess.active_preprocessor import ActivePreprocessor
from src.repository.alarm_graph_repository import AlarmGraphRepository
from src.graphing.temporal_threshold_periods import TemporalThresholdPeriods

from tqdm import tqdm

class SimpleTimeCorrelationActive(CorrelationBase):
    @classmethod
    def common_preprocess_lazy(cls, data, parquet_dir: str):
        data = ActivePreprocessor.select_features(data)
        data = ActivePreprocessor.clean_data(data)
        data = data.collect()

        for i, node_df in enumerate(data.partition_by("Node ID")):
            node_df.write_parquet(f"{parquet_dir}/{i:04d}.parquet")
    
    @classmethod
    def internal_process_lazy(cls, parquet_files, graph_repo: AlarmGraphRepository, threshold_minutes=5, verbose=True):
        strategy = TemporalThresholdPeriods(threshold_minutes=threshold_minutes)

        for parquet_file in tqdm(parquet_files, desc="Processando nós", unit="nó", leave=False, disable=not verbose):
            node_df = pl.read_parquet(parquet_file)  # lê um, processa, descarta
            physical_node_id = node_df["Node ID"][0]

            graph_repo.save_alarm_nodes(node_df, physical_node_id)
            rows = strategy.prepare(node_df)
            edge_gen = strategy.correlate(rows)
            graph_repo.save_temporal_edges(edge_gen, physical_node_id)

            del node_df
    
    @staticmethod
    def train(data, graph_repo: AlarmGraphRepository, threshold_minutes=5, verbose=True): 
        data = ActivePreprocessor.select_features(data)
        data = ActivePreprocessor.clean_data(data)
        data = data.collect()

        partitions = data.partition_by("Node ID")
        
        strategy = TemporalThresholdPeriods(threshold_minutes=threshold_minutes)
        for node_df in tqdm(partitions, desc="Processando nós", unit="nó", total=len(partitions), leave=False, disable=not verbose):
            physical_node_id = node_df["Node ID"][0]
            graph_repo.save_alarm_nodes(node_df, physical_node_id)

            rows = strategy.prepare(node_df)
            edge_gen = strategy.correlate(rows)
            graph_repo.save_temporal_edges(edge_gen, physical_node_id)
        


class SimpleTimeCorrelationHistory(CorrelationBase):
    @classmethod
    def common_preprocess_lazy(cls, data, parquet_dir: str):
        data = HistoryPreprocessor.select_features(data)
        data = HistoryPreprocessor.clean_data(data)
        data = data.collect()

        for i, node_df in enumerate(data.partition_by("Node ID")):
            node_df.write_parquet(f"{parquet_dir}/{i:04d}.parquet")
    
    @classmethod
    def internal_process_lazy(cls, parquet_files, graph_repo: AlarmGraphRepository, threshold_minutes=5, verbose=True):
        strategy = TemporalThresholdEvents(threshold_minutes=threshold_minutes)

        for parquet_file in tqdm(parquet_files, desc="Processando nós", unit="nó", leave=False, disable=not verbose):
            node_df = pl.read_parquet(parquet_file)  # lê um, processa, descarta
            physical_node_id = node_df["Node ID"][0]

            graph_repo.save_alarm_nodes(node_df, physical_node_id)
            rows = strategy.prepare(node_df)
            edge_gen = strategy.correlate(rows)
            graph_repo.save_temporal_edges(edge_gen, physical_node_id)

            del node_df
    
    @staticmethod
    def train(data, graph_repo: AlarmGraphRepository, threshold_minutes=5, verbose=True): 
        data = HistoryPreprocessor.select_features(data)
        data = HistoryPreprocessor.clean_data(data)
        data = data.collect()

        partitions = data.partition_by("Node ID")
        
        strategy = TemporalThresholdEvents(threshold_minutes=threshold_minutes)
        for node_df in tqdm(partitions, desc="Processando nós", unit="nó", total=len(partitions), leave=False, disable=not verbose):
            physical_node_id = node_df["Node ID"][0]
            graph_repo.save_alarm_nodes(node_df, physical_node_id)

            rows = strategy.prepare(node_df)
            edge_gen = strategy.correlate(rows)
            graph_repo.save_temporal_edges(edge_gen, physical_node_id)
        