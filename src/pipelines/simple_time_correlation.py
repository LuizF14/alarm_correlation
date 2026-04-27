import os
import polars as pl

from datetime import timedelta

from .pipeline_base import PipelineBase

from ..preprocess.active_preprocessor import ActivePreprocessor

from ..graphing.graph_builder import GraphBuilder
from ..graphing.node_strategy.alert_instance_node import AlertInstanceNode
from ..graphing.connection_strategy.temporal_threshold_periods import TemporalThresholdPeriods

class SimpleTimeCorrelation(PipelineBase):
    @property
    def MODEL_NAME(self) -> str:
        return f"simple_time_correlation_{self.preprocessor.__class__.__name__.lower()}"
    
    @property
    def EDGES_PATH(self) -> str:
        return f"{self.BASE_PATH}/simple_time_correlation_{self.preprocessor.__class__.__name__.lower()}_edges/"

    def __init__(self, preprocessor=ActivePreprocessor, connection_strategy=TemporalThresholdPeriods):
        self.preprocessor = preprocessor()
        self.connection_strategy = connection_strategy

    def train(self, data, threshold=timedelta(minutes=5)):
        os.makedirs(self.EDGES_PATH, exist_ok=True)

        data = self.preprocessor.select_features(data)
        data = self.preprocessor.clean_data(data)
        data = self.preprocessor.select_nodes(data)

        data = data.collect()

        graph_builder = GraphBuilder(
            AlertInstanceNode(),
            self.connection_strategy(threshold)
        )

        for i, node_df in enumerate(data.partition_by("Node ID")):
            edges = graph_builder.build_edges(node_df)
            if edges:
                pl.DataFrame(edges, schema=["src", "dst"], orient='row')\
                  .write_parquet(f"{self.EDGES_PATH}/part_{i}.parquet")

            del node_df, edges