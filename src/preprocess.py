from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from features import extract_features
from config import *

def preprocess(X_tr, X_v, X_te):
    print("\nSTEP 2 -> FEATURE ENGINEERING")

    X_tr_f = extract_features(X_tr)
    X_v_f  = extract_features(X_v)
    X_te_f = extract_features(X_te)

    scaler = StandardScaler()
    X_tr_s = scaler.fit_transform(X_tr_f)
    X_v_s  = scaler.transform(X_v_f)
    X_te_s = scaler.transform(X_te_f)

    pca = PCA(n_components=100, random_state=SEED)
    X_tr_p = pca.fit_transform(X_tr_s)
    X_v_p  = pca.transform(X_v_s)
    X_te_p = pca.transform(X_te_s)

    return X_tr_p, X_v_p, X_te_p, scaler, pca