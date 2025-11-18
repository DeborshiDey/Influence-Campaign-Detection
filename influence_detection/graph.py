from typing import Dict, Iterable, List, Tuple


def build_edges(records: Iterable[Dict], src_key: str = "src", dst_key: str = "dst") -> List[Tuple[str, str]]:
    edges = []
    for r in records:
        s = r.get(src_key)
        d = r.get(dst_key)
        if s and d:
            edges.append((str(s), str(d)))
    return edges


def degree_centrality(edges: List[Tuple[str, str]]) -> Dict[str, int]:
    deg: Dict[str, int] = {}
    for s, d in edges:
        deg[s] = deg.get(s, 0) + 1
        deg[d] = deg.get(d, 0) + 1
    return deg