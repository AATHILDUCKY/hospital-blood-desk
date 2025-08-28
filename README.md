# Hospital Blood Desk – Donor & Stock Manager (PyQt5 + Flask + MySQL)

A lightweight local app for hospitals to manage donors and blood stock with a modern UI, instant search, and simple analytics.

## Features
- Secure login (default: `admin` / `admin123`)
- Donor management (add/edit/search/filter)
- Inventory (view by blood group, adjust units with reasons; instant UI refresh)
- Dashboard & Analytics (Chart.js via CDN in QWebEngine)
- CSV export (donors)
- Short numeric IDs (auto-increment), 8 standard blood groups only

## Tech
- Backend: Flask + SQLAlchemy + MySQL (XAMPP)
- Desktop: PyQt5 + PyQtWebEngine (for charts)
- Charts/icons: Chart.js + Font Awesome (CDNs in embedded HTML)

## File Structure
```
hospital-blood-desk/
  backend/
    app.py
    auth.py
    routes.py
    models.py
    db.py
    config.py
    create_db.py
    requirements.txt
    .env.example
  desktop/
    main.py
    api.py
    assets/
      styles.qss
      html/
        dashboard.html
        analytics.html
    pages/
      login.py
      dashboard.py
      donors.py
      inventory.py
      analytics.py
      settings.py
```

## Setup

### 1) MySQL (XAMPP)
- Start MySQL in XAMPP.
- Create database `blood_desk` (no tables needed; app will create them).

### 2) Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
# (Optional) copy .env.example to .env and adjust DB creds
python -m backend.create_db   # OR: python create_db.py if run as a module fails
python -m backend.app         # runs Flask at http://127.0.0.1:5000
```
> If `python -m backend.create_db` fails, run: `python create_db.py` from inside `backend/`.

### 3) Desktop app
```bash
cd ../desktop
python -m venv venv
source venv/bin/activate
pip install PyQt5 PyQtWebEngine requests
# Ensure the backend is running first
python -m desktop.main  # or: python main.py
```

If the backend runs on a different host/port, set env var before starting desktop:
```bash
set API_BASE=http://192.168.1.10:5000   # Windows
export API_BASE=http://192.168.1.10:5000 # Linux/macOS
```

## Notes
- Inventory section updates instantly after every adjust.
- Donor list supports double-click to open a profile popup (no extra page load).
- Analytics opens as a separate page with charts (no spinner/loading screens).
- Replace long IDs with simple auto-increment integers for clean UX.
- Only valid blood groups are allowed: O+, O-, A+, A-, B+, B-, AB+, AB-.
