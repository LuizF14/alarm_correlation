import pandas as pd

from .connection_strategy import ConnectionStrategy

class TemporalThresholdEvents(ConnectionStrategy):
    def __init__(self, threshold = pd.Timedelta(minutes=5)):
        self.threshold : pd.Timedelta = threshold

    def connect_nodes(self, graph, data, node_strategy):
        data = data.sort("Alert Occurrence")

        times = data["Alert Occurrence"].to_numpy()
        ids = data["Alert ID"].to_numpy()

        n = len(times)
        j = 0

        for i in range(n):
            while j < n and times[j] <= times[i] + self.threshold:
                j += 1

            for k in range(i + 1, j):
                graph.add_edge(ids[i], ids[k])


        

