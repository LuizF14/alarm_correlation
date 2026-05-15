import duckdb
import polars as pl
from tqdm.notebook import tqdm
from itertools import islice

from ..graphing.correlation_strategy import CorrelationStrategy


class AlarmGraphRepository:
    def __init__(self, db_path: str, batch_size: int = 50_000):
        self.con = duckdb.connect(db_path)
        self.batch_size = batch_size
        self._init_schema()

    def _init_schema(self):
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS alarm_nodes (
                alert_id    VARCHAR,
                node_id     VARCHAR,
                PRIMARY KEY (alert_id, node_id)
            )
        """)
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS alarm_edges (
                src_id      VARCHAR,
                dst_id      VARCHAR,
                node_id     VARCHAR,
                algorithm   VARCHAR
            )
        """)
        self.con.execute("""
            CREATE INDEX IF NOT EXISTS idx_edges_node_id ON alarm_edges (node_id)
        """)

    def close(self):
        self.con.close()

    def save_alarm_nodes(self, node_df: pl.DataFrame, physical_node_id: str):
        df = pl.DataFrame({
            "alert_id": node_df["Alert ID"],
            "node_id": physical_node_id,
        })

        self.con.execute("""
            INSERT OR IGNORE INTO alarm_nodes (alert_id, node_id)
            SELECT alert_id, node_id FROM df
        """)
        
    def save_temporal_edges(self, edge_gen: CorrelationStrategy, physical_node_id: str):
        with tqdm(desc=f"  edges [{physical_node_id}]", unit="edges", leave=False) as pbar:
            while True:
                chunk = list(islice(edge_gen, self.batch_size))
                if not chunk:
                    break
                try:
                    chunk_df = pl.DataFrame(chunk).with_columns(
                        pl.lit(physical_node_id).alias("node_id")
                    )
                    self.con.execute("""
                        INSERT INTO alarm_edges
                        SELECT src_id, dst_id, node_id, algorithm FROM chunk_df
                    """)
                    pbar.update(len(chunk))
                finally:
                    del chunk
                    del chunk_df

    def clear_algorithm(self, algorithm: str, db: str = "active"):
        deleted = self.con.execute("""
            DELETE FROM alarm_edges WHERE algorithm = ?
            RETURNING count(*) as n
        """, [algorithm]).fetchone()
        print(f"[{db}] algoritmo '{algorithm}': {deleted[0] if deleted else 0} arestas removidas")


    def get_edges_by_physical_node(self, physical_node_id: str, db: str = "active") -> list[tuple]:
        return self.con.execute("""
            SELECT src_id, dst_id FROM alarm_edges WHERE node_id = ?
        """, [physical_node_id]).fetchall()

    def get_nodes_by_physical_node(self, physical_node_id: str) -> pl.DataFrame:
        return self.con.execute("""
            SELECT alert_id, data
            FROM alarm_nodes
            WHERE node_id = ?
        """, [physical_node_id]).pl()
    
    def get_node_counts_by_physical_node(self) -> pl.DataFrame:
        return self.con.execute("""
            SELECT node_id, COUNT(*) as num_nodes
            FROM alarm_nodes
            GROUP BY node_id
        """).pl()
    
    def get_edge_counts_by_physical_node(self) -> pl.DataFrame:
        return self.con.execute("""
            SELECT node_id, COUNT(*) as num_edges
            FROM alarm_edges
            GROUP BY node_id
        """).pl()
