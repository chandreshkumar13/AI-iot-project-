import os
import io
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request, render_template, abort, flash, redirect, url_for
from flask_login import login_required, current_user
from config import Config
from extensions import db, login_manager, bcrypt
from models import User, Detection


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"
    from auth import auth_bp
    app.register_blueprint(auth_bp)
    ml_model = _load_model(app.config["MODEL_PATH"])

    # ── Helper: base detection query scoped to current user ───────────
    def _det_query():
        """
        Admins see everything.
        Regular users see: their own uploads + all ESP32 detections (user_id=None or system role).
        """
        if current_user.role == "admin":
            return Detection.query
        system_user = User.query.filter_by(role="system").first()
        system_id   = system_user.id if system_user else -1
        from sqlalchemy import or_
        return Detection.query.filter(
            or_(
                Detection.user_id == current_user.id,   # their own uploads
                Detection.user_id == system_id,          # ESP32 live detections
            )
        )

    # ── Routes ─────────────────────────────────────────────────────────
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/dashboard")
    @login_required
    def dashboard():
        q      = _det_query()
        recent = q.order_by(Detection.timestamp.desc()).limit(10).all()
        total  = q.count()
        alerts = q.filter_by(alert_triggered=True).count()
        return render_template("dashboard.html", detections=recent, total=total,
            alert_count=alerts, refresh_interval=Config.REFRESH_INTERVAL,
            class_colors=Config.CLASS_COLORS,
            model_loaded=(ml_model is not None))

    @app.route("/history")
    @login_required
    def history():
        page         = request.args.get("page", 1, type=int)
        class_filter = request.args.get("class", "")
        q            = _det_query().order_by(Detection.timestamp.desc())
        if class_filter:
            q = q.filter_by(class_name=class_filter)
        pagination = q.paginate(page=page, per_page=25, error_out=False)
        return render_template("history.html", pagination=pagination,
            class_filter=class_filter, class_names=Config.CLASS_NAMES)

    @app.route("/admin/users")
    @login_required
    def admin_users():
        if current_user.role != "admin":
            abort(403)
        users = User.query.filter(User.role != "system").order_by(User.created_at.desc()).all()
        return render_template("admin_users.html", users=users)

    @app.route("/admin/users/<int:user_id>/toggle", methods=["POST"])
    @login_required
    def toggle_user(user_id):
        if current_user.role != "admin":
            abort(403)
        user = User.query.get_or_404(user_id)
        if user.id == current_user.id:
            return jsonify({"error": "Cannot disable yourself"}), 400
        if user.role == "system":
            return jsonify({"error": "Cannot modify system user"}), 400
        user.is_active = not user.is_active
        db.session.commit()
        return jsonify({"status": "ok", "is_active": user.is_active})

    @app.route("/api/esp32/data", methods=["POST"])
    def esp32_data():
        payload = request.get_json(silent=True)
        if not payload or "csi" not in payload:
            return jsonify({"error": "Missing CSI data"}), 400
        csi_raw   = np.array(payload["csi"], dtype=np.float32)
        device_id = payload.get("device_id", "ESP32-01")
        location  = payload.get("location",  "Road Sensor 1")
        try:
            predicted_class, confidence = _run_inference(ml_model, csi_raw)
        except RuntimeError as e:
            return jsonify({"error": str(e)}), 503
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        # Assign to the dedicated system user
        system_user = User.query.filter_by(role="system").first()
        system_id   = system_user.id if system_user else None

        class_name      = Config.CLASS_NAMES[predicted_class]
        alert_triggered = predicted_class in Config.ALERT_CLASSES
        det = Detection(predicted_class=predicted_class, class_name=class_name,
            confidence=confidence, alert_triggered=alert_triggered,
            device_id=device_id, location=location, user_id=system_id)
        db.session.add(det)
        db.session.commit()
        return jsonify({"status": "ok", "id": det.id,
            "predicted_class": predicted_class, "class_name": class_name,
            "confidence": round(confidence, 4), "alert": alert_triggered})

    @app.route("/api/latest")
    @login_required
    def api_latest():
        q          = _det_query()
        detections = q.order_by(Detection.timestamp.desc()).limit(20).all()
        total      = q.count()
        alerts     = q.filter_by(alert_triggered=True).count()
        class_counts = {name: q.filter_by(class_name=name).count()
                        for name in Config.CLASS_NAMES.values()}
        last      = q.order_by(Detection.timestamp.desc()).first()
        last_seen = last.timestamp.strftime("%H:%M:%S") if last else "N/A"
        return jsonify({"timeline": [d.to_dict() for d in detections],
            "total": total, "alerts": alerts, "class_counts": class_counts,
            "last_seen": last_seen, "class_colors": Config.CLASS_COLORS})

    @app.route("/upload", methods=["GET", "POST"])
    @login_required
    def upload():
        if request.method == "GET":
            return render_template("upload.html")

        uploaded = request.files.get("datafile")
        location = request.form.get("location", "File Upload").strip() or "File Upload"

        if not uploaded or uploaded.filename == "":
            flash("Please select a file to upload.", "danger")
            return render_template("upload.html")

        fname = uploaded.filename.lower()
        if not (fname.endswith(".parquet") or fname.endswith(".csv")):
            flash("Only .parquet or .csv files are supported.", "danger")
            return render_template("upload.html")

        try:
            raw_bytes = uploaded.read()
            if fname.endswith(".parquet"):
                df = pd.read_parquet(io.BytesIO(raw_bytes), engine="pyarrow")
            else:
                df = pd.read_csv(io.BytesIO(raw_bytes))
        except Exception as e:
            flash(f"Could not read file: {e}", "danger")
            return render_template("upload.html")

        label_col = next((c for c in ["label","class","target","y"] if c in df.columns), None)
        feat_cols = [c for c in df.columns if c != label_col]
        EXPECTED  = Config.TIME_STEPS * Config.SUBCARRIERS

        if len(feat_cols) != EXPECTED:
            flash(f"Expected {EXPECTED} feature columns, found {len(feat_cols)}.", "danger")
            return render_template("upload.html")

        if ml_model is None:
            flash("Model is not loaded. Place model file in the project folder and restart.", "danger")
            return render_template("upload.html")

        # ── Batch inference ────────────────────────────────────────────
        X = df[feat_cols].values.astype("float32")

        if isinstance(ml_model, dict):
            feats  = _extract_features(X)
            scaled = ml_model["scaler"].transform(feats)
            pca_x  = ml_model["pca"].transform(scaled)
            probs  = ml_model["model"].predict_proba(pca_x)
        else:
            mu     = X.mean(axis=1, keepdims=True)
            std    = X.std(axis=1,  keepdims=True) + 1e-8
            X_norm = ((X - mu) / std).reshape(-1, Config.TIME_STEPS, Config.SUBCARRIERS, 1)
            try:
                probs = ml_model.predict(X_norm, batch_size=32, verbose=0)
            except Exception as e:
                flash(f"Prediction error: {e}", "danger")
                return render_template("upload.html")

        pred_classes = probs.argmax(axis=1)
        confidences  = probs.max(axis=1)
        true_labels  = df[label_col].values.astype(int) if label_col else None

        results          = []
        batch_detections = []

        for idx in range(len(df)):
            pred_class = int(pred_classes[idx])
            confidence = float(confidences[idx])
            class_name = Config.CLASS_NAMES[pred_class]
            alert      = pred_class in Config.ALERT_CLASSES
            true_label = int(true_labels[idx]) if true_labels is not None else None
            true_name  = Config.CLASS_NAMES.get(true_label) if true_label is not None else None
            correct    = (pred_class == true_label) if true_label is not None else None
            results.append({
                "row": idx + 1,
                "class_name": class_name,
                "confidence": round(confidence * 100, 1),
                "alert": alert,
                "true_name": true_name,
                "correct": correct,
            })
            batch_detections.append(Detection(
                predicted_class=pred_class, class_name=class_name,
                confidence=confidence, alert_triggered=alert,
                device_id="File-Upload", location=location,
                user_id=current_user.id,   # ← scoped to uploader
            ))

        db.session.bulk_save_objects(batch_detections)
        db.session.commit()

        total_rows   = len(results)
        alert_count  = sum(1 for r in results if r["alert"])
        class_counts = {}
        for r in results:
            class_counts[r["class_name"]] = class_counts.get(r["class_name"], 0) + 1
        correct_count = sum(1 for r in results if r["correct"]) if label_col else None

        flash(f"Processed {total_rows} rows. {alert_count} alerts triggered.", "success")
        return render_template("upload.html",
            results=results, total_rows=total_rows, alert_count=alert_count,
            class_counts=class_counts, correct_count=correct_count,
            label_col=label_col, class_colors=Config.CLASS_COLORS,
            filename=uploaded.filename,
        )


    @app.route("/admin/users/<int:user_id>/role", methods=["POST"])
    @login_required
    def change_role(user_id):
        if current_user.role != "admin":
            abort(403)
        user = User.query.get_or_404(user_id)
        if user.id == current_user.id:
            return jsonify({"error": "Cannot change your own role"}), 400
        if user.role == "system":
            return jsonify({"error": "Cannot modify system user"}), 400
        new_role = request.get_json(silent=True).get("role", "")
        if new_role not in ("admin", "operator", "viewer"):
            return jsonify({"error": "Invalid role"}), 400
        user.role = new_role
        db.session.commit()
        return jsonify({"status": "ok", "role": user.role})

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("error.html", code=403, message="Access Forbidden"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", code=404, message="Page Not Found"), 404

    with app.app_context():
        db.create_all()
        _migrate_db()
        _seed_users()

    return app


# ══════════════════════════════════════════════════════════════════════════
# DB migration — adds user_id column to existing detections if missing
# ══════════════════════════════════════════════════════════════════════════
def _migrate_db():
    from sqlalchemy import text, inspect
    inspector = inspect(db.engine)
    cols = [c["name"] for c in inspector.get_columns("detections")]
    if "user_id" not in cols:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE detections ADD COLUMN user_id INTEGER REFERENCES users(id)"))
            conn.commit()
        print("[CSI] Migrated: added user_id column to detections")

    # Assign any un-owned detections to admin
    admin = User.query.filter_by(username="admin").first()
    if admin:
        unowned = Detection.query.filter_by(user_id=None).count()
        if unowned:
            Detection.query.filter_by(user_id=None).update({"user_id": admin.id})
            db.session.commit()
            print(f"[CSI] Assigned {unowned} existing detections to admin")


# ══════════════════════════════════════════════════════════════════════════
# Seed admin + system user
# ══════════════════════════════════════════════════════════════════════════
def _seed_users():
    from extensions import bcrypt as _bc

    # Admin
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", email="admin@csi.local",
            password_hash=_bc.generate_password_hash("admin123").decode("utf-8"),
            role="admin")
        db.session.add(admin)
        db.session.commit()
        print("[CSI] Default admin created  username=admin  password=admin123")

    # System user for ESP32 detections
    if not User.query.filter_by(role="system").first():
        system = User(username="__system__", email="system@csi.local",
            password_hash=_bc.generate_password_hash(os.urandom(32).hex()).decode("utf-8"),
            role="system", is_active=False)
        db.session.add(system)
        db.session.commit()
        print("[CSI] System user created for ESP32 detections")


# ══════════════════════════════════════════════════════════════════════════
# Model loading
# ══════════════════════════════════════════════════════════════════════════
def _load_model(path):
    if not os.path.exists(path):
        print(f"[CSI] Model file not found at: {path}")
        return None

    if path.endswith(".pkl"):
        try:
            import joblib
            bundle = joblib.load(path)
            print(f"[CSI] ML model loaded: {bundle.get('model_name','unknown')} from {path}")
            return bundle
        except Exception as e:
            print(f"[CSI] Failed to load .pkl model: {e}")
            return None


# ══════════════════════════════════════════════════════════════════════════
# Feature extraction — must exactly match train_csi_ml.py
# ══════════════════════════════════════════════════════════════════════════
def _extract_features(X):
    from scipy.stats import skew, kurtosis
    from scipy.fft import fft as scipy_fft
    TIME_STEPS  = Config.TIME_STEPS
    SUBCARRIERS = Config.SUBCARRIERS
    N = X.shape[0]
    dc     = X.mean(axis=1, keepdims=True)
    X_c    = X - dc
    X_3d_c = X_c.reshape(N, TIME_STEPS, SUBCARRIERS)
    feats  = []
    sc_mean   = X_3d_c.mean(axis=1)
    sc_std    = X_3d_c.std(axis=1)
    sc_max    = X_3d_c.max(axis=1)
    sc_min    = X_3d_c.min(axis=1)
    sc_range  = sc_max - sc_min
    sc_energy = (X_3d_c ** 2).mean(axis=1)
    sc_skew   = np.array([skew(X_3d_c[i], axis=0)     for i in range(N)])
    sc_kurt   = np.array([kurtosis(X_3d_c[i], axis=0) for i in range(N)])
    feats += [sc_mean, sc_std, sc_max, sc_min, sc_range, sc_energy, sc_skew, sc_kurt]
    ts_mean  = X_3d_c.mean(axis=2)
    ts_std   = X_3d_c.std(axis=2)
    ts_range = X_3d_c.max(axis=2) - X_3d_c.min(axis=2)
    feats += [ts_mean, ts_std, ts_range]
    g_std    = X_c.std(axis=1, keepdims=True)
    g_range  = (X_c.max(axis=1) - X_c.min(axis=1)).reshape(N, 1)
    g_energy = (X_c ** 2).mean(axis=1, keepdims=True)
    g_skew   = skew(X_c, axis=1).reshape(N, 1)
    g_kurt   = kurtosis(X_c, axis=1).reshape(N, 1)
    g_sc_var = sc_mean.std(axis=1, keepdims=True)
    g_ts_var = ts_mean.std(axis=1, keepdims=True)
    feats += [g_std, g_range, g_energy, g_skew, g_kurt, g_sc_var, g_ts_var]
    fft_mag = np.abs(scipy_fft(X_3d_c, axis=1))[:, 1:TIME_STEPS//2, :]
    band_sz = fft_mag.shape[1] // 5
    for b in range(5):
        feats.append(fft_mag[:, b*band_sz:(b+1)*band_sz, :].mean(axis=1))
    delta    = np.diff(X_3d_c, axis=1)
    d_mean   = delta.mean(axis=1)
    d_std    = delta.std(axis=1)
    d_abs    = np.abs(delta).max(axis=1)
    d_energy = (delta ** 2).mean(axis=1)
    feats += [d_mean, d_std, d_abs, d_energy]
    return np.hstack(feats).astype(np.float32)


# ══════════════════════════════════════════════════════════════════════════
# Inference
# ══════════════════════════════════════════════════════════════════════════
def _run_inference(model, csi_raw):
    if model is None:
        raise RuntimeError("Model is not loaded. Place model file in the project folder and restart.")
    EXPECTED = Config.TIME_STEPS * Config.SUBCARRIERS
    if len(csi_raw) != EXPECTED:
        raise ValueError(f"Expected {EXPECTED} features per row, got {len(csi_raw)}.")
    if isinstance(model, dict):
        X      = csi_raw.reshape(1, -1).astype(np.float32)
        feats  = _extract_features(X)
        scaled = model["scaler"].transform(feats)
        pca_x  = model["pca"].transform(scaled)
        proba  = model["model"].predict_proba(pca_x)[0]
        return int(np.argmax(proba)), float(proba[np.argmax(proba)])
    mu  = csi_raw.mean()
    std = csi_raw.std() + 1e-8
    x   = ((csi_raw - mu) / std).reshape(1, Config.TIME_STEPS, Config.SUBCARRIERS, 1)
    prob = model.predict(x, verbose=0)[0]
    return int(np.argmax(prob)), float(prob[np.argmax(prob)])


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
