import hdbscan
from sklearn.preprocessing import normalize

from .cluster_base import ClusterBase

class HDBScanEmbeddingClustering(ClusterBase):
    def clusterize(self, keys, embeddings):
        embeddings_norm = normalize(embeddings)
        clusterer = hdbscan.HDBSCAN(metric='euclidean')
        labels = clusterer.fit_predict(embeddings_norm)

        return {
            "Item Key": keys, 
            "Cluster ID": labels
        }