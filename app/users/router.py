from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.auth.errors import success_response
from app.verify import get_current_user
import app.db.crud as crud
from app.db.init_db import get_db
import schemas

router = APIRouter()


@router.get("/")
def list_users(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    q: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    items, total = crud.list_users(db, limit=limit, offset=offset, q=q)
    resp = [schemas.OutUsers.from_orm(item) for item in items]
    return {
        "status_code":"GS20006",
            "data": 
                {"result": resp,
                 "detail": "Users list"
                 }}

@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    u = crud.get_user(db, user_id)
    if not u:
        raise HTTPException(
            status_code=404, 
            detail={
                    "status": "GE40402",
                    "error": "User not found",
                })
    response_model=schemas.OutUser.from_orm(u)
    return {
        "status_code":"GS20006",
        "data":{
            "result": response_model, 
            "detail": "User data"
            }
            }


@router.patch("/{user_id}")
def patch_user(user_id: int, patch: schemas.UserUpdate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    u = crud.update_user(db, user_id, patch)
    if not u:
        raise HTTPException(status_code=404, detail={
                    "status": "GE40403",
                    "error": "User not found",
                })
    return success_response(
            status_code="GS20004",
            data={"id": u.id, "detail": "User details updated"},
            http_status_code=200,
        )


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    resp = crud.delete_user(db, user_id)
    if not resp:
        raise HTTPException(status_code=404, detail={
                    "status": "GE40404",
                    "error": "User not found",
                })
    return success_response(
            status_code="GS20005",
            data="User deleted",
            http_status_code=200,
        )
