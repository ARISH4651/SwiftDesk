from sqlalchemy.orm import Session
from app.models.user import User
from typing import Optional

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email.strip().lower()).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, email: str, password_hash: str, role: str) -> User:
        user = User(
            email=email.strip().lower(),
            password_hash=password_hash,
            role=role.upper(),
            active=True
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
