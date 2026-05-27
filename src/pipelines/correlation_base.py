from abc import ABC, abstractmethod
from src.repository.alarm_graph_repository import AlarmGraphRepository

class CorrelationBase(ABC):
    @abstractmethod
    def train(self, data, graph_repo: AlarmGraphRepository, window_width: int, verbose: bool):
        pass