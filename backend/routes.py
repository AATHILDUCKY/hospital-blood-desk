from flask import Blueprint, request, send_file
from sqlalchemy import and_, or_, func
from datetime import datetime, date
from io import StringIO
import csv

from .db import db
from .models import Donor, Stock, StockMovement, BLOOD_GROUPS

api_bp = Blueprint("api", __name__)

# ---------- Donors ----------

@api_bp.post("/donors")
def create_donor():
    data = request.get_json() or {}
    try:
        donor = Donor(
            name=data.get("name"),
            nic=data.get("nic"),
            phone=data.get("phone"),
            email=data.get("email"),
            address=data.get("address"),
            area=data.get("area"),
            blood_group=data.get("blood_group"),
            age=data.get("age"),
            last_donation_date=datetime.fromisoformat(data["last_donation_date"]).date() if data.get("last_donation_date") else None,
            notes=data.get("notes"),
            active=bool(data.get("active", True)),
        )
        db.session.add(donor)
        db.session.commit()
        return {"donor": donor.to_dict()}, 201
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 400

@api_bp.get("/donors")
def list_donors():
    donors = Donor.query.order_by(Donor.id.desc()).limit(500).all()
    return {"donors": [d.to_dict() for d in donors]}

@api_bp.get("/donors/<int:donor_id>")
def get_donor(donor_id):
    d = Donor.query.get_or_404(donor_id)
    return {"donor": d.to_dict()}

@api_bp.put("/donors/<int:donor_id>")
def update_donor(donor_id):
    data = request.get_json() or {}
    d = Donor.query.get_or_404(donor_id)
    try:
        for field in ["name", "nic", "phone", "email", "address", "area", "blood_group", "age", "notes", "active"]:
            if field in data:
                setattr(d, field, data[field])
        if "last_donation_date" in data:
            d.last_donation_date = datetime.fromisoformat(data["last_donation_date"]).date() if data["last_donation_date"] else None
        db.session.commit()
        return {"donor": d.to_dict()}
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 400

@api_bp.delete("/donors/<int:donor_id>")
def delete_donor(donor_id):
    d = Donor.query.get_or_404(donor_id)
    db.session.delete(d)
    db.session.commit()
    return {"ok": True}

@api_bp.get("/donors/search")
def search_donors():
    q = request.args.get("q", "").strip()
    bg = request.args.get("blood_group")
    area = request.args.get("area")
    age_min = request.args.get("age_min", type=int)
    age_max = request.args.get("age_max", type=int)
    last_after = request.args.get("last_after")
    last_before = request.args.get("last_before")

    query = Donor.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Donor.name.like(like), Donor.phone.like(like), Donor.email.like(like), Donor.address.like(like), Donor.area.like(like)))
    if bg:
        query = query.filter(Donor.blood_group == bg)
    if area:
        query = query.filter(Donor.area.like(f"%{area}%"))
    if age_min is not None:
        query = query.filter(Donor.age >= age_min)
    if age_max is not None:
        query = query.filter(Donor.age <= age_max)
    if last_after:
        query = query.filter(Donor.last_donation_date >= datetime.fromisoformat(last_after).date())
    if last_before:
        query = query.filter(Donor.last_donation_date <= datetime.fromisoformat(last_before).date())

    donors = query.order_by(Donor.id.desc()).limit(500).all()
    return {"donors": [d.to_dict() for d in donors]}

# ---------- Stock ----------

@api_bp.get("/stock")
def get_stock():
    items = Stock.query.order_by(Stock.blood_group).all()
    # ensure all groups exist
    existing = {s.blood_group for s in items}
    for g in BLOOD_GROUPS:
        if g not in existing:
            s = Stock(blood_group=g, units=0)
            db.session.add(s)
    if len(existing) != len(BLOOD_GROUPS):
        db.session.commit()
        items = Stock.query.order_by(Stock.blood_group).all()
    return {"stock": [s.to_dict() for s in items]}

@api_bp.post("/stock/adjust")
def adjust_stock():
    data = request.get_json() or {}
    bg = data.get("blood_group")
    delta = int(data.get("delta", 0))
    reason = data.get("reason", "adjust")

    if bg not in BLOOD_GROUPS:
        return {"error": "Invalid blood group"}, 400
    if delta == 0:
        return {"error": "Delta must be non-zero"}, 400

    s = Stock.query.filter_by(blood_group=bg).first()
    if not s:
        s = Stock(blood_group=bg, units=0)
        db.session.add(s)
        db.session.flush()

    new_units = s.units + delta
    if new_units < 0:
        return {"error": "Not enough units"}, 400

    s.units = new_units
    mv = StockMovement(blood_group=bg, delta=delta, reason=reason, user_id=None)
    db.session.add(mv)
    db.session.commit()
    return {"stock": s.to_dict(), "movement": mv.to_dict()}

@api_bp.get("/stock/movements")
def stock_movements():
    limit = request.args.get("limit", default=100, type=int)
    items = StockMovement.query.order_by(StockMovement.id.desc()).limit(limit).all()
    return {"movements": [m.to_dict() for m in items]}

# ---------- Analytics ----------

@api_bp.get("/analytics/summary")
def analytics_summary():
    # Total units by group
    stock = db.session.query(Stock.blood_group, Stock.units).all()
    # Donations vs issues (approx via movements + delta sign)
    last_days = int(request.args.get("days", 30))
    since = datetime.utcnow() - func.interval(last_days, 'DAY') if False else None  # portable: filter manually
    # We'll just take last N movements
    movements = StockMovement.query.order_by(StockMovement.id.desc()).limit(300).all()

    donations = {}
    issues = {}
    for m in movements:
        day = m.timestamp.date().isoformat()
        if m.delta >= 0:
            donations[day] = donations.get(day, 0) + m.delta
        else:
            issues[day] = issues.get(day, 0) + (-m.delta)

    low = [s.blood_group for s in Stock.query.filter(Stock.units < 5).all()]

    return {
        "stock": [{"blood_group": bg, "units": units} for bg, units in stock],
        "donations": donations,
        "issues": issues,
        "low_stock": low,
    }

# ---------- Exports ----------

@api_bp.get("/export/donors.csv")
def export_donors_csv():
    donors = Donor.query.order_by(Donor.id.asc()).all()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(["id","name","nic","phone","email","address","area","blood_group","age","last_donation_date","active","created_at"])
    for d in donors:
        cw.writerow([d.id,d.name,d.nic,d.phone,d.email,d.address,d.area,d.blood_group,d.age,
                     d.last_donation_date.isoformat() if d.last_donation_date else "",
                     int(d.active), d.created_at.isoformat()])
    si.seek(0)
    return si.getvalue(), 200, {
        "Content-Type": "text/csv",
        "Content-Disposition": "attachment; filename=donors.csv"
    }
