from typing import Dict, Iterable, List


def length_feature(t: str) -> int:
    return len(t.split())


def extract_features(records: Iterable[Dict], field: str = "text") -> List[Dict]:
    out = []
    for r in records:
        t = str(r.get(field, ""))
        r["feat_length"] = length_feature(t)
        out.append(r)
    return out