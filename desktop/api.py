import requests
import os

API_BASE = os.environ.get("API_BASE", "http://127.0.0.1:5000")
API = f"{API_BASE}/api"
AUTH = f"{API_BASE}/auth"

class ApiClient:
    def __init__(self):
        self.username = None

    # Auth
    def login(self, username, password):
        r = requests.post(f"{AUTH}/login", json={"username": username, "password": password})
        r.raise_for_status()
        self.username = r.json()["user"]["username"]
        return r.json()["user"]

    # Donors
    def list_donors(self):
        r = requests.get(f"{API}/donors")
        r.raise_for_status()
        return r.json()["donors"]

    def get_donor(self, donor_id):
        r = requests.get(f"{API}/donors/{donor_id}")
        r.raise_for_status()
        return r.json()["donor"]

    def create_donor(self, payload):
        r = requests.post(f"{API}/donors", json=payload)
        r.raise_for_status()
        return r.json()["donor"]

    def update_donor(self, donor_id, payload):
        r = requests.put(f"{API}/donors/{donor_id}", json=payload)
        r.raise_for_status()
        return r.json()["donor"]

    def delete_donor(self, donor_id):
        r = requests.delete(f"{API}/donors/{donor_id}")
        r.raise_for_status()
        return True

    def search_donors(self, params):
        r = requests.get(f"{API}/donors/search", params=params)
        r.raise_for_status()
        return r.json()["donors"]

    # Stock
    def get_stock(self):
        r = requests.get(f"{API}/stock")
        r.raise_for_status()
        return r.json()["stock"]

    def adjust_stock(self, blood_group, delta, reason):
        r = requests.post(f"{API}/stock/adjust", json={"blood_group": blood_group, "delta": delta, "reason": reason})
        r.raise_for_status()
        return r.json()

    def stock_movements(self, limit=100):
        r = requests.get(f"{API}/stock/movements", params={"limit": limit})
        r.raise_for_status()
        return r.json()["movements"]

    # Analytics
    def analytics_summary(self, days=30):
        r = requests.get(f"{API}/analytics/summary", params={"days": days})
        r.raise_for_status()
        return r.json()

    # Export
    def export_donors_csv(self, filepath):
        r = requests.get(f"{API}/export/donors.csv")
        r.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(r.content)
        return filepath
