import os

# Las pruebas usan SQLite en memoria; debe definirse antes de importar la app.
os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.pool import StaticPool

from app.db import session as db_session

db_session.engine = db_session.create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
event.listen(db_session.engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
db_session.SessionLocal.configure(bind=db_session.engine)

from app import models  # noqa: E402,F401  (registra las tablas)
from app.main import app  # noqa: E402


@pytest.fixture
def client():
    db_session.Base.metadata.create_all(db_session.engine)
    yield TestClient(app)
    db_session.Base.metadata.drop_all(db_session.engine)


def make_vehicle(client, **kw):
    data = {"make": "Nissan", "model": "Versa", "year": 2020, "engine": "1.6L L4"} | kw
    r = client.post("/api/vehicles", json=data)
    assert r.status_code == 201, r.text
    return r.json()


def make_part(client, sku="GAT-26600", **kw):
    data = {"sku": sku, "name": "Banda", "category": "Motor", "manufacturer": "Gates"} | kw
    r = client.post("/api/parts", json=data)
    assert r.status_code == 201, r.text
    return r.json()


def link(client, part, vehicle, notes=None):
    return client.post(
        "/api/compatibility",
        json={"part_id": part["id"], "vehicle_id": vehicle["id"], "notes": notes},
    )


def test_vehicle_crud_and_duplicates(client):
    v = make_vehicle(client)
    assert client.get(f"/api/vehicles/{v['id']}").json()["model"] == "Versa"
    assert client.post("/api/vehicles", json={"make": "Nissan", "model": "Versa", "year": 2020,
                                              "engine": "1.6L L4"}).status_code == 409
    assert client.post("/api/vehicles", json={"make": "X", "model": "Y", "year": 1800}).status_code == 422
    r = client.patch(f"/api/vehicles/{v['id']}", json={"trim": "Advance"})
    assert r.json()["trim"] == "Advance"
    assert client.get("/api/vehicles", params={"year": 2020}).json()["total"] == 1
    assert client.delete(f"/api/vehicles/{v['id']}").status_code == 204
    assert client.get(f"/api/vehicles/{v['id']}").status_code == 404


def test_cascading_selectors(client):
    make_vehicle(client, year=2020)
    make_vehicle(client, year=2021)
    make_vehicle(client, make="Chevrolet", model="Aveo", year=2018)
    assert client.get("/api/vehicles/makes").json() == ["Chevrolet", "Nissan"]
    assert client.get("/api/vehicles/models", params={"make": "Nissan"}).json() == ["Versa"]
    assert client.get("/api/vehicles/years", params={"make": "Nissan", "model": "Versa"}).json() == [2021, 2020]


def test_part_crud_and_sku(client):
    p = make_part(client)
    assert client.post("/api/parts", json={"sku": "GAT-26600", "name": "a", "category": "b",
                                           "manufacturer": "c"}).status_code == 409
    assert client.get("/api/parts/sku/GAT-26600").json()["id"] == p["id"]
    assert client.get("/api/parts", params={"q": "GAT"}).json()["total"] == 1
    assert client.get("/api/parts/categories").json() == ["Motor"]


def test_compatibility_both_directions(client):
    versa = make_vehicle(client)
    versa_sense = make_vehicle(client, trim="Sense")
    aveo = make_vehicle(client, make="Chevrolet", model="Aveo", year=2018)
    banda = make_part(client)
    balata = make_part(client, sku="BOS-1", name="Balatas", category="Frenos", manufacturer="Bosch")

    assert link(client, banda, versa, "Solo 1.6").status_code == 201
    assert link(client, banda, versa_sense).status_code == 201
    assert link(client, balata, versa).status_code == 201
    assert link(client, banda, aveo).status_code == 201
    assert link(client, banda, versa).status_code == 409
    assert client.post("/api/compatibility", json={"part_id": 999, "vehicle_id": versa["id"]}).status_code == 404

    parts = client.get(f"/api/vehicles/{versa['id']}/parts").json()
    assert [p["sku"] for p in parts["items"]] == ["BOS-1", "GAT-26600"]
    assert parts["items"][1]["notes"] == "Solo 1.6"
    assert client.get(f"/api/vehicles/{versa['id']}/parts", params={"category": "Frenos"}).json()["total"] == 1

    vehicles = client.get(f"/api/parts/{banda['id']}/vehicles").json()
    assert vehicles["total"] == 3

    # Búsqueda por atributos: la banda le queda a 2 versiones del Versa 2020 pero sale una vez.
    found = client.get("/api/search/parts", params={"make": "Nissan", "model": "Versa", "year": 2020}).json()
    assert found["total"] == 2
    assert sorted(p["sku"] for p in found["items"]) == ["BOS-1", "GAT-26600"]
    assert client.get("/api/search/vehicles", params={"sku": "GAT-26600"}).json()["total"] == 3

    assert client.delete(f"/api/compatibility/{banda['id']}/{aveo['id']}").status_code == 204
    assert client.delete(f"/api/compatibility/{banda['id']}/{aveo['id']}").status_code == 404

    # Borrar un vehículo limpia sus compatibilidades (ON DELETE CASCADE).
    client.delete(f"/api/vehicles/{versa['id']}")
    assert client.get(f"/api/parts/{balata['id']}/vehicles").json()["total"] == 0
