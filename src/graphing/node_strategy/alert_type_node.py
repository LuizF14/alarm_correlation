from src.graphing.node_strategy.node_strategy import NodeStrategy

class AlertTypeNode(NodeStrategy):
    def get_node(self, row):
        return row["Alert Type"]

    def initialize_nodes(self, graph, data):
        graph.add_nodes_from(data["Alert Type"].unique())
