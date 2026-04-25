import polars as pl

from .preprocess_base import PreprocessBase

class ParquetPreprocessor(PreprocessBase):
    def csv_to_parquet(self, csv_file, parquet_file):
        pl.scan_csv(csv_file).sink_parquet(parquet_file)