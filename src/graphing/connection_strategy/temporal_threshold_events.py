import polars as pl

from datetime import timedelta

from .connection_strategy import ConnectionStrategy

class TemporalThresholdEvents(ConnectionStrategy):
    def __init__(self, threshold = timedelta(minutes=5)):
        self.threshold = threshold

    def connect_nodes(self, data, node_map):
        data = data.sort("Alert Occurrence")

        times = data["Alert Occurrence"].to_list()
        ids = data["Alert ID"].to_list()

        n = len(times)
        j = 0

        edges = []

        for i in range(n):
            while j < n and times[j] <= times[i] + self.threshold:
                j += 1

            src = node_map[ids[i]]

            for k in range(i + 1, j):
                dst = node_map[ids[k]]
                edges.append((src, dst))

        return edges


        

