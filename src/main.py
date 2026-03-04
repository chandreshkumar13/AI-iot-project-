from data_loader import load_data
from preprocess import preprocess
from train import train_and_compare
from evaluate import evaluate
from save_model import save_bundle

def main():
    X_tr, y_tr, X_v, y_v, X_te, y_te = load_data()
    X_tr_p, X_v_p, X_te_p, scaler, pca = preprocess(X_tr, X_v, X_te)
    results, best = train_and_compare(X_tr_p, y_tr, X_v_p, y_v, X_te_p, y_te)
    model = results[best]["model"]
    evaluate(model, X_te_p, y_te)
    save_bundle(model, scaler, pca, best)

if __name__ == "__main__":
    main()