-- Esquema de compatibilidad de autopartes (MySQL 8.0+, InnoDB, utf8mb4)
-- Ejecutar: mysql -u root -p < database/schema.sql

CREATE DATABASE IF NOT EXISTS autopartes
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE autopartes;

-- ---------------------------------------------------------------------------
-- vehicles: una fila por combinación marca/modelo/año/motor/versión.
-- engine y trim son NOT NULL DEFAULT '' a propósito: en MySQL los NULL no
-- chocan en un UNIQUE, y permitirían duplicar "Nissan Versa 2020" sin motor.
-- ---------------------------------------------------------------------------
CREATE TABLE vehicles (
  id          INT UNSIGNED      NOT NULL AUTO_INCREMENT,
  make        VARCHAR(50)       NOT NULL,              -- marca: Nissan
  model       VARCHAR(80)       NOT NULL,              -- modelo: Versa
  year        SMALLINT UNSIGNED NOT NULL,              -- 2020
  engine      VARCHAR(80)       NOT NULL DEFAULT '',   -- 1.6L L4
  trim        VARCHAR(80)       NOT NULL DEFAULT '',   -- versión: Advance
  created_at  TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT uq_vehicle UNIQUE (make, model, year, engine, trim),
  CONSTRAINT ck_vehicle_year CHECK (year BETWEEN 1900 AND 2100),
  -- El UNIQUE ya sirve para filtros make -> model -> year (prefijo izquierdo).
  -- Este cubre búsquedas por año primero (selector Año -> Marca -> Modelo).
  INDEX ix_vehicle_year_make_model (year, make, model)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- parts: catálogo de autopartes. sku es el código de búsqueda principal.
-- ---------------------------------------------------------------------------
CREATE TABLE parts (
  id            INT UNSIGNED NOT NULL AUTO_INCREMENT,
  sku           VARCHAR(50)  NOT NULL,
  name          VARCHAR(150) NOT NULL,
  category      VARCHAR(80)  NOT NULL,                 -- Frenos, Suspensión...
  manufacturer  VARCHAR(80)  NOT NULL,                 -- Bosch, Gates...
  description   TEXT         NULL,
  created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT uq_part_sku UNIQUE (sku),
  INDEX ix_part_category (category),
  INDEX ix_part_manufacturer (manufacturer),
  INDEX ix_part_name (name)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- part_vehicle_compatibility: relación N:M.
-- La PK (part_id, vehicle_id) resuelve "¿a qué vehículos le queda esta parte?"
-- y el índice inverso (vehicle_id, part_id) resuelve "¿qué partes le quedan a
-- este vehículo?" sin tocar la tabla base (índices cubrientes).
-- ON DELETE CASCADE: borrar un vehículo o parte limpia sus compatibilidades.
-- ---------------------------------------------------------------------------
CREATE TABLE part_vehicle_compatibility (
  part_id     INT UNSIGNED NOT NULL,
  vehicle_id  INT UNSIGNED NOT NULL,
  notes       VARCHAR(255) NULL,                       -- "Solo eje delantero"
  created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (part_id, vehicle_id),
  INDEX ix_compat_vehicle_part (vehicle_id, part_id),
  CONSTRAINT fk_compat_part FOREIGN KEY (part_id)
    REFERENCES parts (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_compat_vehicle FOREIGN KEY (vehicle_id)
    REFERENCES vehicles (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;
