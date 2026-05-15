import polars as pl
import igraph as ig
from tqdm import tqdm

from src.repository.alarm_graph_repository import AlarmGraphRepository

def node_summary(db_path: str) -> pl.DataFrame:
    graph_repo = AlarmGraphRepository(db_path)
    
    node_counts = graph_repo.get_node_counts_by_physical_node()
    edge_counts = graph_repo.get_edge_counts_by_physical_node()

    all_node_ids = node_counts["node_id"].to_list()
    wcc_rows = []

    for physical_node_id in tqdm(all_node_ids, desc="Calculando WCC", unit="nó"):
        edges = graph_repo.get_edges_by_physical_node(physical_node_id)

        if edges:
            G = ig.Graph.TupleList(edges, directed=True)
            num_wcc = len(G.connected_components(mode="weak"))
        else:
            num_wcc = 0

        wcc_rows.append({"node_id": physical_node_id, "num_subgraphs": num_wcc})

    wcc_df = pl.DataFrame(wcc_rows)

    return (
        node_counts
        .join(edge_counts, on="node_id", how="left")
        .join(wcc_df, on="node_id", how="left")
        .fill_null(0)
        .sort("num_edges", descending=True)
    )