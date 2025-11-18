# Influence Campaign Detection

## Quick Start
- Create and activate a virtual environment:
  - `python -m venv .venv`
  - `.\.venv\Scripts\Activate.ps1`
- Install requirements:
  - `pip install -r requirements.txt`
- Run inference on a tiny sample:
  - `python -m influence_detection.cli infer --config configs/base.json --input data/sample.json`
- Other commands:
  - `python -m influence_detection.cli prepare --config configs/base.json`
  - `python -m influence_detection.cli train --config configs/base.json`
  - `python -m influence_detection.cli evaluate --config configs/base.json`

## Repository Layout
- `influence_detection/` modules for data, preprocessing, features, graph, models, detection, evaluation, CLI
- `configs/` configuration files
- `data/` sample dataset
- `reports/` run artifacts
- `tests/` unit tests
- `portfolio/` document mapping

## Example Output
- The infer command prints a JSON payload with basic results for the input file.