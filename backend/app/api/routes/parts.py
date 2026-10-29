from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import or_, select

from app.api.deps import DB, Limit, Offset, commit_or_409, get_or_404, paginate
from app.models import Compatibility, Part, Vehicle
from app.schemas import CompatibleVehicle, Page, PartCreate, PartRead, PartUpdate

router = APIRouter(prefix="/parts", tags=["Autopartes"])

DUPLICATE = "Ya existe una autoparte con ese SKU"


@router.post("", response_model=PartRead, status_code=status.HTTP_201_CREATED)
def create_part(data: PartCreate, db: DB):
    part = Part(**data.model_dump())
    db.add(part)
    commit_or_409(db, DUPLICATE)
    db.refresh(part)
    return part


@router.get("", response_model=Page[PartRead])
def list_parts(
    db: DB,
    q: str | None = None,
    category: str | None = None,
    manufacturer: str | None = None,
    limit: Limit = 50,
    offset: Offset = 0,
):
    """`q` busca por prefijo de SKU o por texto en el nombre."""
    stmt = select(Part).order_by(Part.sku)
    if q:
        stmt = stmt.where(or_(Part.sku.startswith(q), Part.name.contains(q)))
    if category:
        stmt = stmt.where(Part.category == category)
    if manufacturer:
        stmt = stmt.where(Part.manufacturer == manufacturer)
    return paginate(db, stmt, limit, offset)


@router.get("/categories", response_model=list[str])
def list_categories(db: DB):
    return db.scalars(select(Part.category).distinct().order_by(Part.category)).all()


@router.get("/sku/{sku}", response_model=PartRead)
def get_part_by_sku(sku: str, db: DB):
    part = db.scalar(select(Part).where(Part.sku == sku))
    if part is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"SKU {sku} no existe")
    return part


@router.get("/{part_id}", response_model=PartRead)
def get_part(part_id: int, db: DB):
    return get_or_404(db, Part, part_id, "Autoparte")


@router.patch("/{part_id}", response_model=PartRead)
def update_part(part_id: int, data: PartUpdate, db: DB):
    part = get_or_404(db, Part, part_id, "Autoparte")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(part, field, value)
    commit_or_409(db, DUPLICATE)
    db.refresh(part)
    return part


@router.delete("/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_part(part_id: int, db: DB):
    db.delete(get_or_404(db, Part, part_id, "Autoparte"))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{part_id}/vehicles", response_model=Page[CompatibleVehicle])
def list_compatible_vehicles(part_id: int, db: DB, limit: Limit = 50, offset: Offset = 0):
    """Todos los vehículos compatibles con una autoparte."""
    get_or_404(db, Part, part_id, "Autoparte")
    stmt = (
        select(Vehicle, Compatibility.notes)
        .join(Compatibility, Compatibility.vehicle_id == Vehicle.id)
        .where(Compatibility.part_id == part_id)
        .order_by(Vehicle.make, Vehicle.model, Vehicle.year)
    )
    return paginate(db, stmt, limit, offset)
