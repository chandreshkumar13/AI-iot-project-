import os
import secrets
from datetime import datetime
from flask_login import UserMixin
from extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role          = db.Column(db.String(20),  nullable=False, default='viewer')
    # roles: 'admin' | 'operator' | 'viewer' | 'system'
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    is_active     = db.Column(db.Boolean, default=True)

    detections    = db.relationship('Detection', backref='owner', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username} [{self.role}]>'


class Detection(db.Model):
    __tablename__ = 'detections'

    id               = db.Column(db.Integer, primary_key=True)
    timestamp        = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    predicted_class  = db.Column(db.Integer,  nullable=False)
    class_name       = db.Column(db.String(50), nullable=False)
    confidence       = db.Column(db.Float,    nullable=False)
    alert_triggered  = db.Column(db.Boolean,  default=False)
    device_id        = db.Column(db.String(50), default='ESP32-01')
    location         = db.Column(db.String(100), default='Road Sensor 1')
    # Owner — nullable for backwards-compat; existing rows will be reassigned to admin
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)

    def to_dict(self):
        return {
            'id':              self.id,
            'timestamp':       self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'time_only':       self.timestamp.strftime('%H:%M:%S'),
            'predicted_class': self.predicted_class,
            'class_name':      self.class_name,
            'confidence':      round(self.confidence * 100, 1),
            'alert':           self.alert_triggered,
            'device_id':       self.device_id,
            'location':        self.location,
        }

    def __repr__(self):
        return f'<Detection {self.class_name} @ {self.timestamp}>'


class DeviceToken(db.Model):
    __tablename__ = 'device_tokens'

    id         = db.Column(db.Integer, primary_key=True)
    token      = db.Column(db.String(64), unique=True, nullable=False,
                           default=lambda: secrets.token_hex(32))
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('device_token', uselist=False))

    @staticmethod
    def get_or_create(user_id):
        existing = DeviceToken.query.filter_by(user_id=user_id).first()
        if existing:
            return existing
        token = DeviceToken(user_id=user_id)
        db.session.add(token)
        db.session.commit()
        return token

    def regenerate(self):
        self.token = secrets.token_hex(32)
        db.session.commit()

    def __repr__(self):
        return f'<DeviceToken user_id={self.user_id}>'
