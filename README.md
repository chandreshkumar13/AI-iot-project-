# Project 37 — CSI Animal Crossing Detector
This is a student academic project that uses WiFi Channel State Information (CSI) to detect and classify animals and people crossing rural roads in real time. The system uses an ESP32 microcontroller to collect CSI data, which is then sent to a Flask web application where a trained XGBoost model makes predictions.
---
## Dataset
This project uses the **Animal Crossing WiFi CSI dataset**, published on Zenodo in August 2023 by Samuel Vieira Ducca. It was released alongside the research paper *"Detection and Classification of Animal Crossings on Roads Using IoT Based WiFi Sensing"*, submitted to IEEE LATINCOM 2023.
### What's in the Dataset
The dataset contains WiFi CSI amplitude data collected using ESP32 boards placed outdoors:
- Each sample = 500 CSI frames (5 seconds at 100 Hz)
- Each frame has 52 WiFi subcarriers
- Total features per sample: **26,000** (500 × 52)
- Only amplitude values are included (no phase)
Data was collected across four different outdoor environments to reduce environmental bias:
- Paved rural road
- Unpaved rural road
- Pasture
- Gravel road
Hardware setup: ESP32 boards at 70 cm height, 12 metres apart (transmitter to receiver).
### Preprocessing
Before the data was used for training, the following steps were applied:
1. Non-zero amplitude values were converted to decibel (dB) scale
2. Zero or null values were kept as zero (to avoid negative infinity from log conversion)
3. A running mean filter was applied to reduce noise
4. Zero-valued subcarriers were excluded from the running mean calculation
### Class Labels
| Label | Class |
|-------|-------|
| 0 | Background |
| 1 | Person |
| 2 | Car |
| 3 | Dog |
| 4 | Cow |
### Dataset Files
The dataset is split into two Parquet files:
| File | Size |
|------|------|
| `TRAIN.parquet` | 365.4 MB |
| `TEST.parquet` | 108.4 MB |
To load them:
```python
import pandas as pd
train_data = pd.read_parquet("TRAIN.parquet")
test_data  = pd.read_parquet("TEST.parquet")
```
Each row is one CSI sample with its class label.
### Citation
Samuel Vieira Ducca (2023). *Animal Crossing WiFi CSI*, Version 1.0.0. Zenodo.
DOI: [10.5281/zenodo.8266462](https://doi.org/10.5281/zenodo.8266462)
**License:** Creative Commons Attribution–NonCommercial–ShareAlike 4.0 (CC BY-NC-SA 4.0)
---
## How the App Works
1. The ESP32 collects CSI data at 100 Hz for 5 seconds — 26,000 values per sample
2. It sends that data via HTTP POST to `/api/esp32/data` along with its device token
3. The server verifies the token, runs the XGBoost model, and saves the result to the database
4. The dashboard polls `/api/latest` every 5 seconds and updates charts and the detection table automatically
5. If the predicted class is anything other than "Background", an alert is triggered
6. Users can also upload `.parquet` or `.csv` files to run batch predictions on recorded data
---
## Project File Structure
```
project37/
│
├── app.py                  ← Main application file, all routes, ML inference
├── models.py               ← Database table definitions
├── config.py               ← All settings and constants
├── extensions.py           ← Flask extensions (db, login, bcrypt)
├── requirements.txt        ← Python packages needed to run the project
│
├── auth/
│   ├── __init__.py         ← Creates the auth Blueprint
│   └── routes.py           ← Login, register, logout routes
│
├── static/
│   └── style.css           ← Green nature theme stylesheet
│
└── templates/
    ├── base.html           ← Shared layout (navbar, footer, flash messages)
    ├── index.html          ← Public landing page
    ├── login.html          ← Sign in form
    ├── register.html       ← Create account form
    ├── dashboard.html      ← Live detection dashboard with auto-refresh
    ├── history.html        ← Paginated detection log with class filter
    ├── upload.html         ← Batch file upload and inference results
    ├── device_token.html   ← View/copy/regenerate ESP32 device token
    ├── admin_users.html    ← Admin-only user management table
    └── error.html          ← 403 / 404 error page
```
---
## Documentation Files
Each file in the project has its own markdown explanation in this folder:
| File | Covers |
|------|--------|
| `app.md` | `app.py` — routes, inference pipeline, DB migration, model loading |
| `models.md` | `models.py` — User, Detection, DeviceToken database models |
| `config.md` | `config.py` — all settings, class names, CSI constants |
| `extensions.md` | `extensions.py` — why it exists and what each extension does |
| `requirements.md` | `requirements.txt` — every dependency explained |
| `auth.md` | `auth/__init__.py` + `auth/routes.py` — Blueprint, login, register, logout |
| `style_css.md` | `static/style.css` — theme variables, navbar, cards, animations |
| `template_base.md` | `templates/base.html` — shared layout, navbar logic, flash messages |
| `templates.md` | All other templates — index, login, register, dashboard, history, upload, token, admin, error |
---

*This repository is maintained for educational purposes only as part of a student academic project.*
