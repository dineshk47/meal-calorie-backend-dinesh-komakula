from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.auth.errors import error_response, success_response
from app.db.init_db import Base, get_db,engine
import models
import schemas
from ..utils.security import get_password_hash, verify_password, create_access_token
from sqlalchemy.exc import IntegrityError

router = APIRouter()
Base.metadata.create_all(bind=engine)


@router.post("/register")
def register(payload: schemas.RegisterRequest, db: Session = Depends(get_db)):
    # check if exists
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail={
                    "status": "GE40001",
                    "error": "Email already registered",
                })
    hashed = get_password_hash(payload.password)
    user = models.User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        hashed_password=hashed
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail={
                    "status": "GE40002",
                    "error": "Registration failed",
                })
    except Exception as e:
        return error_response(
            status_code="GE50000",
            error=e,
            http_status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    response_data = {
        "id": user.id,
        "message": "Registered successfully."
    }
    return success_response(
            status_code="GS20101",
            data=response_data,
            http_status_code=201,
        )
    

@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=401, 
            detail={
                    "status": "GE40101",
                    "error": "Invalid credentials",
                })
    token = create_access_token(subject=str(user.id))
    return success_response(
            status_code="GS20001",
            data={"access_token": token, "token_type": "bearer"},
            http_status_code=200,
        )
