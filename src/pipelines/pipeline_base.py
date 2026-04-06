import pickle
import os
from abc import ABC, abstractmethod

class PipelineBase(ABC):
    @property
    @abstractmethod
    def MODEL_NAME(self) -> str:
        pass 
    
    BASE_PATH = "data/models/"
    def run(self, data, *args, force_reload=False, **kwargs):
        filename = self.MODEL_NAME
        if not filename.endswith(".pkl"):
            filename += ".pkl"

        filepath = self.BASE_PATH + filename
        if os.path.exists(filepath) and not force_reload:
            print(f"Arquivo '{filepath}' encontrado. Carregando...")
            return self.load(filename)
        else:
            print(f"Arquivo não encontrado. Iniciando treino...")
            self.train(data, *args, **kwargs)
            self.save(filename)         
            return self

    @abstractmethod
    def train(self, data):
        pass

    def save(self, filename):
        if not filename.endswith(".pkl"):
            filename += ".pkl"

        filepath = self.BASE_PATH + filename
            
        with open(filepath, "wb") as f:
            pickle.dump(self, f)
        print(f"Modelo salvo com sucesso em: {filepath}")

    def load(self, filename):
        if not filename.endswith(".pkl"):
            filename += ".pkl"

        filepath = self.BASE_PATH + filename
            
        with open(filepath, "rb") as f:
            obj = pickle.load(f)
            
        for key, value in obj.__dict__.items():
            setattr(self, key, value)

        return obj