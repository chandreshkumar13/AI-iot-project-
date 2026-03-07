# app.py — The Main Application File
This is basically the heart of the whole project. Everything starts here. When you run the app, Python runs this file, which sets up Flask, connects all the pieces together, and registers every URL route.
---
## How the App is Created — `create_app()`
Instead of just writing `app = Flask(__name__)` at the top and dumping everything in one place, I used something called the **Application Factory pattern**. This just means the app is created inside a function (`create_app()`), which makes it easier to test and configure later.
```python
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
```
The extensions (database, login manager, bcrypt) are initialised here. They're defined separately in `extensions.py` so they can be imported anywhere without causing circular import errors.
---
## The `_det_query()` Helper
```python
def _det_query():
    if current_user.role == "admin":
        return Detection.query
    return Detection.query.filter(Detection.user_id == current_user.id)
```
This small helper function is used everywhere that needs to fetch detection records. The idea is simple — admins can see everything, but regular users can only see their own data. Rather than writing the same `if admin` check in every route, I put it in one place and just call `_det_query()` wherever I need it
---
## Routes (URLs)
### `/` — Home
Just renders the landing page. No login needed, no database queries.
### `/dashboard` — Main Dashboard
Requires login. Grabs the 10 most recent detections, total count, and alert count, then passes them to the dashboard template. Uses `_det_query()` so users only see their own data
### `/history` — Detection History
Requires login. Supports URL parameters for pagination (`?page=2`) and filtering by class (`?class=Dog`). Uses SQLAlchemy's `.paginate()` to split results into pages of 25.
### `/upload` — File Upload + Batch Inference
Requires login. Accepts `.parquet` or `.csv` files. Reads them into a pandas DataFrame, validates the column count (must be exactly `500 × 52 = 26,000` features), runs the ML model on every row, saves all the results to the database, and sends everything back to the template for display.
### `/api/esp32/data` — ESP32 Data Endpoint (POST only)
This is how the physical ESP32 device sends data to the server. No login required but it needs a **device token**. The token is checked against the database to figure out which user account the data belongs to. Then it runs inference on the CSI array and saves the result.
### `/api/latest` — JSON Feed for Dashboard
Requires login. Returns a JSON object with recent detections, stats, and chart data. This is what the dashboard JavaScript calls every 5 seconds to refresh the page without a full reload.
### `/admin/users` — User Management
Admin only. Fetches all users (except the `system` user) and displays them.
### `/admin/users/<id>/toggle` — Enable/Disable a User
Admin only. Flips the `is_active` field. Prevents admins from disabling themselves.
### `/admin/users/<id>/role` — Change a User's Role
Admin only. Accepts a JSON body with `{"role": "operator"}`. Only allows valid roles.
### `/settings/token` — View Device Token
Shows the logged-in user's ESP32 token.
### `/settings/token/regenerate` — Regenerate Token
Calls `token.regenerate()` which generates a new random token using `secrets.token_hex(32)`.
---
## Database Setup — `_migrate_db()` and `_seed_users()`
These two functions run every time the app starts (inside `with app.app_context()`).
**`_migrate_db()`** handles updating an existing database that might be missing columns. For example, when I added the `user_id` column to the `detections` table, existing databases didn't have it yet. This function checks if the column exists and adds it if not. It also assigns any unowned detections to the admin account
**`_seed_users()`** creates a default admin account (`admin` / `admin123`) if one doesn't already exist. This makes the app usable straight away without any manual setup
---
## Model Loading — `_load_model(path)`
This function tries to load the ML model from the path defined in `config.py`. It supports two formats:
- **`.pkl` file** — a scikit-learn/XGBoost/LightGBM pipeline saved with `joblib`. Gets loaded as a dictionary with keys like `model`, `scaler`, and `pca`
---
## Feature Extraction — `_extract_features(X)`
This is only used for the `.pkl` (scikit-learn) model path. Because tree-based models like XGBoost can't take raw 26,000-dimensional CSI arrays directly, I extract a set of statistical features first.
The features calculated per sample include:
- Per-subcarrier stats: mean, std, max, min,range, energy,skewness, kurtosis
- Per-timestep stats: mean, std, range
- Global stats: std, range, energy, skewness, kurtosis, subcarrier variance, timestep variance
- FFT frequency bands: the spectrum is split into 5 frequency bands and the mean magnitude is taken from each
- Delta (temporal difference) features: mean, std, max absolute change, energy of changes
All of these get stacked into one flat feature vector per sample
---
## Inference — `_run_inference(model, csi_raw)`
Takes a single CSI reading (flat numpy array) and returns `(predicted_class_index, confidence)`.
- For `.pkl` models: extracts features → scales → PCA → `predict_proba()`
The predicted class is the index with the highest probability (`argmax`), and the confidence is that probability value