import networkx as nx
import pandas as pd

from .graphing_base import GraphingBase

class ClusterAndTemporalBased(GraphingBase):
    def to_graph(self, data, cluster_map, threshold: pd.Timedelta = pd.Timedelta(minutes=5)):
        graph = nx.DiGraph()

        data = data.sort_values("First Occurrence").reset_index()

        for _, row in data.iterrows():
            attrs = row.to_dict()
            attrs.pop("Alert ID", None)
            graph.add_node(row["Alert ID"], **attrs)

        for i in range(len(data)):
            a = data.iloc[i]
            
            for j in range(i+1,len(data)):
                b = data.iloc[j]

                time_condition = b["First Occurrence"] > a["Last Occurrence"] + threshold
                cluster_condition = cluster_map[a["Alert Type"]] != cluster_map[b["Alert Type"]]

                if time_condition:
                    break

                if cluster_condition:
                    continue

                graph.add_edge(a['Alert ID'], b['Alert ID'])
        return graph