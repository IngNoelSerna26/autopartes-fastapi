from fastapi import APIRouter, Query, Response, status
from sqlalchemy import select

from app.api.deps import DB, Limit, Offset, commit_or_409, get_or_404, paginate
from app.models import Compatibility, Part, Vehicle
from app.schemas import CompatiblePart, Page, VehicleCreate, VehicleRead, VehicleUpdate

router = APIRouter(prefix="/vehicles", tags=["Vehículos"])

DUPLICATE = "Ya existe un vehículo con esa marca/modelo/año/motor/versión"


@router.post("", response_model=VehicleRead, status_code=status.HTTP_201_CREATED)
def create_vehicle(data: VehicleCreate, db: DB):
    vehicle = Vehicle(**data.model_dump())
    db.add(vehicle)
    commit_or_409(db, DUPLICATE)
    db.refresh(vehicle)
    return vehicle


@router.get("", response_model=Page[VehicleRead])
def list_vehicles(
    db: DB,
    make: str | None = None,
    model: str | None = None,
    year: int | None = None,
    limit: Limit = 50,
    offset: Offset = 0,
):
    stmt = select(Vehicle).order_by(Vehicle.make, Vehicle.model, Vehicle.year, Vehicle.id)
    if make:
        stmt = stmt.where(Vehicle.make == make)
    if model:
        stmt = stmt.where(Vehicle.model == model)
    if year:
        stmt = stmt.where(Vehicle.year == year)
    return paginate(db, stmt, limit, offset)


# --- Catálogos para los selectores en cascada del frontend (Marca -> Modelo -> Año) ---
@router.get("/makes", response_model=list[str])
def list_makes(db: DB):
    return db.scalars(select(Vehicle.make).distinct().order_by(Vehicle.make)).all()


@router.get("/models", response_model=list[str])
def list_models(db: DB, make: str = Query(...)):
    stmt = select(Vehicle.model).where(Vehicle.make == make).distinct().order_by(Vehicle.model)
    return db.scalars(stmt).all()


@router.get("/years", response_model=list[int])
def list_years(db: DB, make: str = Query(...), model: str = Query(...)):
    stmt = (
        select(Vehicle.year)
        .where(Vehicle.make == make, Vehicle.model == model)
        .distinct()
        .order_by(Vehicle.year.desc())
    )
    return db.scalars(stmt).all()


@router.get("/{vehicle_id}", response_model=VehicleRead)
def get_vehicle(vehicle_id: int, db: DB):
    return get_or_404(db, Vehicle, vehicle_id, "Vehículo")


@router.patch("/{vehicle_id}", response_model=VehicleRead)
def update_vehicle(vehicle_id: int, data: VehicleUpdate, db: DB):
    vehicle = get_or_404(db, Vehicle, vehicle_id, "Vehículo")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(vehicle, field, value)
    commit_or_409(db, DUPLICATE)
    db.refresh(vehicle)
    return vehicle


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(vehicle_id: int, db: DB):
    db.delete(get_or_404(db, Vehicle, vehicle_id, "Vehículo"))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{vehicle_id}/parts", response_model=Page[CompatiblePart])
def list_compatible_parts(
    vehicle_id: int,
    db: DB,
    category: str | None = None,
    limit: Limit = 50,
    offset: Offset = 0,
):
    """Todas las autopartes compatibles con un vehículo."""
    get_or_404(db, Vehicle, vehicle_id, "Vehículo")
    stmt = (
        select(Part, Compatibility.notes)
        .join(Compatibility, Compatibility.part_id == Part.id)
        .where(Compatibility.vehicle_id == vehicle_id)
        .order_by(Part.category, Part.name)
    )
    if category:
        stmt = stmt.where(Part.category == category)
    return paginate(db, stmt, limit, offset)
