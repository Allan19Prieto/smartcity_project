-- Abrir en pgAdmin: Tools > Query Tool. Ejecutar una consulta seleccionada con F5.

-- Sensores por tipo
SELECT t.nombre_tipo, count(*) AS cantidad
FROM sensores s JOIN tipos_sensor t USING (id_tipo_sensor)
GROUP BY t.nombre_tipo ORDER BY cantidad DESC;

-- Sensores por zona
SELECT u.nombre_zona, count(s.id_sensor) AS cantidad
FROM ubicaciones u LEFT JOIN sensores s USING (id_ubicacion)
GROUP BY u.nombre_zona ORDER BY cantidad DESC;

-- Conteo de lecturas por zona y variable; conserva unidades comparables
SELECT u.nombre_zona, v.codigo_variable, count(*) AS cantidad,
       avg(m.valor) AS promedio, min(m.valor) AS minimo, max(m.valor) AS maximo
FROM mediciones_limpias m
JOIN lecturas_limpias l USING (id_lectura)
JOIN sensores s USING (id_sensor)
JOIN ubicaciones u USING (id_ubicacion)
JOIN variables_medicion v USING (id_variable)
GROUP BY u.nombre_zona, v.codigo_variable
ORDER BY u.nombre_zona, v.codigo_variable;

-- Sensores que no tienen lecturas
SELECT s.id_sensor, s.codigo_sensor
FROM sensores s
WHERE NOT EXISTS (SELECT 1 FROM lecturas_limpias l WHERE l.id_sensor = s.id_sensor)
ORDER BY s.id_sensor;

-- CTE y función de ventana: ranking de zonas por lecturas
WITH conteo AS (
    SELECT u.nombre_zona, count(l.id_lectura) AS lecturas
    FROM ubicaciones u
    JOIN sensores s USING (id_ubicacion)
    LEFT JOIN lecturas_limpias l USING (id_sensor)
    GROUP BY u.nombre_zona
)
SELECT nombre_zona, lecturas,
       dense_rank() OVER (ORDER BY lecturas DESC) AS ranking
FROM conteo ORDER BY ranking, nombre_zona;

-- Vista
SELECT * FROM vw_ultima_lectura_sensor ORDER BY cantidad_lecturas DESC LIMIT 20;

-- Función almacenada
SELECT * FROM fn_sensores_por_tipo(1);

-- Plan de consulta: debe poder aprovechar ix_lecturas_sensor_fecha
EXPLAIN SELECT id_lectura
FROM lecturas_limpias
WHERE id_sensor = 1
ORDER BY fecha_medicion DESC LIMIT 5;
