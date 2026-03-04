import numpy as np
from scipy.stats import skew, kurtosis
from scipy.fft import fft
from config import *

def extract_features(X):
    N = X.shape[0]
    X_3d = X.reshape(N, TIME_STEPS, SUBCARRIERS)

    dc = X.mean(axis=1, keepdims=True)
    X_c = X - dc
    X_3d_c = X_c.reshape(N, TIME_STEPS, SUBCARRIERS)

    feats = []

    sc_mean = X_3d_c.mean(axis=1)
    sc_std  = X_3d_c.std(axis=1)
    sc_max  = X_3d_c.max(axis=1)
    sc_min  = X_3d_c.min(axis=1)
    sc_range = sc_max - sc_min
    sc_energy = (X_3d_c ** 2).mean(axis=1)
    sc_skew = np.array([skew(X_3d_c[i], axis=0) for i in range(N)])
    sc_kurt = np.array([kurtosis(X_3d_c[i], axis=0) for i in range(N)])

    feats += [sc_mean, sc_std, sc_max, sc_min, sc_range, sc_energy, sc_skew, sc_kurt]

    ts_mean = X_3d_c.mean(axis=2)
    ts_std  = X_3d_c.std(axis=2)
    ts_range = X_3d_c.max(axis=2) - X_3d_c.min(axis=2)

    feats += [ts_mean, ts_std, ts_range]

    fft_mag = np.abs(fft(X_3d_c, axis=1))[:, 1:TIME_STEPS//2, :]
    band = fft_mag.shape[1] // 5

    for i in range(5):
        feats.append(fft_mag[:, i*band:(i+1)*band, :].mean(axis=1))

    return np.hstack(feats).astype(np.float32)