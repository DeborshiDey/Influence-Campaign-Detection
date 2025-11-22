import joblib
import numpy as np
import pandas as pd
from typing import Dict, Iterable, List, Optional, Union
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

def prepare_features(records: Iterable[Dict]) -> pd.DataFrame:
    """Convert records to feature DataFrame."""
    df = pd.DataFrame(records)
    # Select only feature columns (starting with feat_)
    feat_cols = [c for c in df.columns if c.startswith("feat_")]
    if not feat_cols:
        return pd.DataFrame()
    return df[feat_cols]

def train_model(records: Iterable[Dict], save_path: Optional[Union[str, Path]] = None) -> Pipeline:
    """
    Train a Random Forest model.
    
    Args:
        records: List of training records.
        save_path: Path to save the trained model.
        
    Returns:
        Trained pipeline.
    """
    df = pd.DataFrame(records)
    X = prepare_features(records)
    y = df["label"] if "label" in df.columns else None
    
    if y is None:
        raise ValueError("Training data must contain 'label' field.")
        
    # Pipeline with imputation and classifier
    model = Pipeline([
        ('imputer', SimpleImputer(strategy='constant', fill_value=0)),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    model.fit(X, y)
    
    if save_path:
        joblib.dump(model, save_path)
        
    return model

def predict_model(model: Pipeline, records: Iterable[Dict]) -> List[Dict]:
    """
    Predict scores using trained model.
    
    Args:
        model: Trained pipeline.
        records: List of records to predict.
        
    Returns:
        List of records with 'score' field added.
    """
    X = prepare_features(records)
    if X.empty:
        # Fallback if no features found
        for r in records:
            r["score"] = 0.0
        return list(records)
        
    # Predict probabilities for class 1
    scores = model.predict_proba(X)[:, 1]
    
    out = []
    for r, s in zip(records, scores):
        r["score"] = float(s)
        out.append(r)
        
    return out

def load_model(path: Union[str, Path]) -> Pipeline:
    """Load a trained model."""
    return joblib.load(path)