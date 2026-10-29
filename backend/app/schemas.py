"""Esquemas Pydantic (entrada/salida de la API)."""

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --- Vehículos -------------------------------------------------------------
class VehicleBase(BaseModel):
    make: str = Field(..., min_length=1, max_length=50, examples=["Nissan"])
    model: str = Field(..., min_length=1, max_length=80, examples=["Versa"])
    year: int = Field(..., ge=1900, le=2100, examples=[2020])
    engine: str = Field("", max_length=80, examples=["1.6L L4"])
    trim: str = Field("", max_length=80, examples=["Advance"])


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    make: str | None = Field(None, min_length=1, max_length=50)
    model: str | None = Field(None, min_length=1, max_length=80)
    year: int | None = Field(None, ge=1900, le=2100)
    engine: str | None = Field(None, max_length=80)
    trim: str | None = Field(None, max_length=80)


class VehicleRead(VehicleBase, ORMModel):
    id: int
    created_at: datetime


# --- Autopartes ------------------------------------------------------------
class PartBase(BaseModel):
    sku: str = Field(..., min_length=1, max_length=50, examples=["GAT-26600"])
    name: str = Field(..., min_length=1, max_length=150, examples=["Banda serpentina"])
    category: str = Field(..., min_length=1, max_length=80, examples=["Motor"])
    manufacturer: str = Field(..., min_length=1, max_length=80, examples=["Gates"])
    description: str | None = None


class PartCreate(PartBase):
    pass


class PartUpdate(BaseModel):
    sku: str | None = Field(None, min_length=1, max_length=50)
    name: str | None = Field(None, min_length=1, max_length=150)
    category: str | None = Field(None, min_length=1, max_length=80)
    manufacturer: str | None = Field(None, min_length=1, max_length=80)
    description: str | None = None


class PartRead(PartBase, ORMModel):
    id: int
    created_at: datetime


# --- Compatibilidad --------------------------------------------------------
class CompatibilityCreate(BaseModel):
    part_id: int
    vehicle_id: int
    notes: str | None = Field(None, max_length=255, examples=["Solo eje delantero"])


class CompatibilityRead(ORMModel):
    part_id: int
    vehicle_id: int
    notes: str | None
    created_at: datetime


class CompatiblePart(PartRead):
    notes: str | None = None


class CompatibleVehicle(VehicleRead):
    notes: str | None = None


T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    total: int
    limit: int
    offset: int
    items: list[T]
