import json
import os
from app.database import SessionLocal, engine, Base
from app.models.engineer import Engineer

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        sample_path = os.path.join(os.path.dirname(__file__), "..", "sample_data", "support_agents.json")
        if not os.path.exists(sample_path):
            print("sample_data/support_agents.json not found!")
            return

        with open(sample_path, "r", encoding="utf-8") as f:
            agents_data = json.load(f)

        for agent in agents_data:
            existing = db.query(Engineer).filter(Engineer.agent_id == agent["agent_id"]).first()
            if existing:
                existing.name = agent["name"]
                existing.email = agent["email"]
                existing.level = agent["level"]
                existing.is_available = agent.get("is_available", True)
                existing.max_capacity = agent.get("max_capacity", 5)
                existing.current_load = agent.get("current_load", 0)
                print(f"Updated engineer seed: {existing.name} ({existing.agent_id}, Level {existing.level})")
            else:
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

        db.commit()
        print("Seeding completed successfully.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
