from pyvis.network import Network

def plot_graph(graph, filename):
    net = Network(
        height="700px",
        width="100%",
        directed=True,
        notebook=True
    )

    viz_graph = graph.copy()

    for n, data in viz_graph.nodes(data=True):
        data["First Occurrence"] = data["First Occurrence"].isoformat()
        data["Last Occurrence"] = data["Last Occurrence"].isoformat()

    net.from_nx(viz_graph)

    for node in net.nodes:
        data = graph.nodes[node["id"]]

        node["label"] = data["Alert Type"]
        node["title"] = f"Description: {data['Alert Description']}"

        match data['Alert Severity']:
            case 0:
                node['color'] =  "green"
            case 1:
                node['color'] =  "yellow"
            case 2:
                node['color'] =  "orange"
            case 3:
                node['color'] =  "red"
            case 4:
                node['color'] = "dark red" 

    net.force_atlas_2based(
        gravity=-50,
        central_gravity=0.01,
        spring_length=100,
        spring_strength=0.08,
        damping=0.4
    )

    net.write_html(f"visualization/pyvis/{filename}.html", open_browser=False)