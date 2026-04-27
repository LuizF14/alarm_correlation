import igraph as ig
import polars as pl
import glob

def analyze_amount(edges_path, raw_df):
    id_map = raw_df.select(
        pl.col("alhi_cd_id"),
        pl.col("alhi_cd_node_id"),
        pl.col("alhi_tx_node"),
    ).unique("alhi_cd_id")

    results = []

    for i, filepath in enumerate(glob.glob(f"{edges_path}/*.parquet")):
        print(f"{i} / ")
        edges = pl.read_parquet(filepath)

        edges = (
            edges
            .join(id_map.rename({"alhi_cd_id": "src", "alhi_cd_node_id": "src_node_id", "alhi_tx_node": "src_node_name"}), on="src", how="left")
            .join(id_map.rename({"alhi_cd_id": "dst", "alhi_cd_node_id": "dst_node_id", "alhi_tx_node": "dst_node_name"}), on="dst", how="left")
        )

        for node_id, node_edges in enumerate(edges.group_by("src_node_id")):
            node_id = node_id[0]
            node_name = node_edges["src_node_name"][0]

            src = node_edges["src"].to_list()
            dst = node_edges["dst"].to_list()

            all_nodes = list(set(src + dst))
            node_index = {n: i for i, n in enumerate(all_nodes)}

            g = ig.Graph(
                n=len(all_nodes),
                edges=[(node_index[s], node_index[d]) for s, d in zip(src, dst)],
                directed=True,
            )

            results.append({
                "node_id": node_id,
                "Node Name": node_name,
                "Qtd de Nós": g.vcount(),
                "Qtd de Arestas": g.ecount(),
                "Qtd de subgrafos": len(g.clusters(mode="weak")),
            })

        del edges

    return (
        pl.DataFrame(results)
        .sort("Qtd de Nós", descending=True)
    )