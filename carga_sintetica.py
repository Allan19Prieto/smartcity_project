"""Catálogo y generación/carga de datos sintéticos para PostgreSQL y MongoDB."""

import random
from datetime import datetime, timedelta, timezone

from bson.decimal128 import Decimal128
from bson.int64 import Int64
from psycopg2.extras import execute_values
from pymongo import ReplaceOne

START = datetime(2025, 1, 1, tzinfo=timezone.utc)
BATCH_SIZE = 5000


def say(message: str) -> None:
    print(f"\n{message}", flush=True)


def upsert_catalog(conn) -> None:
    with conn:
        with conn.cursor() as cur:
            execute_values(
                cur,
                "INSERT INTO categorias_sensor(id_categoria,nombre_categoria) VALUES %s "
                "ON CONFLICT(id_categoria) DO UPDATE SET nombre_categoria=EXCLUDED.nombre_categoria",
                [(1, "Movilidad"), (2, "Ambiente")],
            )
            execute_values(
                cur,
                "INSERT INTO tipos_sensor(id_tipo_sensor,nombre_tipo,id_categoria) VALUES %s "
                "ON CONFLICT(id_tipo_sensor) DO UPDATE SET nombre_tipo=EXCLUDED.nombre_tipo,id_categoria=EXCLUDED.id_categoria",
                [(1, "Estacionamiento", 1), (2, "Tráfico", 1), (3, "Ambiental", 2)],
            )
            cur.execute(
                "INSERT INTO ciudades(id_ciudad,nombre,pais,zona_horaria) VALUES (1,'SmartCity','Costa Rica','America/Costa_Rica') "
                "ON CONFLICT(id_ciudad) DO NOTHING"
            )
            execute_values(
                cur,
                "INSERT INTO ubicaciones(id_ubicacion,id_ciudad,codigo_zona,nombre_zona,distrito,latitud,longitud) VALUES %s "
                "ON CONFLICT(id_ubicacion) DO NOTHING",
                [(i, 1, f"Z{i:02}", f"Zona {i:02}", f"Distrito {(i - 1) // 5 + 1}", 9.93 + i / 1000, -84.08 - i / 1000) for i in range(1, 21)],
            )
            execute_values(
                cur,
                "INSERT INTO usuarios_sistema(id_usuario,nombre,correo) VALUES %s ON CONFLICT(id_usuario) DO NOTHING",
                [
                    (1, "Administrador del Sistema", "admin@smartcity.cr"),
                    (2, "Analista de Movilidad", "movilidad@smartcity.cr"),
                    (3, "Operador de Monitoreo", "monitoreo@smartcity.cr"),
                    (4, "Gestor Ambiental", "ambiente@smartcity.cr"),
                    (5, "Auditor Municipal", "auditoria@smartcity.cr"),
                ],
            )
            execute_values(
                cur,
                "INSERT INTO organismos_responsables(id_organismo,nombre,responsable) VALUES %s "
                "ON CONFLICT(id_organismo) DO NOTHING",
                [(i, f"Organismo {i}", None) for i in range(1, 6)],
            )
            cur.execute(
                "INSERT INTO fuentes_datos(id_fuente,nombre,version,url_origen,licencia,naturaleza_datos) "
                "VALUES (1,'Generador SmartCity del curso','1.0',NULL,'Datos sintéticos del proyecto','sintetica') "
                "ON CONFLICT(id_fuente) DO NOTHING"
            )
            execute_values(
                cur,
                "INSERT INTO variables_medicion(id_variable,codigo_variable,nombre,definicion,unidad,criterio_agregacion) VALUES %s "
                "ON CONFLICT(id_variable) DO NOTHING",
                [
                    (1, "capacidad", "Capacidad", "Capacidad total", "plazas", "max"),
                    (2, "ocupacion", "Ocupación", "Plazas ocupadas", "plazas", "avg"),
                    (3, "velocidad_media", "Velocidad media", "Velocidad del flujo", "km/h", "avg"),
                    (4, "vehiculos", "Vehículos", "Vehículos detectados", "vehículos", "sum"),
                    (5, "temperatura", "Temperatura", "Temperatura ambiental", "C", "avg"),
                ],
            )
            execute_values(
                cur,
                "INSERT INTO tipos_sensor_variables(id_tipo_sensor,id_variable) VALUES %s ON CONFLICT DO NOTHING",
                [(1, 1), (1, 2), (2, 3), (2, 4), (3, 5)],
            )
            execute_values(
                cur,
                "INSERT INTO estacionamientos(id_estacionamiento,id_fuente,id_ubicacion,codigo_origen,nombre) VALUES %s "
                "ON CONFLICT(id_estacionamiento) DO NOTHING",
                [(i, 1, i, f"P{i:03}", f"Estacionamiento {i}") for i in range(1, 21)],
            )
            execute_values(
                cur,
                "INSERT INTO rutas(id_ruta,id_fuente,id_ciudad,codigo_origen,nombre) VALUES %s ON CONFLICT(id_ruta) DO NOTHING",
                [(i, 1, 1, f"R{i:03}", f"Ruta {i}") for i in range(1, 21)],
            )
            execute_values(
                cur,
                "INSERT INTO niveles_congestion(id_nivel,codigo,nombre,orden) VALUES %s ON CONFLICT(id_nivel) DO NOTHING",
                [(1, "baja", "Baja", 1), (2, "media", "Media", 2), (3, "alta", "Alta", 3)],
            )
            sensor_rows = []
            for sensor_id in range(1, 101):
                sensor_type = 1 if sensor_id <= 30 else (2 if sensor_id <= 90 else 3)
                sensor_rows.append(
                    (sensor_id, f"S-{sensor_id:04}", f"Sensor {sensor_id:04}", sensor_type,
                     (sensor_id - 1) % 20 + 1, (sensor_id - 1) % 5 + 1,
                     datetime(2020 + sensor_id % 6, 1 + sensor_id % 12, 1).date(),
                     "inactivo" if sensor_id % 9 == 0 else "activo", "fisico")
                )
            execute_values(
                cur,
                "INSERT INTO sensores(id_sensor,codigo_sensor,nombre,id_tipo_sensor,id_ubicacion,id_organismo,fecha_instalacion,estado_administrativo,naturaleza_sensor) VALUES %s "
                "ON CONFLICT(id_sensor) DO NOTHING",
                sensor_rows,
            )
            # Reservar diez sensores ambientales sin lecturas permite demostrar sensores inactivos/sin actividad.
            cur.execute("SELECT setval(pg_get_serial_sequence('usuarios_sistema','id_usuario'), GREATEST((SELECT max(id_usuario) FROM usuarios_sistema),1))")
            cur.execute("SELECT setval(pg_get_serial_sequence('sensores','id_sensor'), GREATEST((SELECT max(id_sensor) FROM sensores),1))")
            cur.execute("SELECT setval(pg_get_serial_sequence('categorias_sensor','id_categoria'), GREATEST((SELECT max(id_categoria) FROM categorias_sensor),1))")
            cur.execute("SELECT setval(pg_get_serial_sequence('tipos_sensor','id_tipo_sensor'), GREATEST((SELECT max(id_tipo_sensor) FROM tipos_sensor),1))")
            cur.execute("SELECT setval(pg_get_serial_sequence('ciudades','id_ciudad'), GREATEST((SELECT max(id_ciudad) FROM ciudades),1))")
            cur.execute("SELECT setval(pg_get_serial_sequence('ubicaciones','id_ubicacion'), GREATEST((SELECT max(id_ubicacion) FROM ubicaciones),1))")
            cur.execute("SELECT setval(pg_get_serial_sequence('organismos_responsables','id_organismo'), GREATEST((SELECT max(id_organismo) FROM organismos_responsables),1))")
            cur.execute("SELECT setval(pg_get_serial_sequence('fuentes_datos','id_fuente'), GREATEST((SELECT max(id_fuente) FROM fuentes_datos),1))")
            cur.execute("SELECT setval(pg_get_serial_sequence('variables_medicion','id_variable'), GREATEST((SELECT max(id_variable) FROM variables_medicion),1))")
            cur.execute("SELECT setval(pg_get_serial_sequence('estacionamientos','id_estacionamiento'), GREATEST((SELECT max(id_estacionamiento) FROM estacionamientos),1))")
            cur.execute("SELECT setval(pg_get_serial_sequence('rutas','id_ruta'), GREATEST((SELECT max(id_ruta) FROM rutas),1))")
            cur.execute("SELECT setval(pg_get_serial_sequence('niveles_congestion','id_nivel'), GREATEST((SELECT max(id_nivel) FROM niveles_congestion),1))")


def reading_rows(i: int, rng: random.Random):
    sensor_id = i % 90 + 1
    sensor_type = 1 if sensor_id <= 30 else 2
    location_id = (sensor_id - 1) % 20 + 1
    dt = START + timedelta(seconds=i * 60)
    is_parking = sensor_type == 1
    if is_parking:
        capacity = 100 + location_id * 5
        # Cada centésima fila genera una ocupación alta para respaldar los eventos.
        occupancy = capacity if i % 100 == 0 else rng.randint(0, capacity)
        measurements = [
            {"id_variable": Int64(1), "codigo": "capacidad", "valor": Decimal128(str(capacity)), "unidad": "plazas"},
            {"id_variable": Int64(2), "codigo": "ocupacion", "valor": Decimal128(str(occupancy)), "unidad": "plazas"},
        ]
        raw = {"Capacity": capacity, "Occupancy": occupancy}
        context = {"id_estacionamiento": location_id}
        class_reading = "parking"
        sql_measurements = [(1, capacity), (2, occupancy)]
    else:
        # Cada centésima fila genera baja velocidad para respaldar alertas de tráfico.
        speed = 10 if i % 100 == 0 else rng.randint(5, 120)
        vehicles = rng.randint(1, 100)
        level_id = 3 if speed < 25 else (2 if speed < 55 else 1)
        measurements = [
            {"id_variable": Int64(3), "codigo": "velocidad_media", "valor": Decimal128(str(speed)), "unidad": "km/h"},
            {"id_variable": Int64(4), "codigo": "vehiculos", "valor": Decimal128(str(vehicles)), "unidad": "vehículos"},
        ]
        raw = {"Average_Speed_kmh": speed, "Vehicle_Count": vehicles}
        context = {"id_ruta": Int64(location_id), "id_nivel": Int64(level_id)}
        class_reading = "trafico"
        sql_measurements = [(3, speed), (4, vehicles)]
    context.update({"id_ubicacion": Int64(location_id), "id_ciudad": Int64(1), "id_tipo_sensor": Int64(sensor_type), "id_categoria": Int64(1), "id_organismo": Int64((sensor_id - 1) % 5 + 1)})
    context = {key: Int64(value) for key, value in context.items()}
    doc_id = f"lec:1:fila{i:07}"
    doc = {
        "_id": doc_id, "schema_version": 1, "id_fuente": Int64(1),
        "clave_origen": f"generado:fila{i:07}", "naturaleza": "sintetica", "procedencia": "simulado",
        "id_sensor": Int64(sensor_id), "tipo": class_reading, "fecha_medicion": dt,
        "fecha_recepcion": dt + timedelta(seconds=10), "contexto": context,
        "mediciones": measurements, "calidad": "valida", "raw": raw,
        "trazabilidad": {"archivo": "generador_sprint1", "fila": Int64(i), "version_ingesta": "1.0"},
    }
    sql_reading = (i, sensor_id, 1, f"generado:fila{i:07}", doc_id, dt, dt + timedelta(seconds=10), "valida", class_reading, 60)
    child = (i, location_id) if is_parking else (i, location_id, 3 if speed < 25 else (2 if speed < 55 else 1))
    return doc, sql_reading, sql_measurements, child, is_parking


def load_data(conn, database, reading_count: int = 500000) -> None:
    say(f"5/6  Cargando {reading_count:,} lecturas sintéticas en ambas bases...")
    upsert_catalog(conn)
    rng = random.Random(20261026)
    sql_insert = """
        INSERT INTO lecturas_limpias(id_sensor,id_fuente,clave_origen,id_documento_mongo,fecha_medicion,fecha_recepcion,calidad,clase_lectura,intervalo_segundos)
        VALUES %s ON CONFLICT(id_fuente,clave_origen) DO UPDATE SET clave_origen=EXCLUDED.clave_origen
        RETURNING id_lectura,clave_origen
    """
    sql_measure_insert = "INSERT INTO mediciones_limpias(id_lectura,id_variable,valor) VALUES %s ON CONFLICT DO NOTHING"
    sql_park = "INSERT INTO lecturas_parking(id_lectura,id_estacionamiento) VALUES %s ON CONFLICT DO NOTHING"
    sql_traffic = "INSERT INTO lecturas_trafico(id_lectura,id_ruta,id_nivel) VALUES %s ON CONFLICT DO NOTHING"
    collection = database.lecturas
    for start in range(1, reading_count + 1, BATCH_SIZE):
        end = min(start + BATCH_SIZE, reading_count + 1)
        docs, readings, measurements, parking_rows, traffic_rows = [], [], [], [], []
        for i in range(start, end):
            doc, row, vals, child, is_parking = reading_rows(i, rng)
            docs.append(doc)
            readings.append(row[1:])
            measurements.extend((i, var_id, value) for var_id, value in vals)
            (parking_rows if is_parking else traffic_rows).append(child)
        with conn:
            with conn.cursor() as cur:
                # PostgreSQL asigna IDs; recuperar también IDs de una ejecución anterior.
                returned = execute_values(cur, sql_insert, readings, page_size=1000, fetch=True)
                ids = {int(key.rsplit("fila", 1)[1]): rid for rid, key in returned}
                measurements = [(ids[i], var, value) for i, var, value in measurements]
                parking_rows = [(ids[row[0]], *row[1:]) for row in parking_rows]
                traffic_rows = [(ids[row[0]], *row[1:]) for row in traffic_rows]
                execute_values(cur, sql_measure_insert, measurements, page_size=2000)
                if parking_rows:
                    execute_values(cur, sql_park, parking_rows, page_size=1000)
                if traffic_rows:
                    execute_values(cur, sql_traffic, traffic_rows, page_size=1000)
        operations = [ReplaceOne({"_id": d["_id"]}, d, upsert=True) for d in docs]
        collection.bulk_write(operations, ordered=False)
        if start == 1 or end - 1 == reading_count or ((end - 1) % 50000 == 0):
            print(f"  {end - 1:,}/{reading_count:,} lecturas procesadas.", flush=True)
    # Activar los contadores SERIAL después de insertar IDs deterministas.
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT setval(pg_get_serial_sequence('lecturas_limpias','id_lectura'), GREATEST((SELECT max(id_lectura) FROM lecturas_limpias),1))")
    create_events_and_alerts(database, min(5000, reading_count // 100))
    print("  Datos listos en PostgreSQL y MongoDB.", flush=True)


def create_events_and_alerts(database, count: int) -> None:
    events, alerts, incidents = [], [], []
    for n in range(1, count + 1):
        reading_no = n * 100
        sensor_id = reading_no % 90 + 1
        location_id = (sensor_id - 1) % 20 + 1
        is_parking = sensor_id <= 30
        when = START + timedelta(seconds=reading_no * 60)
        event_id = f"evt:1:regla:fila{reading_no:07}:v1"
        lectura_id = f"lec:1:fila{reading_no:07}"
        context = {"id_ubicacion": Int64(location_id), "id_ciudad": Int64(1), "id_tipo_sensor": Int64(1 if is_parking else 2), "id_categoria": Int64(1), "id_organismo": Int64((sensor_id - 1) % 5 + 1)}
        if is_parking:
            context["id_estacionamiento"] = Int64(location_id)
            indicator, value, unit, kind = "tasa_ocupacion", 100.0, "%", "ocupacion_alta"
        else:
            context["id_ruta"], context["id_nivel"] = Int64(location_id), Int64(3)
            indicator, value, unit, kind = "velocidad_media", 10.0, "km/h", "velocidad_baja"
        events.append({
            "_id": event_id, "schema_version": 1, "id_fuente": Int64(1), "clave_origen": f"evento:{reading_no}:v1",
            "naturaleza": "sintetica", "procedencia": "derivado", "id_sensor": Int64(sensor_id),
            "id_lectura": lectura_id, "contexto": context, "tipo_evento": kind,
            "fecha_evento": when, "severidad": "critico", "detector": {"codigo": kind, "version": "1"},
            "evidencia": {"indicador": indicator, "valor": Decimal128(str(value)), "unidad": unit},
        })
        alerts.append({
            "_id": f"ale:1:{reading_no}:v1", "schema_version": 1, "id_fuente": Int64(1),
            "clave_origen": f"alerta:{reading_no}:v1", "naturaleza": "sintetica", "procedencia": "derivado",
            "id_sensor": Int64(sensor_id), "id_evento": event_id, "contexto": context,
            "fecha_emision": when + timedelta(seconds=1), "severidad": "critico", "estado": "activa",
            "regla": {"codigo": kind, "version": "1", "indicador": indicator, "operador": ">" if is_parking else "<", "umbral": Decimal128("90.0" if is_parking else "25.0"), "unidad": unit},
            "evidencia": {"valor": Decimal128(str(value)), "unidad": unit},
        })
        if n % 10 == 0:
            incidents.append({
                "_id": f"inc:1:reporte{n}", "schema_version": 1, "id_fuente": Int64(1),
                "clave_origen": f"reporte:{n}", "naturaleza": "sintetica", "procedencia": "simulado",
                "contexto": {"id_ubicacion": Int64(location_id), "id_ciudad": Int64(1)}, "categoria": "revision_sensor",
                "descripcion": "Incidente sintético para demostrar consultas", "fecha_inicio": when,
                "fecha_registro": when + timedelta(minutes=2), "estado": "abierto", "detalle": {"generado": True},
            })
    for collection_name, docs in (("eventos", events), ("alertas", alerts), ("incidentes", incidents)):
        ops = [ReplaceOne({"_id": d["_id"]}, d, upsert=True) for d in docs]
        if ops:
            database[collection_name].bulk_write(ops, ordered=False)
