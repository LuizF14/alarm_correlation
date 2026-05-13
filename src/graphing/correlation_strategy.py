from abc import ABC, abstractmethod
from typing import Generator
import polars as pl

class CorrelationStrategy(ABC):
    @abstractmethod
    def correlate(self, rows: list[dict]) -> Generator[dict, None, None]:
        """Yields edges um a um, sem acumular em memória."""
        ...

    @abstractmethod
    def prepare(self, node_df: pl.DataFrame) -> list[dict]:
        """Pré-processa o DataFrame antes da correlação."""
        ...