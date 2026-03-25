import pandas as pd
import networkx as nx

from .pipeline_base import PipelineBase

from ..preprocess.sequence_preprocessor import SequencePreprocessor

from ..graphing.graph_builder import GraphBuilder
from ..graphing.node_strategy.alert_instance_node import AlertInstanceNode
from ..graphing.connection_strategy.temporal_threshold import TemporalThreshold

class SimpleTimeCorrelation(PipelineBase):
    def __init__(self):
        self.data_by_node = None
        self.graphs_list = None
        self.embedding_model = None
        self.clusters = None

    def train(self, data):
        preprocessor = SequencePreprocessor()

        data = preprocessor.select_features(data)
        self.data_by_node = preprocessor.group_by(data)

        threshold = pd.Timedelta(minutes=5)
        graph_builder = GraphBuilder(AlertInstanceNode(), TemporalThreshold(threshold))
        self.graphs_list = graph_builder.build_forEach(self.data_by_node)

    def get_graph(self, node_name : str) -> nx.DiGraph:
        if self.data_by_node is None or self.graphs_list is None:
            raise RuntimeError("Model has not been trained yet")

        for i, node_df in enumerate(self.data_by_node):
            if node_name in node_df['Node Name'].values:
                return self.graphs_list[i]
            
        raise ValueError(f"Node '{node_name}' não encontrado na base de dados.")
