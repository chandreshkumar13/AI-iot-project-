import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'csi-animal-detection-secret-2024')
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'csi_detection.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Path to your trained keras model
    MODEL_PATH = os.environ.get('MODEL_PATH', os.path.join(BASE_DIR, 'best_csi_model_ml.pkl'))

    # Dashboard auto-refresh interval (seconds)
    REFRESH_INTERVAL = 5

    # CSI constants (must match training)
    TIME_STEPS   = 500
    SUBCARRIERS  = 52
    NUM_CLASSES  = 5

    CLASS_NAMES = {
        0: 'Background',
        1: 'Person',
        2: 'Car',
        3: 'Dog',
        4: 'Cow',
    }

    # Classes that trigger an alert (anything except background)
    ALERT_CLASSES = [1, 2, 3, 4]

    CLASS_COLORS = {
        'Background': '#6c757d',
        'Person':     '#0dcaf0',
        'Car':        '#ffc107',
        'Dog':        '#198754',
        'Cow':        '#dc3545',
    }
