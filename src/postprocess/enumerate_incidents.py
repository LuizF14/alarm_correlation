import polars as pl
import igraph as ig
from tqdm import tqdm

from src.repository.alarm_graph_repository import AlarmGraphRepository

class EnumerateIncidents:
    @staticmethod
    def enumerate_data(graph_repo: AlarmGraphRepository):
        node_counts = graph_repo.get_node_counts_by_physical_node()
        all_node_ids = node_counts["node_id"].to_list()
        
        for physical_node_id in tqdm(all_node_ids, desc="Calculando WCC", unit="nó"):
            edge_generator = graph_repo.get_edges_by_physical_node(physical_node_id)

            G = ig.Graph.TupleList(edge_generator, directed=True)
            wcc = G.connected_components(mode="weak")
            
            incident_counter = 0
            for component in wcc:
                alert_ids = [G.vs[vertex_index]["name"] for vertex_index in component]
                
                graph_repo.write_down_incidents(
                    incident_id=incident_counter, 
                    alert_ids=alert_ids
                )
                
                incident_counter += 1
            
            del G