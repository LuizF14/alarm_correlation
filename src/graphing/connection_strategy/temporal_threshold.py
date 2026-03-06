import pandas as pd

from .connection_strategy import ConnectionStrategy

class TemporalThreshold(ConnectionStrategy):
    def __init__(self, threshold = pd.Timedelta(minutes=5)):
        self.threshold : pd.Timedelta = threshold

    def connect_nodes(self, graph, data, node_strategy):
        data = data.sort_values("First Occurrence").reset_index(drop=True)

        for i in range(len(data)):
            a = data.iloc[i]

            for j in range(i + 1, len(data)):
                b = data.iloc[j]

                if b["First Occurrence"] > a["Last Occurrence"] + self.threshold:
                    break

                src = node_strategy.get_node(a)
                dst = node_strategy.get_node(b)

                graph.add_edge(src, dst)

        

