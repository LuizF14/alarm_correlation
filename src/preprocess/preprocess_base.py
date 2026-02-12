from abc import ABC, abstractmethod

class PreprocessBase(ABC):
    @abstractmethod
    def select_features(self):
        pass