from src.graphing.node_strategy.node_strategy import NodeStrategy

class AlertInstanceNode(NodeStrategy):
    def get_node(self, row):
        return row["Alert ID"]

    def create_node_map(self, data):
        ids = data["Alert ID"].to_list()
        return {node_id: idx for idx, node_id in enumerate(ids)}

