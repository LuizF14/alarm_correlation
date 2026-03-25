from abc import ABC, abstractmethod

class PipelineBase(ABC):
    @abstractmethod
    def train(self):
        pass