import pandas as pd
import networkx as nx
from node2vec import Node2Vec

from .pipeline_base import PipelineBase

from ..preprocess.sequence_preprocessor import SequencePreprocessor
from ..graphing.temporal_threshold import TemporalThreshold
from ..embedding.node2vec_embedding import Node2VecEmbedding
from ..clustering.hdbscan_embedding_clustering import HDBScanEmbeddingClustering

class AlarmCorrelationV1(PipelineBase):
    def run(self, data):
        preprocessor = SequencePreprocessor()

        data = preprocessor.select_features(data)
        nodes_df = preprocessor.group_by(data)

        threshold = pd.Timedelta(minutes=5)
        graphs_list = []
        temporal_threshold = TemporalThreshold(threshold=threshold)
        for node_df in nodes_df:
            graph = temporal_threshold.graph_by_key(node_df, 'Alert Type')
            graphs_list.append(graph)

        entire_graph = nx.compose_all(graphs_list)
        
        embeder = Node2VecEmbedding()
        model = embeder.embed(entire_graph)
        nodes, embeddings = embeder.get_all_embeddings(model, entire_graph)

        clusterer = HDBScanEmbeddingClustering()
        clusters = clusterer.clusterize(nodes, embeddings)
        


