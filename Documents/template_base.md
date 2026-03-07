# templates/base.html — Base Template
Every page in the site extends this template. It defines the overall page structure — the `<head>`, navbar, flash messages area, main content wrapper, and footer. Individual page templates just fill in the `{% block content %}` section.
---
## How Template Inheritance Works
At the top of every other template file you'll see:
```html
{% extends 'base.html' %}
```
This tells Jinja2 (Flask's template engine) to use `base.html` as a starting point and insert content into the defined blocks. The blocks in this file are:
| Block | What Goes In It |
|-------|----------------|
| `{% block title %}` | The page title shown in the browser tab |
| `{% block head %}` | Extra `<link>` or `<style>` tags specific to a page |
| `{% block content %}` | The main page content |
| `{% block scripts %}` | JavaScript that runs at the bottom of the page |
---
## External Libraries Loaded
These are loaded from CDNs so I don't have to host them myself:
- **Bootstrap 5.3.2** (CSS + JS bundle) — the UI framework for layout, buttons, forms, tables etc.
- **Bootstrap Icons 1.11.3** — icon font used throughout (`bi-speedometer2`, `bi-bell-fill`, etc.)
- **Chart.js 4.4.0** — the charting library used for the doughnut and bar charts on the dashboard
The project's own CSS is loaded after Bootstrap so it can override Bootstrap's defaults:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}"/>
```
---
## Navbar
The navbar is always visible at the top. Its content changes based on whether the user is logged in:
**If logged in**, the left side shows navigation links:
- Dashboard
- History
- Upload
- My ESP32 Token
- Users (only visible to admins)
The right side shows:
- A role badge (Admin / Operator / Viewer) — colour-coded
- The current username
- A red Logout button
**If not logged in**, the right side just shows Login and Register buttons.
The active nav link (the page you're currently on) is highlighted by checking `request.endpoint` against the route name:
```html
class="nav-link {% if request.endpoint=='dashboard' %}active{% endif %}"
```
---
## Flash Messages
Flask's flash system is used to show one-time notifications after actions (like "Login successful", "Invalid password", etc.).
```html
{% with messages = get_flashed_messages(with_categories=true) %}
  {% for category, message in messages %}
  <div class="alert alert-{{ category }} alert-dismissible fade show">
    {{ message }}
    ...
  </div>
  {% endfor %}
{% endwith %}
```
The category (e.g. `"success"`, `"danger"`, `"warning"`) maps directly to Bootstrap's alert colour classes (`alert-success` = green, `alert-danger` = red, etc.)
---
## Footer
Just a simple centred footer line:
```
CSI Animal Detection System © 2024 — Project 37
```
Has a top border and a subtle background gradient to separate it from the page content