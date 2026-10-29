"""Búsquedas por atributos (sin conocer IDs): lo que usa el buscador del frontend."""

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from app.api.deps import DB, Limit, Offset, paginate
from app.models import Compatibility, Part, Vehicle
from app.schemas import CompatiblePart, CompatibleVehicle, Page

router = APIRouter(prefix="/search", tags=["Búsqueda"])


@router.get("/parts", response_model=Page[CompatiblePart])
def parts_for_vehicle(
    db: DB,
    make: str = Query(..., examples=["Nissan"]),
    model: str = Query(..., examples=["Versa"]),
    year: int = Query(..., examples=[2020]),
    engine: str | None = None,
    category: str | None = None,
    limit: Limit = 50,
    offset: Offset = 0,
):
    """Autopartes compatibles con un vehículo dado por marca/modelo/año (y opcionalmente motor)."""
    # GROUP BY Part.id deduplica partes que aplican a varias versiones del mismo
    # año/modelo; MySQL lo acepta con ONLY_FULL_GROUP_BY porque id es la PK.
    stmt = (
        select(Part, func.max(Compatibility.notes))
        .join(Compatibility, Compatibility.part_id == Part.id)
        .join(Vehicle, Vehicle.id == Compatibility.vehicle_id)
        .where(Vehicle.make == make, Vehicle.model == model, Vehicle.year == year)
        .group_by(Part.id)
        .order_by(Part.category, Part.name)
    )
    if engine:
        stmt = stmt.where(Vehicle.engine == engine)
    if category:
        stmt = stmt.where(Part.category == category)
    return paginate(db, stmt, limit, offset)


@router.get("/vehicles", response_model=Page[CompatibleVehicle])
def vehicles_for_part(
    db: DB,
    sku: str = Query(..., examples=["GAT-26600"]),
    limit: Limit = 50,
    offset: Offset = 0,
):
    """Vehículos compatibles con una autoparte dada por SKU."""
    stmt = (
        select(Vehicle, Compatibility.notes)
        .join(Compatibility, Compatibility.vehicle_id == Vehicle.id)
        .join(Part, Part.id == Compatibility.part_id)
        .where(Part.sku == sku)
        .order_by(Vehicle.make, Vehicle.model, Vehicle.year)
    )
    return paginate(db, stmt, limit, offset)
