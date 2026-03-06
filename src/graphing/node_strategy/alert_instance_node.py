from src.graphing.node_strategy.node_strategy import NodeStrategy

class AlertInstanceNode(NodeStrategy):
    def get_node(self, row):
        return row["Alert ID"]

    def initialize_nodes(self, graph, data):
        for _, row in data.iterrows():
            attrs = row.to_dict()
            attrs.pop("Alert ID", None)

            graph.add_node(row["Alert ID"], **attrs)
