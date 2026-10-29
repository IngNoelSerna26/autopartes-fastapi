-- Datos de ejemplo. Ejecutar después de schema.sql.
USE autopartes;

INSERT INTO vehicles (make, model, year, engine, trim) VALUES
  ('Nissan',     'Versa',  2020, '1.6L L4', 'Advance'),
  ('Nissan',     'Versa',  2021, '1.6L L4', 'Sense'),
  ('Volkswagen', 'Jetta',  2019, '1.4L L4 Turbo', 'Comfortline'),
  ('Chevrolet',  'Aveo',   2018, '1.6L L4', 'LT');

INSERT INTO parts (sku, name, category, manufacturer, description) VALUES
  ('BOS-0986AB1234', 'Balatas delanteras cerámicas', 'Frenos',    'Bosch', 'Juego de 4 piezas'),
  ('GAT-26600',      'Banda serpentina',             'Motor',     'Gates', NULL),
  ('MON-72950',      'Amortiguador delantero',       'Suspensión','Monroe', NULL),
  ('FRA-PH6607',     'Filtro de aceite',             'Filtros',   'Fram',  NULL);

INSERT INTO part_vehicle_compatibility (part_id, vehicle_id, notes) VALUES
  (1, 1, 'Eje delantero'), (1, 2, 'Eje delantero'),
  (2, 1, NULL), (2, 2, NULL),
  (3, 3, NULL),
  (4, 1, NULL), (4, 2, NULL), (4, 4, NULL);
