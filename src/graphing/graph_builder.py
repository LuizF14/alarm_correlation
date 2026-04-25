import networkx as nx

class GraphBuilder():
    def __init__(self, node_strategy, connect_strategy):
        self.connect_strategy = connect_strategy
        self.node_strategy = node_strategy 

    def build(self, data):
        graph = nx.DiGraph()

        self.node_strategy.initialize_nodes(graph, data)

        self.connect_strategy.connect_nodes(graph, data, self.node_strategy)

        return graph
    
    def build_forEach(self, groups: dict):
        return {
            node_id: self.build(node_df)
            for node_id, node_df in groups.items()
        }
