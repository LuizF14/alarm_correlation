from abc import ABC, abstractmethod


class CorrelationBase(ABC):
    @abstractmethod
    def train(self, data, window_width: int, output_path: str):
        pass