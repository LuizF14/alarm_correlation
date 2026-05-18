from src.pipelines.correlation_base import CorrelationBase
from src.utils.node_summary import node_summary


class SlidingWindowSearch:
    @staticmethod
    def search(algorithm: CorrelationBase, data, window_widths: list):
        results = {}
        for w in window_widths:
            path = f"graph_{algorithm.__name__}_{w}"
            algorithm.train(data, w, path)
            
            summary, metrics = node_summary(path)
            results[w] = (summary, metrics)
        return results
            