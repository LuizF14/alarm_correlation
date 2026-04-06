from pyvis.network import Network
import networkx as nx

PALETTE = [
        "#E6194B", "#3CB44B", "#FFE119", "#4363D8", "#F58231", 
        "#911EB4", "#42D4F4", "#F032E6", "#BDEF16", "#FABEBE", 
        "#008080", "#E6BEFF", "#9A6324", "#FFFAC8", "#800000", 
        "#AAFFC3", "#808000", "#FFD8B1", "#000075", "#A9A9A9"
    ]

def plot_graph(graph, filename, label=""):
    net = Network(
        height="700px",
        width="100%",
        directed=True,
        notebook=True
    )

    viz_graph = graph.copy()

    components = list(nx.weakly_connected_components(viz_graph))

    node_colors = {}
    for i, component in enumerate(components):
        color = PALETTE[i % len(PALETTE)]
        for node in component:
            node_colors[node] = color

    for n, data in viz_graph.nodes(data=True):
        if data.get("First Occurrence", False) and data.get("Last Occurrence", False):
            data["First Occurrence"] = data["First Occurrence"].isoformat()
            data["Last Occurrence"] = data["Last Occurrence"].isoformat()

    net.from_nx(viz_graph)

    for node in net.nodes:
        node_id = node["id"]
        data = graph.nodes[node_id]

        if label == "":
            node["label"] = node_id
        else:
            node["label"] = data["Alert Type"]

        node['color'] = node_colors.get(node_id, "gray")

    net.force_atlas_2based(
        gravity=-30,           # Menos repulsão (nós não voam para longe)
        central_gravity=0.005, # Menos puxão para o centro
        spring_length=150,     # Aumenta a distância de repouso das arestas
        spring_strength=0.05,  # Deixa a "mola" mais frouxa
        damping=0.9            # Damping ALTO (0.9) faz o movimento parar quase instantaneamente
    )

    # Adicione isso antes do write_html
    # net.toggle_physics(False)

    net.write_html(f"visualization/pyvis/{filename}.html", open_browser=False)