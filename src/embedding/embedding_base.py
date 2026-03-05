from abc import ABC, abstractmethod

class EmbeddingBase(ABC):
    @abstractmethod
    def embed(self, data):
        pass