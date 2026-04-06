import pandas as pd
import networkx as nx

from .pipeline_base import PipelineBase

from ..preprocess.sequence_preprocessor import SequencePreprocessor

from ..graphing.graph_builder import GraphBuilder
from ..graphing.node_strategy.alert_instance_node import AlertInstanceNode
from ..graphing.connection_strategy.temporal_threshold import TemporalThreshold

class SimpleTimeCorrelation(PipelineBase):
    @property
    def MODEL_NAME(self) -> str:
        return "simple_time_correlation"

    def __init__(self):
        self.data_by_node = None
        self.graphs = None

    def train(self, data, threshold=pd.Timedelta(minutes=5)):
        preprocessor = SequencePreprocessor()

        data = preprocessor.select_features(data)
        data = preprocessor.clean_data(data)
        self.data_by_node = preprocessor.group_by(data)

        graph_builder = GraphBuilder(AlertInstanceNode(), TemporalThreshold(threshold))
        self.graphs = graph_builder.build_forEach(self.data_by_node)

    @classmethod
    def search_timedeltas(cls, data):
        thresholds = [
            pd.Timedelta(minutes=1),
            pd.Timedelta(minutes=5),
            pd.Timedelta(minutes=10),
            pd.Timedelta(minutes=30)
        ]

        results = {}
        pipeline = SimpleTimeCorrelation()
        for t in thresholds:
            print(f"Testando threshold de: {t}")
            pipeline.train(data, threshold=t)

            graphs = pipeline.graphs

            total_subgraphs = 0
            total_nodes = 0
            total_edges = 0

            for g in graphs.values():
                total_subgraphs += sum(1 for _ in nx.weakly_connected_components(g))
                total_nodes += g.number_of_nodes()
                total_edges += g.number_of_edges()

            results[str(t)] = {
                "subgraphs": total_subgraphs,
                "nodes": total_nodes,
                "edges": total_edges
            }

        return results


