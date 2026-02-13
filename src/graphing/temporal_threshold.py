import networkx as nx
import pandas as pd

from .graphing_base import GraphingBase

class TemporalThreshold(GraphingBase):
    def to_graph(self, data, threshold: pd.Timedelta = pd.Timedelta(minutes=5)):
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

                if b["First Occurrence"] > a["Last Occurrence"] + threshold:
                    break

                graph.add_edge(a['Alert ID'], b['Alert ID'])
        return graph
    
    def graph_by_key(self, data, key, threshold: pd.Timedelta = pd.Timedelta(minutes=5)):
        graph = nx.DiGraph()

        data = data.sort_values("First Occurrence").reset_index()
        unique_values = data[key].unique()

        graph.add_nodes_from(unique_values)

        for i in range(len(data)):
            a = data.iloc[i]
            
            for j in range(i+1,len(data)):
                b = data.iloc[j]

                if b["First Occurrence"] > a["Last Occurrence"] + threshold:
                    break

                graph.add_edge(a[key], b[key])
        return graph
