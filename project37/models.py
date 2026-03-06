from datetime import datetime
from flask_login import UserMixin
from extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(80),  unique=True, nullable=False)
    email=db.Column(db.String(120), unique=True, nullable=False)
    password_hash=db.Column(db.String(256), nullable=False)
    role=db.Column(db.String(20),  nullable=False, default='viewer')
    
    created_at=db.Column(db.DateTime, default=datetime.utcnow)
    is_active=db.Column(db.Boolean, default=True)

    detections=db.relationship('Detection', backref='owner', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username} [{self.role}]>'


class Detection(db.Model):
    __tablename__ = 'detections'

    id=db.Column(db.Integer, primary_key=True)
    timestamp=db.Column(db.DateTime, default=datetime.utcnow, index=True)
    predicted_class=db.Column(db.Integer,  nullable=False)
    class_name=db.Column(db.String(50), nullable=False)
    confidence=db.Column(db.Float,    nullable=False)
    alert_triggered=db.Column(db.Boolean,  default=False)
    device_id=db.Column(db.String(50), default='ESP32-01')
    location=db.Column(db.String(100), default='Road Sensor 1')
    
    user_id=db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)

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
