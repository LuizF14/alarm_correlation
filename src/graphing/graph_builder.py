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
    
    def build_forEach(self, df_list : list):
        graphs_list = []
        for df in df_list:
            graph = self.build(df)
            graphs_list.append(graph)

        return graphs_list