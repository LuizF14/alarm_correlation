import hdbscan
from collections import defaultdict
from sklearn.preprocessing import normalize

from .cluster_base import ClusterBase

class HDBScanEmbeddingClustering(ClusterBase):
    def clusterize(self, keys, embeddings):
        embeddings_norm = normalize(embeddings)
        clusterer = hdbscan.HDBSCAN(metric='euclidean')
        labels = clusterer.fit_predict(embeddings_norm)

        cluster_map = defaultdict(lambda: -1)
        
        for key, label in zip(keys, labels):
            cluster_map[key] = int(label) 
        return cluster_map