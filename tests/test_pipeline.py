import json
import sys
import subprocess
from pathlib import Path
import pytest
import pandas as pd

def test_pipeline(tmp_path):
    # Setup
    data_path = tmp_path / "data.json"
    config_path = tmp_path / "config.json"
    
    data = [
        {"id": 1, "text": "short", "src": "u1", "dst": "u2", "label": 0},
        {"id": 2, "text": "long " * 25, "src": "u2", "dst": "u3", "label": 1}
    ]
    data_path.write_text(json.dumps(data))
    
    config = {
        "data": {"input_path": str(data_path), "text_field": "text"},
        "detection": {"score_threshold": 0.5}
    }
    config_path.write_text(json.dumps(config))
    
    # 1. Prepare
    cmd = [sys.executable, "-m", "influence_detection.cli", "prepare", "--config", str(config_path)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    assert p.returncode == 0
    
    # 2. Train
    cmd = [sys.executable, "-m", "influence_detection.cli", "train", "--config", str(config_path)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    assert p.returncode == 0
    assert "model_path" in p.stdout
    
    # 3. Infer
    cmd = [sys.executable, "-m", "influence_detection.cli", "infer", "--config", str(config_path), "--input", str(data_path)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    assert p.returncode == 0
    out = json.loads(p.stdout)
    assert out["status"] == "inferred"
    assert out["summary"]["count"] == 2
