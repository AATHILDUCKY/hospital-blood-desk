from .app import create_app
from .db import db
from .models import User, Stock, BLOOD_GROUPS
import bcrypt

def main():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Seed admin user
        password = b"admin123"
        pw_hash = bcrypt.hashpw(password, bcrypt.gensalt())
        admin = User(username="admin", password_hash=pw_hash, role="staff")
        db.session.add(admin)

        # Seed stock rows
        for g in BLOOD_GROUPS:
            db.session.add(Stock(blood_group=g, units=0))

        db.session.commit()
        print("Database created. Default login: admin / admin123")

if __name__ == "__main__":
    main()
