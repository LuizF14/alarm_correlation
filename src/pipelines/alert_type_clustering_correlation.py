import pandas as pd
import networkx as nx

from .pipeline_base import PipelineBase

from ..preprocess.sequence_preprocessor import SequencePreprocessor

from ..graphing.graph_builder import GraphBuilder
from ..graphing.node_strategy.alert_type_node import AlertTypeNode
from ..graphing.connection_strategy.temporal_threshold import TemporalThreshold

from ..graphing.node_strategy.alert_instance_node import AlertInstanceNode
from ..graphing.connection_strategy.cluster_and_temporal_based import ClusterAndTemporalBased

from ..embedding.node2vec_embedding import Node2VecEmbedding
from ..clustering.hdbscan_embedding_clustering import HDBScanEmbeddingClustering

class AlertTypeClusteringCorrelation(PipelineBase):
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
        graph_builder = GraphBuilder(AlertTypeNode(), TemporalThreshold(threshold))
        self.graphs_list = graph_builder.build_forEach(self.data_by_node)

        entire_graph = nx.compose_all(self.graphs_list)
        
        embeder = Node2VecEmbedding(entire_graph)
        self.embedding_model = embeder.embed(entire_graph)

        clusterer = HDBScanEmbeddingClustering()
        self.clusters = clusterer.clusterize(embeder.nodes, embeder.embeddings)

    def inference(self, data):
        preprocessor = SequencePreprocessor()

        data = preprocessor.select_features(data)

        graph_builder = GraphBuilder(AlertInstanceNode(), ClusterAndTemporalBased(self.clusters))
        return graph_builder.build(data)


        


