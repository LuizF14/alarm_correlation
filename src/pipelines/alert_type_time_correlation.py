import pandas as pd
import networkx as nx

from .pipeline_base import PipelineBase

from ..preprocess.active_preprocessor import SequencePreprocessor

from ..graphing.graph_builder import GraphBuilder
from ..graphing.node_strategy.alert_type_node import AlertTypeNode
from ..graphing.connection_strategy.temporal_threshold_periods import TemporalThreshold

class AlertTypeTimeCorrelation(PipelineBase):
    @property
    def MODEL_NAME(self) -> str:
        return "alert_type_time_correlation"
    
    def __init__(self):
        self.data_by_node = None
        self.graphs = None
        self.embedding_model = None
        self.clusters = None

    def train(self, data):
        preprocessor = SequencePreprocessor()

        data = preprocessor.select_features(data)
        data = preprocessor.clean_data(data)
        self.data_by_node = preprocessor.group_by(data)

        threshold = pd.Timedelta(minutes=5)
        graph_builder = GraphBuilder(AlertTypeNode(), TemporalThreshold(threshold))
        self.graphs = graph_builder.build_forEach(self.data_by_node)