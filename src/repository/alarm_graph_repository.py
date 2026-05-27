import os
import duckdb
import polars as pl
from itertools import islice

from ..graphing.correlation_strategy import CorrelationStrategy


class AlarmGraphRepository:
    def __init__(self, db_path: str, batch_size: int = 35_000_000):
        self.path = f"{os.getenv("VOLUMES_PATH")}{db_path}"
        self.con = duckdb.connect(self.path)
        self.batch_size = batch_size
        self._init_schema()

    def _init_schema(self):
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS alarm_nodes (
                alert_id    VARCHAR,
                incident    INTEGER,
                alert_type  VARCHAR,
                start_time  DATETIME,
                end_time    DATETIME,
                node_id     VARCHAR
            )
        """)
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS alarm_edges (
                src_id      VARCHAR,
                dst_id      VARCHAR,
                node_id     VARCHAR
            )
        """)
        # self.con.execute("""
        #     CREATE INDEX IF NOT EXISTS idx_edges_node_id ON alarm_edges (node_id)
        # """)
        # self.con.execute("""
        #     CREATE INDEX IF NOT EXISTS idx_nodes_alert_id ON alarm_nodes (alert_id)
        # """)

    def close(self):
        self.con.close()

    def save_alarm_nodes(self, node_df: pl.DataFrame, physical_node_id: str):
        if "First Occurrence" in node_df.columns:
            start_time = node_df["First Occurrence"]
            end_time = node_df["Last Occurrence"]
        elif "Alert Occurrence" in node_df.columns:
            start_time = node_df["Alert Occurrence"]
            end_time = pl.Series("end_time", [None] * len(node_df), dtype=start_time.dtype)
        else:
            raise ValueError(f"Nenhuma coluna de tempo encontrada em: {node_df.columns}")

        df = pl.DataFrame({
            "alert_id":   node_df["Alert ID"].cast(pl.String),
            "node_id":    pl.Series("node_id", [physical_node_id] * len(node_df), dtype=pl.String),
            "alert_type": node_df["Alert Type"].cast(pl.String),
            "start_time": start_time,
            "end_time":   end_time
        })

        self.con.execute("""
            INSERT INTO alarm_nodes (alert_id, node_id, alert_type, start_time, end_time)
            SELECT alert_id, node_id, alert_type, start_time, end_time FROM df
        """)
        
    def save_temporal_edges(self, edge_gen: CorrelationStrategy, physical_node_id: str):
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
                    SELECT src_id, dst_id, node_id FROM chunk_df
                """)
            finally:
                del chunk
                del chunk_df

    def get_edges_by_physical_node(self, physical_node_id: str):
        relation = self.con.execute("""
            SELECT src_id, dst_id FROM alarm_edges WHERE node_id = ?
        """, [physical_node_id])
        
        while True:
            chunk = relation.fetchmany(self.batch_size)
            if not chunk:
                break
            yield from chunk

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
        
    def get_incident_counts_by_physical_node(self) -> pl.DataFrame:
        return self.con.execute("""
            SELECT 
                node_id, 
                COUNT(DISTINCT incident) as num_subgraphs
            FROM alarm_nodes
            GROUP BY node_id     
        """).pl()
    
    def preview_nodes(self, limit=20) -> pl.DataFrame:
        df_nodes = self.con.execute(f"SELECT * FROM alarm_nodes LIMIT {limit}").pl()
        return df_nodes
    
    def preview_edges(self, limit=20) -> pl.DataFrame:
        df_edges = self.con.execute(f"SELECT * FROM alarm_edges LIMIT {limit}").pl()
        return df_edges

    def write_down_incidents(self, incidents: list[tuple[int, list[str]]]):
        rows_incident_id = []
        rows_alert_id = []
        
        for incident_id, alert_ids in incidents:
            for alert_id in alert_ids:
                rows_incident_id.append(incident_id)
                rows_alert_id.append(alert_id)
        
        if not rows_alert_id:
            return
        
        df = pl.DataFrame({
            "incident_id": pl.Series(rows_incident_id, dtype=pl.Int32),
            "alert_id": pl.Series(rows_alert_id, dtype=pl.String),
        })
        
        self.con.execute("""
            UPDATE alarm_nodes
            SET incident = df.incident_id
            FROM df
            WHERE alarm_nodes.alert_id = df.alert_id
        """)
        
    def delete_db(self) -> bool:
        db_filename = self.con.execute("PRAGMA database_list").fetchall()[0][2]
        
        self.close()
        
        if db_filename and os.path.exists(db_filename):
            os.remove(db_filename)
        
            wal_file = f"{db_filename}.wal"
            if os.path.exists(wal_file):
                os.remove(wal_file)
                
            return True
        return False