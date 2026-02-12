from abc import ABC, abstractmethod

class GraphingBase(ABC):
    @abstractmethod
    def to_graph(self):
        pass