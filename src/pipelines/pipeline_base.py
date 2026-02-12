from abc import ABC, abstractmethod

class PipelineBase(ABC):
    @abstractmethod
    def run(self):
        pass