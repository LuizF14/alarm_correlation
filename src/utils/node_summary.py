import polars as pl
import igraph as ig
from tqdm import tqdm

from src.repository.alarm_graph_repository import AlarmGraphRepository

def search_graph(graph_repo: AlarmGraphRepository) -> pl.DataFrame:
    node_counts = graph_repo.get_node_counts_by_physical_node()
    edge_counts = graph_repo.get_edge_counts_by_physical_node()

    all_node_ids = node_counts["node_id"].to_list()
    wcc_rows = []

    for physical_node_id in tqdm(all_node_ids, desc="Calculando WCC", unit="nó"):
        edge_generator = graph_repo.get_edges_by_physical_node(physical_node_id)

        G = ig.Graph.TupleList(edge_generator, directed=True)
        num_wcc = len(G.connected_components(mode="weak"))

        wcc_rows.append({"node_id": physical_node_id, "num_subgraphs": num_wcc})
        del G

    wcc_df = pl.DataFrame(wcc_rows)

    return (
        node_counts
        .join(edge_counts, on="node_id", how="left")
        .join(wcc_df, on="node_id", how="left")
        .fill_null(0)
        .sort("num_edges", descending=True)
    )
    
def add_stats_columns(base_df: pl.DataFrame) -> pl.DataFrame:
    return (
        base_df
        .with_columns(
            pl.when((pl.col("num_subgraphs") == 0) & (pl.col("num_nodes") > 0))
            .then(1)
            .otherwise(pl.col("num_subgraphs"))
            .alias("num_subgraphs")
        )
        .with_columns(
            (pl.col("num_nodes") / pl.col("num_subgraphs"))
            .fill_nan(1.0) # Garante o tratamento caso exista algum caso 0 / 0
            .alias("nodes_por_subgraph")
        )
        .with_columns(
            pl.when(pl.col("num_nodes") <= 1)
            .then(0.0) # Se só tem 1 alarme, não há conexões possíveis, logo a densidade é 0%
            .otherwise(
                (2.0 * pl.col("num_edges")) / (pl.col("num_nodes") * (pl.col("num_nodes") - 1))
            )
            # Trava de segurança para garantir que o valor fique estritamente entre 0.0 e 1.0
            .clip(0.0, 1.0)
            .alias("density")
        )
        .rename({
            "node_id": "Node ID",
            "num_nodes": "Total de Alarmes",
            "num_edges": "Total de Correlações",
            "num_subgraphs": "Total de Incidentes",
            "nodes_por_subgraph": "Média de Alarmes por Incidente",
            "density": "Densidade"
        })
    )
    
def extract_general_metrics(df: pl.DataFrame) -> pl.DataFrame:
    metrics = pl.DataFrame({
        "media_alarmes_por_incidente": [df["Média de Alarmes por Incidente"].mean()],
        "media_incidentes_por_node": [df["Total de Incidentes"].mean()],
        "densidade_media_nodes": [df["Densidade"].mean()]
    })
    return metrics
    
def node_summary(db_path: str):
    graph_repo = AlarmGraphRepository(db_path)
    df = search_graph(graph_repo)
    df = add_stats_columns(df) 
    general_metrics = extract_general_metrics(df)
    return df, general_metrics

    
    