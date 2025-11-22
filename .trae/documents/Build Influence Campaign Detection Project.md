## Goals
- Implement a production-ready Influence Campaign Detection pipeline with clear modules, tests, and runnable CLI.
- Use the provided PDFs for guidance:
  - Summary PDF: scope, goals, success criteria
  - Framework PDF: architecture, module boundaries, data flow
  - AI Execution Guide: specs, algorithms, thresholds, evaluation standards
  - Complete Project PDF: code references and implementation examples
- Prepare portfolio outputs with the requested document roles.

## Architecture
- Core modules (Python 3.11):
  - `data`: ingestion, schema validation, source adapters (CSV/JSON/DB/API)
  - `preprocess`: text cleaning, language detection, tokenization, deduplication
  - `features`: content, user, network, temporal feature extractors
  - `graph`: interaction graph build + centrality/community metrics (NetworkX)
  - `models`: baseline (LogReg), tree-based (XGBoost/LightGBM), optional deep
  - `detection`: campaign scoring, anomaly detection, thresholding, explanations
  - `evaluate`: metrics (precision/recall/F1, ROC-AUC), error analysis, fairness
  - `cli`: commands `prepare`, `train`, `evaluate`, `infer`, `report`
  - `utils`: config, logging, caching, serialization
- Project structure:
  - `influence_detection/` (modules above)
  - `configs/` (YAML configs for data, features, models)
  - `scripts/` (helper runners)
  - `tests/` (pytest unit + integration)
  - `data/` (local samples + cache; excluded from VCS if sensitive)
  - `reports/` (auto-generated metrics/plots)
  - `portfolio/` (PDFs and index for deliverables)

## Dependencies
- `pandas`, `numpy`, `scikit-learn`, `networkx`, `xgboost` or `lightgbm`
- Text: `nltk` (stopwords, tokenization) or `spacy` (if heavier NLP needed)
- Utilities: `pyyaml`, `pydantic`, `typer` (CLI), `rich` (progress/logging)
- Testing: `pytest`, `pytest-cov`
- Optional: `mlflow` (experiment tracking), `matplotlib`/`seaborn` (plots)

## Implementation Phases
1. Baseline repo setup
   - `pyproject.toml` or `requirements.txt`, simple `logging` config, `configs/base.yaml`
   - Pre-commit (black/flake8/isort) optional; GitHub CI added later
2. Data ingestion + schema
   - Define `Record` schema (pydantic), loaders, and adapters
   - Small synthetic dataset + `tests/data/` to validate loaders
3. Preprocessing
   - Text normalization, language detection, tokenization, deduplication
   - Deterministic unit tests for each transform
4. Feature engineering
   - Content features (lexical richness, sentiment stub), user/account features
   - Network features from interaction graph; temporal burst features
5. Models
   - Baseline Logistic Regression + class weighting
   - Tree-based model with config-driven hyperparameters
   - Train/val split, cross-validation utility
6. Detection logic
   - Score aggregation, thresholds from AI Guide
   - Campaign grouping rules, explanation artifacts
7. Evaluation & reporting
   - Metrics table, confusion matrices, PR/ROC curves
   - Auto-save to `reports/` with run hash
8. CLI
   - `typer` commands for end-to-end runs and config override
   - `python -m influence_detection.cli prepare/train/evaluate/infer`
9. Portfolio packaging
   - `portfolio/` folder:
     - Main attachment: Complete Project PDF
     - Supporting docs: Framework PDF + AI Execution Guide
     - Quick reference: Summary PDF
   - `portfolio/index.txt` listing roles and links

## Mapping to PDFs
- Implementation starts with Summary PDF to confirm target outcomes
- Module boundaries and data flow follow Framework PDF
- Specs, thresholds, and metrics follow AI Execution Guide
- Code patterns reference Complete Project PDF; align naming/conventions

## Deliverables
- Runnable CLI, documented configs, reproducible reports
- Test coverage for data, preprocess, features, models, detection
- Portfolio folder containing the specified PDFs and index

## Milestones
- M1: Setup + data/preprocess + unit tests
- M2: Features + graph + baseline model
- M3: Detection + evaluation + reports
- M4: CLI polish + portfolio packaging

## Acceptance Criteria
- End-to-end run produces campaign scores and evaluation reports without errors
- Config-driven runs; unit tests pass; clear logs and artifacts
- Portfolio assets present and correctly labeled

## Notes
- If any library choice conflicts with the Complete Project PDF, we will revise to match its references.
- If sensitive data sources exist, they stay local (`data/`) and out of VCS by default.

Please confirm this plan to proceed with implementation and wiring up the portfolio folder using your PDFs already in the repo.