# config.py — App Configuration
This file holds all the settings for the application in one place. Instead of scattering magic numbers and file paths throughout the code, I put them all here as class attributes. The app loads them with `app.config.from_object(Config)` in `app.py`.
---
## Settings
### `SECRET_KEY`
```python
SECRET_KEY = os.environ.get('SECRET_KEY', 'csi-animal-detection-secret-2024')
```
Flask uses this to sign session cookies and flash messages. If someone gets hold of this key they could forge session tokens and log in as anyone.
The `os.environ.get(...)` pattern means: use the environment variable `SECRET_KEY` if it exists, otherwise fall back to the hardcoded default. **In production, always set this as an environment variable and never use the default.**
---
### `SQLALCHEMY_DATABASE_URI`
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'csi_detection.db')
```
Points to a SQLite database file in the project folder. SQLite is fine for a local/university project since it's just a single file with no server needed. If this were deployed for real, I'd switch this to PostgreSQL or MySQL.
`SQLALCHEMY_TRACK_MODIFICATIONS = False` turns off a Flask-SQLAlchemy feature that fires events on every model change. It's unnecessary overhead so I disabled it.
---
### `MODEL_PATH`
```python
MODEL_PATH = os.environ.get('MODEL_PATH', os.path.join(BASE_DIR, 'best_csi_model_ml.pkl'))
```
Where the trained ML model file is located. Defaults to looking for `best_csi_model_ml.pkl` in the same folder as the project. Can be overridden with an environment variable.
---
### `REFRESH_INTERVAL`
```python
REFRESH_INTERVAL = 5
```
How often the dashboard auto-refreshes in seconds. The JavaScript on the dashboard page uses this value (passed via the template) to set its polling interval.
---
### CSI Constants
```python
TIME_STEPS   = 500
SUBCARRIERS  = 52
NUM_CLASSES  = 5
```
These **must match exactly** what was used during training. The ESP32 samples CSI at 100 Hz for 5 seconds, giving 500 time steps. The Wi-Fi channel has 52 usable subcarriers. The total input size per sample is therefore `500 × 52 = 26,000` values.
If any of these numbers change, the model will refuse to run because the input shape won't match.
---
### `CLASS_NAMES`
```python
CLASS_NAMES = {
    0: 'Background',
    1: 'Person',
    2: 'Car',
    3: 'Dog',
    4: 'Cow',
}
```
Maps the model's integer output (0–4) to a human-readable label. The order here must match the label encoding used when the model was trained.
---
### `ALERT_CLASSES`
```python
ALERT_CLASSES = [1, 2, 3, 4]
```
Any predicted class in this list triggers an alert.That's everything except class 0 (Background). So a detection of a Person, Car, Dog, or Cow will all show the red ALERT badge and trigger the banner on the dashboard.
---
### `CLASS_COLORS`
```python
CLASS_COLORS = {
    'Background': '#6c757d',
    'Person':     '#0dcaf0',
    'Car':        '#ffc107',
    'Dog':        '#198754',
    'Cow':        '#dc3545',
}
```
Hex colour codes for each class used by the Chart.js charts on the dashboard and upload pages. Passed to the templates via `tojson` filter so the JavaScript can use them directly