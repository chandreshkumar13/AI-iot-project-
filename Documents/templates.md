# templates/ — Page Templates
These are the Jinja2 HTML templates for every page in the site. They all extend `base.html` and just fill in the `{% block content %}` section.
---
## index.html — Home / Landing Page
**Route:** `/` | **Login required:** No
The public-facing landing page. Explains the project to visitors before they log in. Has three feature cards:
- **ESP32 Sensing** — 100 Hz CSI across 52 subcarriers
- **XGBoost** — classifies 5 classes with 91% accuracy
- **Instant Alerts** — banner pops up on detection
At the bottom, the template checks `current_user.is_authenticated`:
- Logged in → shows a **Dashboard** button
- Not logged in → shows **Login** and **Register** button
No server-side data is passed to this template. It's completely static.
---
## login.html — Sign In Page
**Route:** `/auth/login` | **Login required:** No
A centred card with a username field, password field, "Remember me" checkbox, and a login button. Errors (wrong password, disabled account) appear as flash messages above the card.
There's a link at the bottom to the register page for new users.
The form submits via `POST` to `url_for('auth.login')`.
---
## register.html — Create Account Page
**Route:** `/auth/register` | **Login required:** No
Similar centred card layout. Has these fields:
- Username
- Email
- Role dropdown (Viewer / Operator / Admin)
- Password (min 6 characters)
- Confirm Password
The role dropdown includes the note "Admin (Requires approval)" to hint that picking admin doesn't automatically give you admin access — it will be downgraded unless an admin is already logged in.
The form submits via `POST` to the register route.
---
## dashboard.html — Live Monitoring Dashboard
**Route:** `/dashboard` | **Login required:** Yes
The most complex template in the project. Uses Chart.js and a JavaScript polling loop to keep itself updated every 5 seconds.
**Page sections:**
1. **Model warning banner** — shown if `model_loaded` is `False`. Displayed using `{% if not model_loaded %}`.
2. **Alert banner** — hidden by default (`d-none`). JavaScript shows it when a new alert comes in and hides it again after 8 seconds.
3. **4 stat cards** — Total Detections, Total Alerts, Last Seen, Sensor. The values are set by the initial server render but then updated live by JavaScript.
4. **Two charts side by side:**
   - Left: Doughnut chart showing class distribution
   - Right: Bar chart of recent confidence scores
5. **Live detection table** — 10 most recent detections. Alert rows are highlighted red.
**How JavaScript refresh works:**
```javascript
function refresh() {
  fetch('/api/latest')
    .then(r => r.json())
    .then(data => {
      // update stat cards
      // update both charts
      // update table rows
      // check for new alerts
    });
}
refresh();
setInterval(refresh, REFRESH_MS);  // every 5 seconds
```
The `CLASS_COLORS` from `config.py` are passed into the template as `{{ class_colors | tojson }}` and used to colour the chart bars/segments.
---
## history.html — Detection Log
**Route:** `/history` | **Login required:** Yes
A paginated table of all detections. Supports filtering by class using a dropdown at the top that auto-submits when changed.
The table shows: ID, full timestamp, class badge, confidence %, device ID, location, and alert badge.
Pagination is built with Jinja2 using `pagination.iter_pages()` which automatically adds `...` dots for long page ranges. 25 rows per page.
Alert rows are highlighted red. If there are no results at all, the table shows "No detections found."
---
## upload.html — Batch File Upload & Inference
**Route:** `/upload` | **Login required:** Yes
Has two sections — the upload form and (after submission) the results.
**Upload form:**
- File picker (`.parquet` or `.csv` only)
- Optional location label text input
- "Run Predictions" button (POST)
**Results section** (only shown if `results` is defined):
- 4 summary stat cards (rows processed, alerts, accuracy if label column present, filename)
- Horizontal bar chart of prediction distribution using Chart.js
- Scrollable table of row-by-row results
The results table uses inline CSS classes for visual coding:
- `row-alert` → red-tinted background for alert predictions
- `row-correct` → green left border (when true labels are present and prediction was right)
- `row-wrong` → red left border (wrong prediction)
- `conf-high` / `conf-med` / `conf-low` → green / yellow / red confidence text
The bar chart is only rendered after upload (`{% if results is defined and results %}`).
---
## device_token.html — ESP32 Token Management
**Route:** `/settings/token` | **Login required:** Yes
Three card sections on this page:
**Card 1 — Your token:**
Shows the token in a read-only monospace input with a copy button. The copy button uses `navigator.clipboard.writeText()` and briefly shows a tick icon to confirm the copy worked
**Card 2 — ESP32 code examples:**
Shows ready-to-use C++ code snippets the user can paste directly into their ESP32 Arduino sketch. Two options are shown — including the token in the JSON body or as an HTTP header.
**Card 3 — Regenerate (danger zone):**
Has a red-bordered card with a regenerate button. An `onsubmit` confirmation dialog (`confirm(...)`) pops up before the form is submitted to make sure the user understands their ESP32 will stop working until updated.
---
## admin_users.html — User Management
**Route:** `/admin/users` | **Login required:** Yes (Admin only)
A table of all users with columns: ID, username, email, role, created date, status, actions.
**Role column:** Shows a role dropdown for other users. For the current admin's own row, it shows a static badge instead (you can't change your own role).
Role changes are made instantly via JavaScript — no page reload needed:
```javascript
sel.addEventListener('change', function() {
  fetch(`/admin/users/${uid}/role`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({role})
  });
});
```
**Actions column:** Enable/Disable button for each user. For the admin's own row it just shows "You". Clicking the button calls `/admin/users/<id>/toggle` via `fetch()` and reloads the page on success.
---
## error.html — Error Page (403 / 404)
**Routes:** Triggered automatically by Flask error handlers
A centred layout with:
- Large red warning icon
- Big bold error code (e.g. `403`)
- Short description message (e.g. `"Access Forbidden"`)
- "Go Home" button back to the index
The same template handles both 403 and 404 errors. The `code` and `message` variables are passed in by the error handlers in `app.py`.