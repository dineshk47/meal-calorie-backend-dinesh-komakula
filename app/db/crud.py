from sqlalchemy.orm import Session
from sqlalchemy import or_

import models
import schemas

def create_user(db: Session, user: schemas.UserCreate):
    u = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        hashed_password=user.password  # hashed before calling this ideally
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def update_user(db: Session, user_id: int, patch: schemas.UserUpdate):
    u = get_user(db, user_id)
    if not u:
        return None
    if patch.first_name is not None:
        u.first_name = patch.first_name
    if patch.last_name is not None:
        u.last_name = patch.last_name
    if patch.email is not None:
        u.email = patch.email
    db.commit()
    db.refresh(u)
    return u

def delete_user(db: Session, user_id: int):
    u = get_user(db, user_id)
    if not u:
        return False
    db.delete(u)
    db.commit()
    return True

def list_users(db: Session, limit: int = 10, offset: int = 0, q: str | None = None):
    query = db.query(models.User)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(models.User.first_name.ilike(like),
                                 models.User.last_name.ilike(like),
                                 models.User.email.ilike(like)))
    total = query.count()
    items = query.order_by(models.User.id).offset(offset).limit(limit).all()
    return items, total
