import time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from config import *

def load_data():
    print("\nSTEP 1 -> LOADING DATA")
    t0 = time.time()

    df_train = pd.read_parquet(TRAIN_PATH)
    df_test  = pd.read_parquet(TEST_PATH)

    label_col = next(
        (c for c in ["label","class","target","y"] if c in df_train.columns),
        df_train.columns[-1],
    )

    feat_cols = [c for c in df_train.columns if c != label_col]

    X_all = df_train[feat_cols].values.astype(np.float32)
    y_all = df_train[label_col].values.astype(np.int32)
    X_test = df_test[feat_cols].values.astype(np.float32)
    y_test = df_test[label_col].values.astype(np.int32)

    X_train, X_val, y_train, y_val = train_test_split(
        X_all, y_all,
        test_size=VAL_SPLIT,
        stratify=y_all,
        random_state=SEED
    )

    print(f"  Loaded in {time.time()-t0:.1f}s")
    print(f"  Train {X_train.shape} | Val {X_val.shape} | Test {X_test.shape}")

    return X_train, y_train, X_val, y_val, X_test, y_test