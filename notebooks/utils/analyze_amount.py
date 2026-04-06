import pandas as pd
import networkx as nx

def get_node_mapping(data):
    return data[['acal_cd_node_id', 'acal_tx_node']].drop_duplicates().set_index('acal_cd_node_id')['acal_tx_node'].to_dict()

def analyze_amount(graphs, df):
    data = []
    node_mapping = get_node_mapping(df)

    for node_id, G in graphs.items():
        isolated_subgraphs = list(nx.weakly_connected_components(G))
        data.append({
            "node_id": node_id,  # Agora a chave do dict vira uma coluna
            "Node Name": node_mapping[node_id],
            "Qtd de Nós": G.number_of_nodes(),
            "Qtd de Arestas": G.number_of_edges(),
            "Qtd de subgrafos": len(isolated_subgraphs)
        })
    
    df = pd.DataFrame(data)
    # df.set_index("node_id", inplace=True)
    df = df.sort_values("Qtd de Nós", ascending=False)
    df = df.reset_index(drop=True)
    
    return df