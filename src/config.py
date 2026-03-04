import numpy as np
from pathlib import Path

SEED = 42
TIME_STEPS = 500
SUBCARRIERS = 52
NUM_CLASSES = 5

CLASS_NAMES = {
    0: "Background",
    1: "Person",
    2: "Car",
    3: "Dog",
    4: "Cow",
}

VAL_SPLIT = 0.20

TRAIN_PATH = "/kaggle/input/datasets/dwigyadav9/dataset/TRAIN.parquet"
TEST_PATH  = "/kaggle/input/datasets/dwigyadav9/dataset/TEST.parquet"

if not Path(TRAIN_PATH).exists():
    TRAIN_PATH = "TRAIN.parquet"
    TEST_PATH  = "TEST.parquet"

SAVE_PATH = "best_csi_model_ml.pkl"

np.random.seed(SEED)