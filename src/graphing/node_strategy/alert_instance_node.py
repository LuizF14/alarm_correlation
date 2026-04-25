from src.graphing.node_strategy.node_strategy import NodeStrategy

class AlertInstanceNode(NodeStrategy):
    def get_node(self, row):
        return row["Alert ID"]

    def initialize_nodes(self, graph, data):
        node_ids = data["Alert ID"].to_list()

        attrs_df = data.drop("Alert ID")
        attrs_list = attrs_df.to_dicts()

        for node_id, attrs in zip(node_ids, attrs_list):
            graph.add_node(node_id, **attrs)

