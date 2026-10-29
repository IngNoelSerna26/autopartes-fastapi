"""Modelos SQLAlchemy. Reflejan database/schema.sql (que es la fuente de verdad en MySQL)."""

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Vehicle(Base):
    __tablename__ = "vehicles"
    __table_args__ = (
        UniqueConstraint("make", "model", "year", "engine", "trim", name="uq_vehicle"),
        CheckConstraint("year BETWEEN 1900 AND 2100", name="ck_vehicle_year"),
        Index("ix_vehicle_year_make_model", "year", "make", "model"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    make: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(80))
    year: Mapped[int] = mapped_column(SmallInteger)
    engine: Mapped[str] = mapped_column(String(80), default="", server_default="")
    trim: Mapped[str] = mapped_column(String(80), default="", server_default="")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    compatibilities: Mapped[list["Compatibility"]] = relationship(
        back_populates="vehicle", cascade="all, delete-orphan", passive_deletes=True
    )


class Part(Base):
    __tablename__ = "parts"
    __table_args__ = (
        Index("ix_part_category", "category"),
        Index("ix_part_manufacturer", "manufacturer"),
        Index("ix_part_name", "name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(150))
    category: Mapped[str] = mapped_column(String(80))
    manufacturer: Mapped[str] = mapped_column(String(80))
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    compatibilities: Mapped[list["Compatibility"]] = relationship(
        back_populates="part", cascade="all, delete-orphan", passive_deletes=True
    )


class Compatibility(Base):
    __tablename__ = "part_vehicle_compatibility"
    __table_args__ = (Index("ix_compat_vehicle_part", "vehicle_id", "part_id"),)

    part_id: Mapped[int] = mapped_column(
        ForeignKey("parts.id", ondelete="CASCADE"), primary_key=True
    )
    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicles.id", ondelete="CASCADE"), primary_key=True
    )
    notes: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    part: Mapped[Part] = relationship(back_populates="compatibilities")
    vehicle: Mapped[Vehicle] = relationship(back_populates="compatibilities")
