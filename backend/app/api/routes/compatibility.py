from fastapi import APIRouter, HTTPException, Response, status

from app.api.deps import DB, commit_or_409, get_or_404
from app.models import Compatibility, Part, Vehicle
from app.schemas import CompatibilityCreate, CompatibilityRead

router = APIRouter(prefix="/compatibility", tags=["Compatibilidad"])


@router.post("", response_model=CompatibilityRead, status_code=status.HTTP_201_CREATED)
def associate(data: CompatibilityCreate, db: DB):
    """Asocia una autoparte con un vehículo."""
    get_or_404(db, Part, data.part_id, "Autoparte")
    get_or_404(db, Vehicle, data.vehicle_id, "Vehículo")
    if db.get(Compatibility, (data.part_id, data.vehicle_id)):
        raise HTTPException(status.HTTP_409_CONFLICT, "La compatibilidad ya existe")
    link = Compatibility(**data.model_dump())
    db.add(link)
    commit_or_409(db, "La compatibilidad ya existe")
    db.refresh(link)
    return link


@router.delete("/{part_id}/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def dissociate(part_id: int, vehicle_id: int, db: DB):
    """Elimina la compatibilidad entre una autoparte y un vehículo."""
    link = db.get(Compatibility, (part_id, vehicle_id))
    if link is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "La compatibilidad no existe")
    db.delete(link)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
