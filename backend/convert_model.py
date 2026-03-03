import tensorflow as tf

# Load using TensorFlow SavedModel loader (NOT keras load_model)
loaded = tf.saved_model.load("ml_model")

# Convert to concrete function
infer = loaded.signatures["serving_default"]

# Wrap into a Keras Model
class WrappedModel(tf.keras.Model):
    def __init__(self, infer):
        super().__init__()
        self.infer = infer

    def call(self, inputs):
        return self.infer(inputs)

model = WrappedModel(infer)

# Save as .h5
model.save("best_csi_model.h5")

print("Model converted successfully to best_csi_model.h5 ✅")