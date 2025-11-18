import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List


def load_json(path: str) -> List[Dict]:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_csv(path: str) -> List[Dict]:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def head(records: Iterable[Dict], n: int = 5) -> List[Dict]:
    out = []
    for i, r in enumerate(records):
        if i >= n:
            break
        out.append(r)
    return out