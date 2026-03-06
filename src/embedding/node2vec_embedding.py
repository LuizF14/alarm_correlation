from pathlib import Path
from node2vec import Node2Vec
from gensim.models import Word2Vec
import numpy as np

from .embedding_base import EmbeddingBase

class Node2VecEmbedding(EmbeddingBase):
    def __init__(self, graph):
        self.model = None
        self.graph = graph
        self.nodes = list(graph.nodes())

    def embed(self, force_reload=False):
        model_path = Path("data/models/alarm_correlation_v1.model")

        if model_path.exists() and not force_reload:
            self.model = Word2Vec.load(model_path)
            return self.model

        node2vec = Node2Vec(self.graph, dimensions=64, walk_length=30, num_walks=200)
        self.model = node2vec.fit(window=10, min_count=1, batch_words=4)

        self.model.save(model_path)
        return self.model

    @property
    def embeddings(self):

        if self.model is None:
            raise RuntimeError("Model not trained. Call embed() first.")

        return np.array([
            self.model.wv[str(node)]
            for node in self.nodes
        ])