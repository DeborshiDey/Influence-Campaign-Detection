from typing import Dict, Iterable, List


def simple_score(records: Iterable[Dict]) -> List[Dict]:
    out = []
    for r in records:
        l = int(r.get("feat_length", 0))
        s = 1.0 if l > 20 else 0.0
        r["score"] = s
        out.append(r)
    return out