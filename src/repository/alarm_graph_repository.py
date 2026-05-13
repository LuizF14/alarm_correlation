from neo4j import GraphDatabase
import polars as pl

from ..graphing.correlation_strategy import CorrelationStrategy

class AlarmGraphRepository:
    def __init__(self, uri: str, user: str, password: str, database: str, batch_size: int = 1000):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database
        self.batch_size = batch_size

        with self.driver.session(database="system") as session:
            session.run(f"CREATE DATABASE {self.database} IF NOT EXISTS")
    
    def close(self):
        self.driver.close()

    def save_alarm_nodes(self, node_df: pl.DataFrame, physical_node_id: str):
        records = node_df.to_dicts()
        with self.driver.session(database=self.database) as session:
            session.execute_write(self._create_alarm_nodes, records, physical_node_id)
    
    @staticmethod
    def _create_alarm_nodes(tx, records: list[dict], physical_node_id: str):
        query = """
        UNWIND $records AS row
    
        WITH row WHERE row['Alert ID'] IS NOT NULL
        
        MERGE (a:Alarm {alert_id: row['Alert ID'], node_id: $node_id})
        
        SET a += row
        SET a.node_id = $node_id
        """
        tx.run(query, records=records, node_id=physical_node_id)

    def save_temporal_edges(self, node_df: pl.DataFrame, physical_node_id: str, strategy: CorrelationStrategy):
        rows = strategy.prepare(node_df)
        edge_generator = strategy.correlate(rows)

        with self.driver.session(database=self.database) as session:
            batch = []
            for edge in edge_generator:
                batch.append(edge)
                if len(batch) >= self.batch_size:
                    session.execute_write(self._create_edges, batch, physical_node_id)
                    batch.clear()

            if batch:  # flush do restante
                session.execute_write(self._create_edges, batch, physical_node_id)

    @staticmethod
    def _create_edges(tx, edges: list[dict], physical_node_id: str):
        query = """
        UNWIND $edges AS edge
        MATCH (src:Alarm {`Alert ID`: edge.src_id, node_id: $node_id})
        MATCH (dst:Alarm {`Alert ID`: edge.dst_id, node_id: $node_id})
        MERGE (src)-[r:CORRELATED]->(dst)
        SET r.algorithm = edge.algorithm
        """
        tx.run(query, edges=edges, node_id=physical_node_id)