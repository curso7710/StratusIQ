"""Resource dependency graph visualization"""
import streamlit as st
import plotly.graph_objects as go
from typing import Dict
import networkx as nx


def render_graph_view(graph_data: Dict):
    """Render interactive dependency graph"""
    if not graph_data or not graph_data.get('nodes'):
        st.info("No graph data available")
        return
    
    st.header("Resource Dependency Graph")
    st.write("Visualize relationships between cloud resources")
    
    nodes = graph_data.get('nodes', [])
    edges = graph_data.get('edges', [])
    
    # Create networkx graph for layout
    G = nx.DiGraph()
    for node in nodes:
        G.add_node(node['id'])
    for edge in edges:
        G.add_edge(edge['source'], edge['target'])
    
    # Use spring layout
    try:
        pos = nx.spring_layout(G, k=2, iterations=50)
    except:
        pos = {node['id']: (i, 0) for i, node in enumerate(nodes)}
    
    # Create edge traces
    edge_traces = []
    for edge in edges:
        source = edge['source']
        target = edge['target']
        
        if source in pos and target in pos:
            x0, y0 = pos[source]
            x1, y1 = pos[target]
            
            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=1, color='#888'),
                hoverinfo='none',
                showlegend=False
            )
            edge_traces.append(edge_trace)
    
    # Create node trace
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    
    color_map = {
        'aws_instance': '#FF9900',
        'aws_security_group': '#FF4444',
        'aws_ebs_volume': '#4444FF',
        'aws_s3_bucket': '#44FF44',
        'aws_iam_role': '#FF44FF',
        'aws_eip': '#FFFF44',
    }
    
    for node in nodes:
        if node['id'] in pos:
            x, y = pos[node['id']]
            node_x.append(x)
            node_y.append(y)
            node_text.append(f"{node['type']}<br>{node['id']}")
            node_color.append(color_map.get(node['type'], '#888888'))
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=[n['id'].split('.')[-1][:15] for n in nodes if n['id'] in pos],
        textposition="top center",
        hovertext=node_text,
        marker=dict(
            size=20,
            color=node_color,
            line=dict(width=2, color='white')
        ),
        showlegend=False
    )
    
    # Create figure
    fig = go.Figure(data=edge_traces + [node_trace])
    
    fig.update_layout(
        title="Resource Dependency Graph",
        showlegend=False,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Legend
    st.subheader("Resource Types")
    cols = st.columns(3)
    resource_types = list(set(node['type'] for node in nodes))
    
    for i, rtype in enumerate(resource_types):
        with cols[i % 3]:
            color = color_map.get(rtype, '#888888')
            st.markdown(f"<span style='color:{color}'>●</span> {rtype}", unsafe_allow_html=True)
    
    # Statistics
    st.subheader("Graph Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Resources", len(nodes))
    with col2:
        st.metric("Total Connections", len(edges))
    with col3:
        avg_degree = len(edges) * 2 / len(nodes) if nodes else 0
        st.metric("Avg Connections", f"{avg_degree:.1f}")
