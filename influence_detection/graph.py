from typing import Dict, Iterable, List, Tuple
import networkx as nx

def build_graph(records: Iterable[Dict], src_key: str = "src", dst_key: str = "dst") -> nx.DiGraph:
    """
    Build a directed graph from records.
    
    Args:
        records: List of data records.
        src_key: Key for source node.
        dst_key: Key for destination node.
        
    Returns:
        nx.DiGraph: Directed graph.
    """
    G = nx.DiGraph()
    for r in records:
        s = r.get(src_key)
        d = r.get(dst_key)
        if s and d:
            G.add_edge(str(s), str(d))
    return G

def calculate_graph_features(G: nx.DiGraph) -> Dict[str, Dict[str, float]]:
    """
    Calculate centrality and other graph features for each node.
    
    Args:
        G: NetworkX graph.
        
    Returns:
        Dict mapping node ID to a dictionary of features.
    """
    if len(G) == 0:
        return {}

    # Degree Centrality
    in_degree = nx.in_degree_centrality(G)
    out_degree = nx.out_degree_centrality(G)
    
    # PageRank
    try:
        pagerank = nx.pagerank(G)
    except nx.PowerIterationFailedConvergence:
        pagerank = {n: 0.0 for n in G.nodes()}

    # Community Detection (using simple connected components for now as Louvain requires extra lib)
    # For directed graph, we can use weakly connected components
    # But for features, let's stick to centrality for now.
    
    features = {}
    for node in G.nodes():
        features[node] = {
            "feat_in_degree": in_degree.get(node, 0.0),
            "feat_out_degree": out_degree.get(node, 0.0),
            "feat_pagerank": pagerank.get(node, 0.0)
        }
        
    return features