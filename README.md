# Autopartes FastAPI

API para gestionar la compatibilidad de autopartes con vehículos: qué partes le quedan a qué marca/modelo/año/motor, y viceversa.

**Stack:** MySQL 8 · Python 3.12+ · FastAPI · SQLAlchemy 2 · Pydantic v2 · (próximamente) React + Vite + Axios.

## Estructura

```
autopartes-fastapi/
├── database/
│   ├── schema.sql          # Esquema MySQL (fuente de verdad: FKs, índices)
│   └── seed.sql            # Datos de ejemplo
└── backend/
    ├── .env.example        # Variables de conexión (copiar a .env)
    ├── requirements.txt
    ├── requirements-dev.txt
    ├── app/
    │   ├── main.py         # App FastAPI, CORS, registro de routers
    │   ├── core/config.py  # Settings leídos de .env (pydantic-settings)
    │   ├── db/session.py   # Engine, SessionLocal, Base, get_db
    │   ├── models.py       # Modelos SQLAlchemy: Vehicle, Part, Compatibility
    │   ├── schemas.py      # Esquemas Pydantic de entrada/salida
    │   └── api/
    │       ├── deps.py     # Dependencias compartidas: DB, paginación, 404/409
    │       └── routes/     # vehicles, parts, compatibility, search
    └── tests/test_api.py   # Pruebas con SQLite en memoria
```

## Modelo de datos

| Tabla | Clave | Índices relevantes |
|---|---|---|
| `vehicles` | `id` | `UNIQUE(make, model, year, engine, trim)` para filtrar Marca→Modelo→Año; `(year, make, model)` para filtrar por año primero |
| `parts` | `id` | `UNIQUE(sku)`, `category`, `manufacturer`, `name` |
| `part_vehicle_compatibility` | `PK(part_id, vehicle_id)` | `(vehicle_id, part_id)` para la búsqueda inversa; FKs con `ON DELETE CASCADE` |

`engine` y `trim` son `NOT NULL DEFAULT ''` porque en MySQL los `NULL` no chocan dentro de un `UNIQUE` y permitirían vehículos duplicados.

## Puesta en marcha

```bash
# 1. Base de datos
mysql -u root -p < database/schema.sql
mysql -u root -p < database/seed.sql      # opcional

# 2. Backend
cd backend
python -m venv .venv
.venv\Scripts\activate                    # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements-dev.txt
copy .env.example .env                    # y editar credenciales
fastapi dev app/main.py                   # http://localhost:8000/docs
```

Pruebas: `pytest` (dentro de `backend/`, no necesitan MySQL).

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST / GET | `/api/vehicles` | Registrar / listar vehículos (`make`, `model`, `year`, `limit`, `offset`) |
| GET | `/api/vehicles/makes` · `/models?make=` · `/years?make=&model=` | Opciones para selectores en cascada |
| GET / PATCH / DELETE | `/api/vehicles/{id}` | Detalle, edición, borrado |
| GET | `/api/vehicles/{id}/parts` | Partes compatibles con el vehículo (`category`) |
| POST / GET | `/api/parts` | Registrar / listar autopartes (`q`, `category`, `manufacturer`) |
| GET | `/api/parts/categories` · `/api/parts/sku/{sku}` | Categorías; buscar por SKU |
| GET / PATCH / DELETE | `/api/parts/{id}` | Detalle, edición, borrado |
| GET | `/api/parts/{id}/vehicles` | Vehículos compatibles con la parte |
| POST | `/api/compatibility` | Asociar `{part_id, vehicle_id, notes}` |
| DELETE | `/api/compatibility/{part_id}/{vehicle_id}` | Desasociar |
| GET | `/api/search/parts?make=&model=&year=[&engine=&category=]` | Partes por atributos del vehículo |
| GET | `/api/search/vehicles?sku=` | Vehículos por SKU de la parte |

Errores: `404` si no existe, `409` si duplica (SKU, vehículo o compatibilidad), `422` si la validación falla.
