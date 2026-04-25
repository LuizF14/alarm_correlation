import pandas as pd
import networkx as nx

from .pipeline_base import PipelineBase

from ..preprocess.active_preprocessor import SequencePreprocessor

from ..graphing.graph_builder import GraphBuilder
from ..graphing.node_strategy.alert_instance_node import AlertInstanceNode
from ..graphing.connection_strategy.temporal_threshold_periods import TemporalThreshold

from ..graphing.connection_strategy.cluster_and_temporal_based import ClusterAndTemporalBased

from ..embedding.node2vec_embedding import Node2VecEmbedding
from ..clustering.hdbscan_embedding_clustering import HDBScanEmbeddingClustering

class SimpleClusteringCorrelation(PipelineBase):
    @property
    def MODEL_NAME(self) -> str:
        return "simple_clustring_correlation"

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
        graph_builder = GraphBuilder(AlertInstanceNode(), TemporalThreshold(threshold))
        self.graphs = graph_builder.build_forEach(self.data_by_node)

        entire_graph = nx.compose_all(self.graphs.values())
        
        embeder = Node2VecEmbedding(entire_graph)
        self.embedding_model = embeder.embed(entire_graph)

        clusterer = HDBScanEmbeddingClustering()
        self.clusters = clusterer.clusterize(embeder.nodes, embeder.embeddings)

    def inference(self, data):
        preprocessor = SequencePreprocessor()

        data = preprocessor.select_features(data)
        data = preprocessor.clean_data(data)

        graph_builder = GraphBuilder(AlertInstanceNode(), ClusterAndTemporalBased(self.clusters, cluster_attribute="Alert ID"))
        return graph_builder.build(data)
    
    def test(self, data):
        preprocessor = SequencePreprocessor()

        data = preprocessor.select_features(data)
        data = preprocessor.clean_data(data)
        data_by_node = preprocessor.group_by(data)

        graph_builder = GraphBuilder(AlertInstanceNode(), ClusterAndTemporalBased(self.clusters, cluster_attribute="Alert ID"))
        return graph_builder.build_forEach(data_by_node)
        


