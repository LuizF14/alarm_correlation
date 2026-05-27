import os

from src.pipelines.correlation_base import CorrelationBase
from src.graphing.temporal_threshold_events import TemporalThresholdEvents
from src.preprocess.history_preprocessor import HistoryPreprocessor
from src.preprocess.active_preprocessor import ActivePreprocessor
from src.repository.alarm_graph_repository import AlarmGraphRepository
from src.graphing.temporal_threshold_periods import TemporalThresholdPeriods

from tqdm import tqdm

class SimpleTimeCorrelationActive(CorrelationBase):
    @classmethod
    def common_preprocess(cls, data):
        data = ActivePreprocessor.select_features(data)
        data = ActivePreprocessor.clean_data(data)
        data = data.collect()

        partitions = data.partition_by("Node ID")
        return partitions
    
    @classmethod
    def internal_process(cls, partitions, graph_repo: AlarmGraphRepository, threshold_minutes=5, verbose=True):
        strategy = TemporalThresholdPeriods(threshold_minutes=threshold_minutes)
        for node_df in tqdm(partitions, desc="Processando nós", unit="nó", total=len(partitions), leave=False, disable=not verbose):
            physical_node_id = node_df["Node ID"][0]
            graph_repo.save_alarm_nodes(node_df, physical_node_id)

            rows = strategy.prepare(node_df)
            edge_gen = strategy.correlate(rows)
            graph_repo.save_temporal_edges(edge_gen, physical_node_id)
    
    @classmethod
    def train(cls, data, graph_repo: AlarmGraphRepository, threshold_minutes=5, verbose=True): 
        partitions = cls.common_preprocess(data)
        cls.internal_process(partitions, graph_repo, threshold_minutes=threshold_minutes, verbose=verbose)
        


class SimpleTimeCorrelationHistory(CorrelationBase):
    @classmethod
    def common_preprocess(cls, data):
        data = HistoryPreprocessor.select_features(data)
        data = HistoryPreprocessor.clean_data(data)
        data = data.collect()

        partitions = data.partition_by("Node ID")
        return partitions
    
    @classmethod
    def internal_process(cls, partitions, graph_repo: AlarmGraphRepository, threshold_minutes=5, verbose=True):
        strategy = TemporalThresholdEvents(threshold_minutes=threshold_minutes)
        for node_df in tqdm(partitions, desc="Processando nós", unit="nó", total=len(partitions), leave=False, disable=not verbose):
            physical_node_id = node_df["Node ID"][0]
            graph_repo.save_alarm_nodes(node_df, physical_node_id)

            rows = strategy.prepare(node_df)
            edge_gen = strategy.correlate(rows)
            graph_repo.save_temporal_edges(edge_gen, physical_node_id)
    
    @classmethod
    def train(cls, data, graph_repo: AlarmGraphRepository, threshold_minutes=5, verbose=True): 
        partitions = cls.common_preprocess(data)
        cls.internal_process(partitions, graph_repo, threshold_minutes=threshold_minutes, verbose=verbose)
        
        