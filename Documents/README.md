# Project 37 — CSI Animal Crossing Detector
## Documentation Overview

This folder contains a markdown file explaining every file in the project. Below is a quick summary of what each file does and where to find its documentation.

---

## Project File Structure

```
project37_v3_green/
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
## Documentation Files in This Folder

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
## How the App Works (Quick Summary)
1. The ESP32 sensor collects Wi-Fi CSI data at 100 Hz for 5 seconds (500 frames × 52 subcarriers = 26,000 values per sample).
2. It sends that data via HTTP POST to `/api/esp32/data` with its device token.
3. The server verifies the token, runs the XGBoost model on the data, and saves the predicted class + confidence to the database.
4. The dashboard polls `/api/latest` every 5 seconds and updates the charts and table automatically.
5. If the predicted class is anything other than "Background", an alert is triggered.
6. Users can also upload `.parquet` or `.csv` files to run batch predictions on recorded data.