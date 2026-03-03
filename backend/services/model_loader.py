import tensorflow as tf
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.abspath(
    os.path.join(BASE_DIR, "..", "ML_model", "best_csi_model.keras")
)

print("Loading ML model from:", MODEL_PATH)

model = tf.keras.models.load_model(MODEL_PATH)

print("Model loaded successfully ✅")