from abc import ABC, abstractmethod

class ClusterBase(ABC):
    def __init__(self, data):
        super().__init__()
        self.data = data
    
    @abstractmethod
    def clusterize(self):
        pass