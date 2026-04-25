import pandas as pd

from .connection_strategy import ConnectionStrategy

class TemporalThresholdPeriods(ConnectionStrategy):
    def __init__(self, threshold = pd.Timedelta(minutes=5)):
        self.threshold : pd.Timedelta = threshold

    def connect_nodes(self, graph, data, node_strategy):
        data = data.sort("First Occurrence")
        rows = data.to_dicts()

        j = 0
        n = len(rows)

        for i in range(n):
            a = rows[i]

            while j < n and rows[j]["First Occurrence"] <= a["Last Occurrence"] + self.threshold:
                j += 1

            for k in range(i + 1, j):
                b = rows[k]

                src = node_strategy.get_node(a)
                dst = node_strategy.get_node(b)

                graph.add_edge(src, dst)

        

