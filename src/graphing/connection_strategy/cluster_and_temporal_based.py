import pandas as pd

from .connection_strategy import ConnectionStrategy

class ClusterAndTemporalBased(ConnectionStrategy):
    def __init__(self, cluster_map, threshold = pd.Timedelta(minutes=5), cluster_attribute = "Alert Type"):
        self.threshold : pd.Timedelta = threshold
        self.cluster_map : dict = cluster_map
        self.cluster_attribute = cluster_attribute

    def connect_nodes(self, graph, data, node_strategy):
        data = data.sort_values("First Occurrence").reset_index(drop=True)

        for i in range(len(data)):
            a = data.iloc[i]
            
            for j in range(i+1,len(data)):
                b = data.iloc[j]

                time_condition = b["First Occurrence"] > a["Last Occurrence"] + self.threshold

                cluster_a = self.cluster_map.get(a[self.cluster_attribute], -1)
                cluster_b = self.cluster_map.get(b[self.cluster_attribute], -1)

                cluster_condition = cluster_a != cluster_b
                # cluster_condition = self.cluster_map[a["Alert Type"]] != self.cluster_map[b["Alert Type"]]

                if time_condition:
                    break

                if cluster_condition:
                    continue

                src = node_strategy.get_node(a)
                dst = node_strategy.get_node(b)

                graph.add_edge(src, dst)
        return graph