# extensions.py — Flask Extensions
This is a very short file but it solves a really annoying problem in Flask called **circular imports**.
```python
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
db=SQLAlchemy()
login_manager=LoginManager()
bcrypt=Bcrypt()
```
That's literally the whole file.
---
## Why Does This File Exist?
In Flask, extensions like SQLAlchemy and Flask-Login need to be initialised with the app object (`db.init_app(app)`), but they also need to be imported by `models.py` to define the database tables.
If I defined `db = SQLAlchemy()` inside `app.py`, then `models.py` would have to import from `app.py`. But `app.py` also imports from `models.py`. That creates a circular import — Python gets confused about which file to load first and crashes.
The fix is to define the extensions in their own separate file (`extensions.py`) that has no imports from the rest of the project. Then both `app.py` and `models.py` can import from `extensions.py` without any circular dependency.
```
extensions.py←app.py
extensions.py←models.py
app.py← models.py
```
---
## What Each Extension Does
**`SQLAlchemy` (`db`)** — handles all database interactions. Lets me define tables as Python classes and query them using Python instead of raw SQL
**`LoginManager` (`login_manager`)** — manages user sessions. Tracks who is logged in, protects routes with `@login_required`, and handles redirecting unauthenticated users to the login page
**`Bcrypt` (`bcrypt`)** — used to hash passwords before saving them and to verify passwords at login. Bcrypt is slow by design which makes brute-force attacks much harder