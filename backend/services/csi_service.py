from services.model_loader import model
import numpy as np

CLASS_LABELS = [
    "Class_0",
    "Class_1",
    "Class_2",
    "Class_3",
    "Class_4"
]

def analyze_signal(csi_matrix):
    data = np.array(csi_matrix)

    # Shape validation
    if data.shape != (500, 52):
        raise ValueError(f"Invalid CSI matrix shape {data.shape}. Expected (500, 52)")

    # Reshape for model
    data = data.reshape(1, 500, 52, 1)

    prediction = model.predict(data)

    probabilities = prediction[0]
    predicted_index = int(np.argmax(probabilities))
    confidence = float(np.max(probabilities))

    return {
        "predicted_class_index": predicted_index,
        "predicted_class_label": CLASS_LABELS[predicted_index],
        "confidence": round(confidence, 4),
        "all_probabilities": probabilities.tolist()
    }