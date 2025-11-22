import json
from pathlib import Path
from typing import Dict, List, Union

import pandas as pd


def load_json(path: Union[str, Path]) -> List[Dict]:
    """Legacy function to keep compatibility, wraps load_dataset."""
    df = load_dataset(path)
    return df.to_dict(orient="records")


def load_dataset(path: Union[str, Path]) -> pd.DataFrame:
    """
    Load dataset from JSON or CSV file.
    
    Args:
        path: Path to the data file.
        
    Returns:
        pd.DataFrame: Loaded data.
        
    Raises:
        ValueError: If file format is not supported or required columns are missing.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Data file not found: {path}")

    if p.suffix == ".json":
        # Try reading as records first, then as standard JSON
        try:
            df = pd.read_json(p, orient="records")
        except ValueError:
            df = pd.read_json(p)
    elif p.suffix == ".csv":
        df = pd.read_csv(p)
    else:
        raise ValueError(f"Unsupported file format: {p.suffix}")

    required_columns = ["id", "text"]
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df