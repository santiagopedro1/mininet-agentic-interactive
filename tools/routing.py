import networkx as nx
from agno.tools import tool
from topology import TOPOLOGY

def build_graph():
    G = nx.Graph()
    for node, neighbors in TOPOLOGY.items():
        for n in neighbors:
            G.add_edge(node, n)
    return G

@tool
def routing_tool(src: str, dst: str) -> dict:
    """Compute shortest path between two nodes."""
    G = build_graph()
    try:
        path = nx.shortest_path(G, src, dst)
        return {"path": path}
    except nx.NetworkXNoPath:
        return {"error": "No path found"}