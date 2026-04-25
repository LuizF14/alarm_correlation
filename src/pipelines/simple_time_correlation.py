import pandas as pd
import networkx as nx

from .pipeline_base import PipelineBase

from ..preprocess.active_preprocessor import ActivePreprocessor

from ..graphing.graph_builder import GraphBuilder
from ..graphing.node_strategy.alert_instance_node import AlertInstanceNode
from ..graphing.connection_strategy.temporal_threshold_periods import TemporalThresholdPeriods

class SimpleTimeCorrelation(PipelineBase):
    @property
    def MODEL_NAME(self) -> str:
        return f"simple_time_correlation_{self.preprocessor.__class__.__name__.lower()}"

    def __init__(self, preprocessor = ActivePreprocessor, connection_strategy=TemporalThresholdPeriods):
        self.data_by_node = None
        self.graphs = None
        self.preprocessor = preprocessor()
        self.connection_strategy = connection_strategy

    def train(self, data, threshold=pd.Timedelta(minutes=5)):
        data = self.preprocessor.select_features(data)
        data = self.preprocessor.clean_data(data)
        self.data_by_node = self.preprocessor.group_by(data)

        graph_builder = GraphBuilder(AlertInstanceNode(), self.connection_strategy(threshold))
        self.graphs = graph_builder.build_forEach(self.data_by_node)


