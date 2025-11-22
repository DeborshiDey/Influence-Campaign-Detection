from typing import Dict, Iterable, List, Any
import numpy as np

def length_feature(t: str) -> int:
    return len(t.split())

def extract_text_stats(text: str) -> Dict[str, float]:
    """Extract basic statistics from text."""
    words = text.split()
    return {
        "feat_num_words": len(words),
        "feat_avg_word_len": np.mean([len(w) for w in words]) if words else 0,
        "feat_num_chars": len(text)
    }

def extract_features(records: Iterable[Dict], field: str = "text", graph_features: Dict[str, Dict[str, float]] = None) -> List[Dict]:
    """
    Extract features from records.
    
    Args:
        records: List of data records.
        field: Name of the text field.
        graph_features: Dictionary mapping user IDs to their graph features (centrality, etc.).
    """
    out = []
    for r in records:
        t = str(r.get(field, ""))
        
        # Text stats
        stats = extract_text_stats(t)
        r.update(stats)
        
        # Graph features
        if graph_features:
            uid = str(r.get("src", "")) # Assuming 'src' is the user ID
            if uid in graph_features:
                r.update(graph_features[uid])
            else:
                # Default values if user not in graph (e.g. isolated)
                # We assume graph features are prefixed with 'feat_'
                first_val = next(iter(graph_features.values())) if graph_features else {}
                for k in first_val:
                    r[k] = 0.0
                    
        out.append(r)
    return out