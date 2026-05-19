import os
from pathlib import Path
from datetime import datetime
import polars as pl

class AggregateResultsRepository:
    def __init__(self, filename: str):
        self.output_dir = Path("data/results/")
        path_obj = Path(filename)
        self.base_name = path_obj.stem
        self.extension = path_obj.suffix if path_obj.suffix else ".csv"
        
        # Garante que a pasta exista
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save(self, df: pl.DataFrame) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = self.output_dir / f"{self.base_name}_{timestamp}{self.extension}"
        
        df.write_csv(file_path)
        print(f"✅ Nova versão salva com sucesso em: {file_path}")

    def load(self, timestamp_str: str = None) -> pl.DataFrame:
        """
        Carrega o arquivo.
        :param timestamp_str: Opcional. Pode ser apenas a data '20260519' ou 
                              o timestamp completo '20260519_180730'.
                              Se omitido, busca a versão mais recente.
        """
        if timestamp_str:
            files = sorted(self.output_dir.glob(f"{self.base_name}_{timestamp_str}*{self.extension}"))
            if not files:
                raise FileNotFoundError(f"Nenhuma versão correspondente a '{timestamp_str}' foi encontrada.")
            return pl.read_csv(files[-1])
        
        files = sorted(self.output_dir.glob(f"{self.base_name}_*{self.extension}"))
        
        if not files:
            raise FileNotFoundError(f"Nenhuma versão de '{self.base_name}' foi encontrada em {self.output_dir}")
        
        most_recent_file = files[-1]
        print(f"📖 Carregando a versão mais recente encontrada: {most_recent_file.name}")
        return pl.read_csv(most_recent_file)