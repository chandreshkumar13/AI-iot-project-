# models.py — Database Models
This file defines the three database tables used in the project. I'm using **Flask-SQLAlchemy**, which lets me define tables as Python classes instead of writing raw SQL. Each class is a table, and each class attribute is a column
---
## User
```python
class User(UserMixin, db.Model):
    __tablename__ = 'users'
```
This stores all the registered accounts. `UserMixin` is from Flask-Login — it adds the methods Flask-Login needs (like `is_authenticated`, `is_active`, `get_id()`) so I don't have to write them myself
| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer | Primary key, auto-increments |
| `username` | String(80) | Must be unique, case-sensitive |
| `email` | String(120) | Must be unique |
| `password_hash` | String(256) | Bcrypt hash — never the plain password |
| `role` | String(20) | One of: `admin`, `operator`, `viewer`, `system` |
| `created_at` | DateTime | Set to current UTC time on creation |
| `is_active` | Boolean | `True` by default. Admins can set this to `False` to block login |
The `detections` relationship at the bottom links each user to their detection records. The `backref='owner'` means you can do `detection.owner` to get back to the user.
---
## Detection
```python
class Detection(db.Model):
    __tablename__ = 'detections'
```
Every time the ML model makes a prediction (whether from the ESP32 or a file upload), one row is saved here.
| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer | Primary key |
| `timestamp` | DateTime | When the detection was made (UTC) |
| `predicted_class` | Integer | The class index (0–4) |
| `class_name` | String(50) | The readable name e.g. `"Car"` |
| `confidence` | Float | Probability from the model (0.0 to 1.0) |
| `alert_triggered` | Boolean | `True` if the class is not Background |
| `device_id` | String(50) | Which device sent the data (e.g. `"ESP32-01"` or `"File-Upload"`) |
| `location` | String(100) | Location label set by the ESP32 or the upload form |
| `user_id` | Integer (FK) | Links to `users.id` — who owns this detection |
The `user_id` column has `nullable=True` — this was added to keep backwards compatibility with any old database rows that existed before I added per-user data scoping
**`to_dict()`** converts a Detection into a plain Python dictionary. This is used when the dashboard requests JSON from `/api/latest` — Flask's `jsonify()` can't serialise SQLAlchemy objects directly, so I convert them first.
---
## DeviceToken
```python
class DeviceToken(db.Model):
    __tablename__ = 'device_tokens'
```
Each user gets exactly one device token. This token is what the ESP32 includes in its HTTP requests so the server knows which user the data belongs to.
| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer | Primary key |
| `token` | String(64) | A 64-character random hex string, unique |
| `user_id` | Integer (FK) | Links to `users.id`, also unique (one token per user) |
| `created_at` | DateTime | When the token was generated |
The `token` column has a `default=lambda: secrets.token_hex(32)` — this means whenever a new DeviceToken is created, the token value is automatically generated using Python's `secrets` module (which is cryptographically secure).
**`get_or_create(user_id)`** — a static method that checks if a token already exists for a user, and creates one if not. I use this so I don't accidentally create duplicate tokens.
**`regenerate()`** — replaces the current token with a brand new one. Used when the user clicks "Regenerate Token" on the device token page.
---
## The `@login_manager.user_loader` Function
```python
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```
This tells Flask-Login how to load a user from the database given their ID. Flask-Login stores the user ID in the session cookie, and every request it calls this function to get the full user object back. Without this, `current_user` wouldn't work.