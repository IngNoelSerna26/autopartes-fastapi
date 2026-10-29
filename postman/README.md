# Pruebas con Postman

`autopartes.postman_collection.json` trae 40 peticiones con 63 aserciones que recorren toda la API: alta, consulta, edición, compatibilidades, búsquedas, errores esperados y limpieza.

## Importar

1. Postman → **Import** → elige `postman/autopartes.postman_collection.json`.
2. En la pestaña **Variables** de la colección, ajusta `baseUrl` si la API no corre en `http://localhost:8000/api`.

## Ejecutar

**Toda la colección:** clic derecho en la colección → **Run collection** → **Run**. El orden importa: cada petición guarda IDs (`vehicleId`, `vehicleId2`, `partId`, `partSku`) que usan las siguientes.

- Se puede correr las veces que quieras: los datos de prueba llevan un sufijo único (`runId`, generado en *Health check*), así que no chocan con corridas anteriores ni con tus datos.
- La carpeta **6. Limpieza** borra lo que creó la corrida.

**Peticiones sueltas:** ejecuta primero *Health check*, *Registrar vehículo*, *Registrar segundo vehículo* y *Registrar autoparte*, para que existan las variables.

**Desde terminal (CI):**

```bash
npx newman run postman/autopartes.postman_collection.json
```

## Qué se prueba

| Carpeta | Casos |
|---|---|
| 0. Sistema | `GET /api/health` |
| 1. Vehículos | Alta (201), duplicado (409), año fuera de rango (422), listado con filtros y paginación, selectores marca/modelo/año, detalle, PATCH, inexistente (404) |
| 2. Autopartes | Alta (201), SKU duplicado (409), campos faltantes (422), búsqueda `q`, filtros por categoría y fabricante, categorías, por SKU, por ID, PATCH, SKU inexistente (404) |
| 3. Compatibilidad | Asociar (201) con notas, segunda asociación, duplicada (409), parte inexistente (404) |
| 4. Búsqueda | Partes de un vehículo por ID, vehículos de una parte por ID, partes por marca/modelo/año (con y sin categoría), falta el año (422), vehículos por SKU |
| 5. Desasociar | Desasociar (204), repetir (404), verificar conteo |
| 6. Limpieza | Borrar vehículo y comprobar el `ON DELETE CASCADE`, borrar el resto, verificar 404 |

## Ejemplos de cuerpo

```jsonc
// POST /api/vehicles
{ "make": "Nissan", "model": "Versa", "year": 2020, "engine": "1.6L L4", "trim": "Advance" }

// POST /api/parts
{ "sku": "GAT-26600", "name": "Banda serpentina", "category": "Motor", "manufacturer": "Gates", "description": null }

// POST /api/compatibility
{ "part_id": 2, "vehicle_id": 1, "notes": "Solo motor 1.6" }
```

Las respuestas de listado tienen la forma `{ "total", "limit", "offset", "items": [...] }`. Los errores vienen como `{ "detail": "mensaje" }`.
