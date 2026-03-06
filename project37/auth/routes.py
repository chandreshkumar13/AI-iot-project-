from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func
from auth import auth_bp
from extensions import db, bcrypt
from models import User


def _redirect_dashboard():
    return redirect(url_for("dashboard"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return _redirect_dashboard()
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")
        role     = request.form.get("role", "viewer")

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")
        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("register.html")
        if role not in ("admin", "operator", "viewer"):
            role = "viewer"

        # Case-sensitive exact match — 'Admin' and 'admin' are different users
        if User.query.filter(User.username == username).first():
            flash("Username already taken.", "danger")
            return render_template("register.html")
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return render_template("register.html")

        # Only an existing admin can create another admin
        if role == "admin" and (not current_user.is_authenticated or current_user.role != "admin"):
            role = "viewer"
            flash("Admin role requires an existing admin. Registered as Viewer.", "warning")

        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(username=username, email=email, password_hash=pw_hash, role=role)
        db.session.add(user)
        db.session.commit()
        flash("Account created! You can now log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return _redirect_dashboard()
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        # Case-sensitive login — 'Admin' != 'admin'
        user = User.query.filter(User.username == username).first()

        if user and user.role == "system":
            # Block system user from logging in
            flash("Invalid username or password.", "danger")
            return render_template("login.html")

        if user and bcrypt.check_password_hash(user.password_hash, password):
            if not user.is_active:
                flash("Your account has been disabled.", "danger")
                return render_template("login.html")
            login_user(user, remember=remember)
            next_page = request.args.get("next")
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(next_page or url_for("dashboard"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
