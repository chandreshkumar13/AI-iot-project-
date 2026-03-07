# requirements.txt — Project Dependencies
This file lists every Python package the project needs to run. You install them all at once with:
```bash
pip install -r requirements.txt
```
---
## Package Breakdown
### Web Framework

| Package | Version | What It Does |
|---------|---------|-------------|
| `Flask` | 3.0.0 | The web framework. Handles routing, templates, request/response. |
| `Flask-SQLAlchemy` | 3.1.1 | Connects Flask to SQLAlchemy so I can use the database with Python classes. |
| `Flask-Login` | 0.6.3 | Handles user sessions — `@login_required`, `current_user`, login/logout. |
| `Flask-Bcrypt` | 1.0.1 | Password hashing. Wraps the bcrypt algorithm for Flask. |
| `SQLAlchemy` | 2.0.23 | The actual ORM (Object Relational Mapper) that talks to the database. |
| `Werkzeug` | 3.0.1 | Flask's underlying toolkit. Handles HTTP utilities, routing internals, etc. |
### Data Processing
| Package | Version | What It Does |
|---------|---------|-------------|
| `numpy` | 1.26.2 | Used everywhere for fast array maths — reshaping CSI data, computing stats, normalisation. |
| `pandas` | ≥2.0.0 | Reads the uploaded `.parquet` and `.csv` files into DataFrames for batch processing. |
| `pyarrow` | ≥14.0.0 | Backend engine that pandas uses to read `.parquet` files. |
| `scipy` | ≥1.11.0 | Used in `_extract_features()` for computing skewness, kurtosis, and FFT on CSI data. |
### Machine Learning
| Package | Version | What It Does |
|---------|---------|-------------|
| `scikit-learn` | ≥1.3.0 | Used for the scaler (StandardScaler), PCA, and any sklearn-based classifiers in the `.pkl` model bundle. |
| `xgboost` | ≥2.0.0 | XGBoost classifier — the main model used for classifying CSI windows. |
| `lightgbm` | ≥4.0.0 | LightGBM classifier — an alternative gradient boosting model (supported but not the primary one). |
| `joblib` | ≥1.3.0 | Used to save and load the `.pkl` model bundle. `joblib.load()` reads the file back into memory. |
---