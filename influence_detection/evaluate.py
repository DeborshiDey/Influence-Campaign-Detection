from typing import Dict, Iterable, List


def compute_metrics(records: Iterable[Dict], label_key: str = "label", pred_key: str = "label_pred") -> Dict[str, float]:
    tp = fp = fn = tn = 0
    for r in records:
        y = int(r.get(label_key, 0))
        p = int(r.get(pred_key, 0))
        if y == 1 and p == 1:
            tp += 1
        elif y == 0 and p == 1:
            fp += 1
        elif y == 1 and p == 0:
            fn += 1
        else:
            tn += 1
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}