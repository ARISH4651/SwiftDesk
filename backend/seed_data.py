import os
import sys

# Ensure backend root is in python path
backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import json
from app.database import SessionLocal, engine, Base
from app.models.engineer import Engineer
from app.models.user import User
from app.core.security import hash_password

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Seed Support Engineers
        sample_path = os.path.join(os.path.dirname(__file__), "..", "sample_data", "support_agents.json")
        if os.path.exists(sample_path):
            with open(sample_path, "r", encoding="utf-8") as f:
                agents_data = json.load(f)

            for agent in agents_data:
                existing = db.query(Engineer).filter(Engineer.agent_id == agent["agent_id"]).first()
                if not existing:
                    eng = Engineer(
                        agent_id=agent["agent_id"],
                        name=agent["name"],
                        email=agent["email"],
                        level=agent["level"],
                        is_available=agent.get("is_available", True),
                        max_capacity=agent.get("max_capacity", 5),
                        current_load=agent.get("current_load", 0)
                    )
                    db.add(eng)
                    print(f"Seeded engineer: {eng.name} ({eng.agent_id}, Level {eng.level})")

        # Seed Users for JWT Auth
        default_users = [
            {"email": "customer@swiftdesk.com", "password": "customer123", "role": "CUSTOMER"},
            {"email": "support@swiftdesk.com", "password": "support123", "role": "SUPPORT"},
            {"email": "admin@swiftdesk.com", "password": "admin123", "role": "ADMIN"},
        ]

        for u in default_users:
            existing_user = db.query(User).filter(User.email == u["email"]).first()
            if existing_user:
                existing_user.password_hash = hash_password(u["password"])
                existing_user.role = u["role"]
                existing_user.active = True
                print(f"Updated user credentials: {u['email']} (Role: {u['role']})")
            else:
                new_user = User(
                    email=u["email"],
                    password_hash=hash_password(u["password"]),
                    role=u["role"],
                    active=True
                )
                db.add(new_user)
                print(f"Seeded user: {u['email']} (Role: {u['role']})")

        db.commit()
        print("Seeding completed successfully.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
