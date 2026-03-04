#Source Code Explanation (src/)
This document explains the structure and working of the src/ directory used in the CSI-Based Animal & Object Detection (Machine Learning Pipeline).
The goal of this structure is to:
keep code modular and readable
separate data loading, feature extraction, training, and evaluation
make the trained model easy to reuse in Flask or deployment
---
#Directory Structure
src/
│
├── config.py
├── data_loader.py
├── features.py
├── preprocess.py
├── train.py
├── evaluate.py
├── save_model.py
└── main.py
Each file has one clear responsibility, following a clean ML pipeline design.
---
#config.py — Global Configuration
Purpose
Stores all constants and configuration values used across the project.
Why this file exists
Avoids hard-coding values in multiple files
Makes experiments reproducible
Easy to change paths, PCA size, or dataset shape in one place
Contains
Random seed
CSI signal dimensions
Class labels
Train/validation split
Dataset paths
Model save path
Example responsibilities
TIME_STEPS = 500
SUBCARRIERS = 52
CLASS_NAMES = {0: "Background", 1: "Person", ...}
---
#data_loader.py — Dataset Loading & Splitting
Purpose
Handles reading the dataset and preparing train/validation/test splits.
What it does
Loads TRAIN and TEST .parquet files
Automatically detects the label column
Separates features and labels
Applies stratified train-validation split
Why it’s important
Keeps I/O logic separate from ML logic
Makes it easy to swap datasets later
Output
Returns:
X_train, y_train, X_val, y_val, X_test, y_test
---
#feaures.py — Feature Engineering
Purpose
Extracs statistical, temporal, and frequency-domain features from raw CSI data.
Input
Raw SI samples shaped as:
(samples, TIME_STEPS × SUBCARRIERS)
Feature Categories
Subcarrier-wise statistics
Mean, std, min, max, range
Energy, skewnss, kurtosi
Time-series statistcs
Mean, standard deviation, range over time
Frequency-domain features
FFT magnitude
Energy in 5 requency bands
Why this matters
Raw CSI signals are noisy and high-dimensional.
Feature extraction:
reduces noise
improves ML model performance
converts signals into meaningful numeric descriptors
---
#preprocess.py — Scaling & Dimensionality Reduction
Purpose
Prepares extracted features for ML models.
Steps performed
Calls extract_features()
Applies StandardScaler
Applies PCA (100 components)
Why PCA is used
Reduces dimensionality
Speeds up training
Prevents overfitting
Retains most variance from original features
Output
Returns:
X_train_pca, X_val_pca, X_test_pca, scaler, pca
---
#train.py — Model Training & Comparison
Purpose
Trains and compares multiple machine learning models.
Models used
Random Forest
XGBoost
LightGBM
What happens here
Each model is trained on PCA-reduced features
Validation and test accuracy are computed
Best model is selected based on validation accuracy
Why validation accuracy matters
It ensures the model generalizes well and is not overfitting to training data.
Output
Dictionary of trained models
Name of the best performing model
---
#evaluate.py — Model Evaluation
Purpos
Provides detailed performance metrics for the final model.
Metrics generated
Precision
Recall
F1-Scor
Class-wise performance summary
Why this is important
Accuracy alone is misleading.
This report shows:
which classes are confused
how well each object is detected
---
#save_model.py — Model Serialization
Purpose
Saves the trained pipeline for deployment.
What is saved
Best ML model
StandardScaler
PCA object
Class names
File created
best_csi_model_ml.pkl
Why bundling is used
Ensures same preprocessing steps are applied during inference in Flask or API.
---
#main.py — Pipeline Entry Point
Purpose
Acts as the controller script that runs the entire ML pipeline.
Execution flow
Load Data
   ↓
Feature Extraction
   ↓
Scaling + PCA
   ↓
Model Training
   ↓
Evaluation
   ↓
Save Best Model
Why this design is clean
One command runs everything
Easy to debug
Easy to automate
✅ Summary
This src/ structure:
follows real ML engineering practices
is easy to understand for students
is suitable for GitHub, viva, and interviews
supports smooth transition to Flask deployment
