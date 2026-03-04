import xgboost as xgb
import lightgbm as lgb
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import accuracy_score
from config import *

def train_and_compare(X_tr, y_tr, X_v, y_v, X_te, y_te):
    models = {
        "RandomForest": RandomForestClassifier(
            n_estimators=600, n_jobs=-1,
            class_weight="balanced",
            random_state=SEED
        ),
        "XGBoost": xgb.XGBClassifier(
            n_estimators=600,
            learning_rate=0.05,
            tree_method="hist",
            random_state=SEED
        ),
        "LightGBM": lgb.LGBMClassifier(
            n_estimators=600,
            learning_rate=0.05,
            class_weight="balanced",
            random_state=SEED
        ),
    }

    results = {}
    cv = StratifiedKFold(5, shuffle=True, random_state=SEED)

    for name, model in models.items():
        model.fit(X_tr, y_tr)
        val = accuracy_score(y_v, model.predict(X_v))
        test = accuracy_score(y_te, model.predict(X_te))
        results[name] = {"model": model, "val": val, "test": test}

    best = max(results, key=lambda x: results[x]["val"])
    return results, best