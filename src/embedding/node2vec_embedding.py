from pathlib import Path
from node2vec import Node2Vec
from gensim.models import Word2Vec
import numpy as np

from .embedding_base import EmbeddingBase

class Node2VecEmbedding(EmbeddingBase):
    def embed(self, graph, force_reload=False):
        model_path = Path("data/models/alarm_correlation_v1.model")

        if model_path.exists() and not force_reload:
            return Word2Vec.load(model_path)

        node2vec = Node2Vec(graph, dimensions=64, walk_length=30, num_walks=200)
        model = node2vec.fit(window=10, min_count=1, batch_words=4)

        model.save(model_path)

        return model

    def get_all_embeddings(self, model, graph):
        nodes = list(graph.nodes())
        embeddings = np.array([model.wv[str(node)] for node in nodes])
        return nodes, embeddings