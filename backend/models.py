from datetime import datetime, date
from .db import db
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import validates

# Short IDs via auto-increment (INT). No long UUIDs.
# Blood groups limited to standard set.
BLOOD_GROUPS = ("O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-")

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.LargeBinary(60), nullable=False)  # bcrypt hash
    role = db.Column(db.String(20), default="staff")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id, "username": self.username, "role": self.role,
            "created_at": self.created_at.isoformat()
        }

class Donor(db.Model):
    __tablename__ = "donors"
    id = db.Column(db.Integer, primary_key=True)  # short numeric ID
    name = db.Column(db.String(120), nullable=False)
    nic = db.Column(db.String(32), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    area = db.Column(db.String(120), nullable=True)
    blood_group = db.Column(db.String(4), nullable=False, index=True)
    age = db.Column(db.Integer, nullable=True)
    last_donation_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @validates("blood_group")
    def validate_bg(self, key, value):
        assert value in BLOOD_GROUPS, "Invalid blood group"
        return value

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "nic": self.nic, "phone": self.phone,
            "email": self.email, "address": self.address, "area": self.area,
            "blood_group": self.blood_group, "age": self.age,
            "last_donation_date": self.last_donation_date.isoformat() if self.last_donation_date else None,
            "notes": self.notes, "active": self.active,
            "created_at": self.created_at.isoformat(), "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class Stock(db.Model):
    __tablename__ = "stock"
    id = db.Column(db.Integer, primary_key=True)
    blood_group = db.Column(db.String(4), unique=True, nullable=False)
    units = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {"id": self.id, "blood_group": self.blood_group, "units": self.units}

class StockMovement(db.Model):
    __tablename__ = "stock_movements"
    id = db.Column(db.Integer, primary_key=True)
    blood_group = db.Column(db.String(4), nullable=False, index=True)
    delta = db.Column(db.Integer, nullable=False)  # + received, - issued/discarded
    reason = db.Column(db.String(50), nullable=False)  # donation/issue/discard/adjust
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    def to_dict(self):
        return {
            "id": self.id, "blood_group": self.blood_group, "delta": self.delta,
            "reason": self.reason, "timestamp": self.timestamp.isoformat(), "user_id": self.user_id
        }
