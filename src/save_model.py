import joblib
from config import *

def save_bundle(model, scaler, pca, name):
    joblib.dump({
        "model": model,
        "scaler": scaler,
        "pca": pca,
        "class_names": CLASS_NAMES
    }, SAVE_PATH)

    print("Saved ->", SAVE_PATH)