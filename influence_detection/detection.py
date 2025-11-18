from typing import Dict, Iterable, List


def threshold(records: Iterable[Dict], t: float = 0.5) -> List[Dict]:
    out = []
    for r in records:
        s = float(r.get("score", 0.0))
        r["label_pred"] = 1 if s >= t else 0
        out.append(r)
    return out