import igraph as ig

class GraphBuilder():
    def __init__(self, node_strategy, connect_strategy):
        self.connect_strategy = connect_strategy
        self.node_strategy = node_strategy 

    def build_edges(self, data):
        node_map = self.node_strategy.create_node_map(data)
        edges = self.connect_strategy.connect_nodes(data, node_map)

        reverse_map = {v: k for k, v in node_map.items()}

        return [
            (reverse_map[src], reverse_map[dst])
            for src, dst in edges
        ]
