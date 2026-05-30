import plotly.express as px

def plot_timeline_incidents_by_node(data):
    fig = px.scatter(
        data,
        x="start_time",
        y="node_id",                  # Cada linha será um Node Físico
        color="incident",             # Cada incidente ganha uma cor diferente
        hover_data=["alert_type", "alert_id"], # Passando o mouse você vê o tipo do alarme
        title="Disparos de Alarmes por Nó Físico e Incidente",
        labels={
            "start_time": "Linha do Tempo Global", 
            "node_id": "Nó Físico (Node ID)", 
            "incident": "ID do Incidente"
        },
    )

    fig.update_traces(
        marker=dict(size=14, opacity=0.75, line=dict(width=1, color='DarkSlateGrey'))
    )

    fig.update_layout(
        height=700,                      # Aumentado para acomodar os múltiplos nós no eixo Y
        showlegend=True,
        xaxis_title="Data e Hora do Disparo",
        yaxis_title="Nós Físicos Afetados",
        hovermode="closest",
        # Força o eixo Y a tratar os nós como categorias discretas bem espaçadas
        yaxis={'type': 'category'} 
    )

    fig.show()