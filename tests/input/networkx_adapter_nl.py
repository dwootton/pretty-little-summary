ID = "networkx_adapter_nl"
TITLE = "NetworkX graph"
TAGS = ["networkx", "graph"]
REQUIRES = ['networkx']
DISPLAY_INPUT = "nx.Graph().add_edge('a', 'b')"


def build():
    import networkx as nx

    g = nx.Graph()
    g.add_edge("a", "b")
    return g


def expected(meta):
    return (
        f"A networkx graph with {meta['node_count']} nodes and {meta['edge_count']} edges."
    )
