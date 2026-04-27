from pyvis.network import Network
import igraph as ig

PALETTE = [
    "#E6194B", "#3CB44B", "#FFE119", "#4363D8", "#F58231", 
    "#911EB4", "#42D4F4", "#F032E6", "#BDEF16", "#FABEBE", 
    "#008080", "#E6BEFF", "#9A6324", "#FFFAC8", "#800000", 
    "#AAFFC3", "#808000", "#FFD8B1", "#000075", "#A9A9A9"
]

def plot_graph(g: ig.Graph, filename, label=""):
    net = Network(
        height="700px",
        width="100%",
        directed=True,
        notebook=True
    )

    # Colore por componente fraco
    components = g.clusters(mode="weak")
    node_colors = {}
    for i, component in enumerate(components):
        color = PALETTE[i % len(PALETTE)]
        for node_idx in component:
            node_colors[node_idx] = color

    # Adiciona nós
    for v in g.vs:
        node_label = v["name"] if label == "" else v.get(label, v["name"])
        net.add_node(
            v.index,
            label=node_label,
            color=node_colors.get(v.index, "gray"),
        )

    # Adiciona arestas
    for e in g.es:
        net.add_edge(e.source, e.target)

    net.force_atlas_2based(
        gravity=-30,
        central_gravity=0.005,
        spring_length=150,
        spring_strength=0.05,
        damping=0.9
    )

    net.write_html(f"visualization/pyvis/{filename}.html", open_browser=False)