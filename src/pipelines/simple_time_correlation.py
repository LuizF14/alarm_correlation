import os
import polars as pl

from datetime import timedelta

from .pipeline_base import PipelineBase

from ..preprocess.active_preprocessor import ActivePreprocessor

class SimpleTimeCorrelationActive(PipelineBase):
    def train(self, data, threshold=timedelta(minutes=5)):
        data = ActivePreprocessor.select_features(data)
        data = ActivePreprocessor.clean_data(data)
        # data = ActivePreprocessor.select_nodes(data)

        data = data.collect()

        for i, node_df in enumerate(data.partition_by("Node ID")):
            print(f"{node_df}")

        # graph_builder = GraphBuilder(
        #     AlertInstanceNode(),
        #     self.connection_strategy(threshold)
        # )

        # for i, node_df in enumerate(data.partition_by("Node ID")):
        #     edges = graph_builder.build_edges(node_df)
        #     if edges:
        #         pl.DataFrame(edges, schema=["src", "dst"], orient='row')\
        #           .write_parquet(f"{self.EDGES_PATH}/part_{i}.parquet")

        #     del node_df, edges