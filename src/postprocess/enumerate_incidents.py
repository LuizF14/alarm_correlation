import polars as pl
import igraph as ig
from tqdm import tqdm

from src.repository.alarm_graph_repository import AlarmGraphRepository

class EnumerateIncidents:
    @staticmethod
    def enumerate_data(graph_repo: AlarmGraphRepository, verbose=True):
        node_counts = graph_repo.get_node_counts_by_physical_node()
        all_node_ids = node_counts["node_id"].to_list()
        
        for physical_node_id in tqdm(all_node_ids, desc="Calculando WCC", unit="nó", leave=False, disable=not verbose):
            edges = graph_repo.get_edges_by_physical_node(physical_node_id)
            G = ig.Graph.TupleList(edges, directed=True)
            wcc = G.connected_components(mode="weak")

            incidents = []
            for incident_counter, component in enumerate(wcc):
                alert_ids = [G.vs[v]["name"] for v in component]
                incidents.append((incident_counter, alert_ids))

            graph_repo.write_down_incidents(incidents)