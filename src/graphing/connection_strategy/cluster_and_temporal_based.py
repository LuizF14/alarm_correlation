import pandas as pd

from .connection_strategy import ConnectionStrategy

class ClusterAndTemporalBased(ConnectionStrategy):
    def __init__(self, cluster_map, threshold = pd.Timedelta(minutes=5)):
        self.threshold : pd.Timedelta = threshold
        self.cluster_map : dict = cluster_map

    def connect_nodes(self, graph, data, node_strategy):
        data = data.sort_values("First Occurrence").reset_index(drop=True)

        for i in range(len(data)):
            a = data.iloc[i]
            
            for j in range(i+1,len(data)):
                b = data.iloc[j]

                time_condition = b["First Occurrence"] > a["Last Occurrence"] + self.threshold
                cluster_condition = self.cluster_map[a["Alert Type"]] != self.cluster_map[b["Alert Type"]]

                if time_condition:
                    break

                if cluster_condition:
                    continue

                src = node_strategy.get_node(a)
                dst = node_strategy.get_node(b)

                graph.add_edge(src, dst)
        return graph