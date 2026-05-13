import polars as pl

class ParquetPreprocessor:
    @staticmethod
    def csv_to_parquet(csv_file, parquet_file):
        pl.scan_csv(csv_file).sink_parquet(parquet_file)