from uuid import UUID
from sqlalchemy.orm import Session
from rejesha_green.models.user import User

class UserRepository:
    def __init__(self, db: Session): self.db = db
    def create_user(self, user: User): self.db.add(user); self.db.commit(); self.db.refresh(user); return user
    def get_user(self, user_id: UUID): return self.db.query(User).filter(User.user_id == user_id).first()
    def get_all_users(self, skip=0, limit=100): return self.db.query(User).offset(skip).limit(limit).all()
    def get_by_phone(self, phone: str): return self.db.query(User).filter(User.phone == phone).first()
    def get_by_national_id(self, national_id: str): return self.db.query(User).filter(User.national_id == national_id).first()
    def get_by_email(self, email: str): return self.db.query(User).filter(User.email == email).first() if email else None
    def update_user(self, user: User): self.db.commit(); self.db.refresh(user); return user
    def delete_user(self, user: User): self.db.delete(user); self.db.commit()
    

user_repository = UserRepository