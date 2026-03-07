# auth/ — Authentication Blueprint
The `auth/` folder contains all the login/register/logout logic, separated from the main `app.py` using Flask's **Blueprint** system.
---
## auth/\_\_init\_\_.py
```python
from flask import Blueprint
auth_bp=Blueprint('auth', __name__, url_prefix='/auth')
from auth import routes
```
This is where the Blueprint object is created. A Blueprint in Flask is basically a mini-app — a way to group related routes together and register them onto the main app later.
The `url_prefix='/auth'` means every route defined in this blueprint automatically gets `/auth` prepended to it. So the login route becomes `/auth/login`, register becomes `/auth/register`, etc.
The `from auth import routes` at the bottom imports the routes file, which registers all the route functions onto `auth_bp`. The `# noqa` comment tells the linter to ignore the fact that this import looks unused — it's actually required to trigger the registration.
---
## auth/routes.py
This file defines three routes on the `auth_bp` blueprint.
---
### `POST /auth/register` — Create a New Account
Validates the form in this order:
1. All fields must be filled in
2. Passwords must match
3. Password must be at least 6 characters
4. Role must be one of `admin`, `operator`, `viewer` (anything else gets reset to `viewer`)
5. Username must not already exist (exact case match — `Admin` and `admin` are different)
6. Email must not already be registered
7. **Admin guard** — if someone selects the Admin role but isn't already logged in as an admin, they're silently downgraded to Viewer with a warning flash message
If all checks pass, the password is hashed with bcrypt and the new user is saved:
```python
pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
user = User(username=username, email=email, password_hash=pw_hash, role=role)
db.session.add(user)
db.session.commit()
```
### `POST /auth/login` — Sign In
1. Looks up the user by username: `User.query.filter(User.username == username).first()`
2. Blocks the `system` role user from ever logging in
3. Verifies the password: `bcrypt.check_password_hash(user.password_hash, password)`
4. If `is_active` is `False`, blocks login with an error message
5. Calls `login_user(user, remember=remember)` which creates the session
6. Redirects to the `next` URL parameter if present (Flask-Login sets this when a user is redirected to login from a protected page), otherwise goes to `/dashboard`
The login is **case-sensitive** — `Admin` and `admin` are treated as completely different accounts.
---
### `GET /auth/logout` — Sign Out
Very simple:
```python
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
```
`logout_user()` clears the session. The user is then redirected back to the login page.