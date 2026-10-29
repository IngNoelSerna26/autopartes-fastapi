from typing import Annotated

from fastapi import Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from app.db.session import get_db

DB = Annotated[Session, Depends(get_db)]
Limit = Annotated[int, Query(ge=1, le=200)]
Offset = Annotated[int, Query(ge=0)]


def get_or_404(db: Session, model, obj_id: int, label: str):
    obj = db.get(model, obj_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"{label} {obj_id} no existe")
    return obj


def commit_or_409(db: Session, detail: str) -> None:
    """Commit; si viola un UNIQUE/FK devuelve 409 en vez de un 500."""
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, detail) from None


def paginate(db: Session, stmt: Select, limit: int, offset: int) -> dict:
    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery()))
    rows = db.execute(stmt.limit(limit).offset(offset)).all()
    # Filas de una sola entidad -> el objeto; filas (entidad, notes) -> se combinan.
    items = [row[0] if len(row) == 1 else {**_as_dict(row[0]), "notes": row[1]} for row in rows]
    return {"total": total, "limit": limit, "offset": offset, "items": items}


def _as_dict(obj) -> dict:
    return {c.key: getattr(obj, c.key) for c in obj.__table__.columns}
