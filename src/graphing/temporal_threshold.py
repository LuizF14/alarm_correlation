import networkx as nx
import pandas as pd

from .graphing_base import GraphingBase

class TemporalThreshold(GraphingBase):
    def __init__(self, threshold = pd.Timedelta(minutes=5)):
        self.threshold : pd.Timedelta = threshold
        
    def to_graph(self, data):
        graph = nx.DiGraph()

        data = self._prepare_data(data)
        self._add_alert_nodes(graph, data)
        self._add_temporal_edges(graph, data, "Alert ID")
        return graph
    
    def graph_by_key(self, data, key):
        graph = nx.DiGraph()

        data = self._prepare_data(data)
        graph.add_nodes_from(data[key].unique())

        self._add_temporal_edges(graph, data, key)
        return graph

    def _prepare_data(self, data):
        return data.sort_values("First Occurrence").reset_index(drop=True)
    
    def _add_alert_nodes(self, graph, data):
        for _, row in data.iterrows():
            attrs = row.to_dict()
            attrs.pop("Alert ID", None)

            graph.add_node(row["Alert ID"], **attrs)

    def _add_temporal_edges(self, graph, data, key):
        for i in range(len(data)):
            a = data.iloc[i]

            for j in range(i + 1, len(data)):
                b = data.iloc[j]

                if b["First Occurrence"] > a["Last Occurrence"] + self.threshold:
                    break

                graph.add_edge(a[key], b[key])

