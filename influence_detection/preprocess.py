import re
from typing import Dict, Iterable, List


def normalize_text(t: str) -> str:
    s = t.strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def apply_normalization(records: Iterable[Dict], field: str = "text") -> List[Dict]:
    out = []
    for r in records:
        v = r.get(field, "")
        r[field] = normalize_text(str(v))
        out.append(r)
    return out


def deduplicate(records: Iterable[Dict], key: str = "id") -> List[Dict]:
    seen = set()
    out = []
    for r in records:
        k = r.get(key)
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
    return out