-- Ejecutar desde pgAdmin: Tools > Query Tool. Seleccionar una consulta y F5.

-- 1. Sensores por tipo
SELECT t.nombre_tipo, COUNT(*) AS cantidad
FROM sensores s
JOIN tipos_sensor t ON t.id_tipo_sensor = s.id_tipo_sensor
GROUP BY t.nombre_tipo
ORDER BY cantidad DESC;

-- 2. Sensores por ubicación
SELECT u.nombre_zona, COUNT(s.id_sensor) AS cantidad
FROM ubicaciones u
LEFT JOIN sensores s ON s.id_ubicacion = u.id_ubicacion
GROUP BY u.nombre_zona
ORDER BY cantidad DESC;

-- 3. Sensores activos e inactivos
SELECT estado_administrativo, COUNT(*) AS cantidad
FROM sensores
GROUP BY estado_administrativo
ORDER BY estado_administrativo;

-- 4. Sensores por organismo responsable
SELECT o.nombre, COUNT(s.id_sensor) AS cantidad
FROM organismos_responsables o
LEFT JOIN sensores s ON s.id_organismo = o.id_organismo
GROUP BY o.nombre
ORDER BY cantidad DESC;

-- 5. Zonas con mayor cantidad de sensores
SELECT u.nombre_zona, COUNT(s.id_sensor) AS cantidad
FROM ubicaciones u
LEFT JOIN sensores s ON s.id_ubicacion = u.id_ubicacion
GROUP BY u.nombre_zona
ORDER BY cantidad DESC, u.nombre_zona
FETCH FIRST 5 ROWS ONLY;

-- 6. Sensores instalados por año
SELECT EXTRACT(YEAR FROM fecha_instalacion) AS anio, COUNT(*) AS cantidad
FROM sensores
WHERE fecha_instalacion IS NOT NULL
GROUP BY EXTRACT(YEAR FROM fecha_instalacion)
ORDER BY anio;

-- 7. Sensores sin actividad registrada
SELECT s.id_sensor, s.codigo_sensor
FROM sensores s
WHERE NOT EXISTS (
    SELECT 1
    FROM lecturas_limpias l
    WHERE l.id_sensor = s.id_sensor
)
ORDER BY s.id_sensor;

-- 8. Ranking de zonas monitoreadas (CTE y función de ventana)
WITH conteo AS (
    SELECT u.nombre_zona, COUNT(l.id_lectura) AS lecturas
    FROM ubicaciones u
    JOIN sensores s ON s.id_ubicacion = u.id_ubicacion
    LEFT JOIN lecturas_limpias l ON l.id_sensor = s.id_sensor
    GROUP BY u.nombre_zona
)
SELECT nombre_zona, lecturas,
       DENSE_RANK() OVER (ORDER BY lecturas DESC) AS ranking
FROM conteo
ORDER BY ranking, nombre_zona;

-- 9. Última lectura por sensor (vista)
SELECT *
FROM vw_ultima_lectura_sensor
ORDER BY cantidad_lecturas DESC
FETCH FIRST 20 ROWS ONLY;

-- 10. Sensores de un tipo (función)
SELECT *
FROM fn_sensores_por_tipo(1);

-- Consulta adicional: agregados por sensor y variable
SELECT l.id_sensor, v.codigo_variable, COUNT(*) AS lecturas,
       SUM(m.valor) AS suma, AVG(m.valor) AS promedio,
       MIN(m.valor) AS minimo, MAX(m.valor) AS maximo
FROM mediciones_limpias m
JOIN lecturas_limpias l ON l.id_lectura = m.id_lectura
JOIN variables_medicion v ON v.id_variable = m.id_variable
GROUP BY l.id_sensor, v.codigo_variable
ORDER BY lecturas DESC
FETCH FIRST 10 ROWS ONLY;

-- Consulta adicional sobre columnas indexadas por sensor y fecha
SELECT id_lectura, fecha_medicion
FROM lecturas_limpias
WHERE id_sensor = 1
ORDER BY fecha_medicion DESC
FETCH FIRST 5 ROWS ONLY;

-- 11. Ejecución de Procedimiento Almacenado
CALL pr_cambiar_estado_sensor(1, 'activo');

-- ========================================================
-- CONSULTAS DE NEGOCIO DEL ENUNCIADO (Pág. 9)
-- ========================================================

-- Pregunta de Negocio 1: ¿Cuál zona registra mayor cantidad de vehículos?
SELECT u.nombre_zona, SUM(m.valor) AS total_vehiculos
FROM mediciones_limpias m
JOIN variables_medicion v ON v.id_variable = m.id_variable
JOIN lecturas_limpias l ON l.id_lectura = m.id_lectura
JOIN sensores s ON s.id_sensor = l.id_sensor
JOIN ubicaciones u ON u.id_ubicacion = s.id_ubicacion
WHERE v.codigo_variable = 'vehiculos'
GROUP BY u.nombre_zona
ORDER BY total_vehiculos DESC
FETCH FIRST 1 ROWS ONLY;

-- Pregunta de Negocio 2: ¿Cuál es la hora de mayor congestión?
SELECT EXTRACT(HOUR FROM l.fecha_medicion) AS hora_del_dia,
       COUNT(*) AS lecturas_congestionadas
FROM lecturas_trafico lt
JOIN lecturas_limpias l ON l.id_lectura = lt.id_lectura
JOIN niveles_congestion nc ON nc.id_nivel = lt.id_nivel
WHERE nc.codigo = 'alta'
GROUP BY EXTRACT(HOUR FROM l.fecha_medicion)
ORDER BY lecturas_congestionadas DESC
FETCH FIRST 1 ROWS ONLY;

-- Pregunta de Negocio 3: ¿Qué rutas presentan mayor utilización?
SELECT r.nombre AS ruta, COUNT(lt.id_lectura) AS total_registros,
       AVG(m.valor) AS velocidad_promedio
FROM lecturas_trafico lt
JOIN rutas r ON r.id_ruta = lt.id_ruta
JOIN lecturas_limpias l ON l.id_lectura = lt.id_lectura
LEFT JOIN mediciones_limpias m ON m.id_lectura = l.id_lectura AND m.id_variable = 3
GROUP BY r.nombre
ORDER BY total_registros DESC
FETCH FIRST 5 ROWS ONLY;
