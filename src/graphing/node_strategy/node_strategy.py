
class NodeStrategy:
    def get_node(self, row):
        raise NotImplementedError()

    def initialize_nodes(self, graph, data):
        raise NotImplementedError()
