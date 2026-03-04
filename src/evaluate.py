from sklearn.metrics import classification_report
from config import *

def evaluate(model, X_te, y_te):
    y_pred = model.predict(X_te)
    print(classification_report(y_te, y_pred,
          target_names=[CLASS_NAMES[i] for i in range(NUM_CLASSES)]))