"""Importación validada de parking y estadísticas anuales; no inventa rutas."""
import csv
import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal, DecimalException, InvalidOperation
from pathlib import Path
from zoneinfo import ZoneInfo

from bson.decimal128 import Decimal128
from bson.int64 import Int64
from psycopg2.extras import execute_values
from pymongo import ReplaceOne

PARKING = ['SystemCodeNumber', 'Capacity', 'Occupancy', 'LastUpdated']
TRAFFIC = ['City', 'Year', 'Average_Daily_Traffic_Counts', 'Peak_Hourly_Traffic_Volume',
           'Percentage_of_Commercial_Vehicles', 'Number_of_Road_Accidents',
           'Average_Traffic_Speed_kmh', 'Air_Quality_Index', 'Population_Million']
# Códigos propios: no confundir promedios anuales con conteos de sensores por minuto.
METRICS = [
    ('trafico_promedio_diario_anual', 'vehículos/día'),
    ('trafico_volumen_hora_pico_anual', 'vehículos/hora'),
    ('trafico_porcentaje_comerciales_anual', '%'),
    ('trafico_accidentes_anuales', 'accidentes/año'),
    ('trafico_velocidad_media_anual', 'km/h'),
    ('trafico_indice_calidad_aire_anual', 'índice'),
    ('trafico_poblacion_millones_anual', 'millones de personas'),
]


def number(value):
    try:
        result = Decimal(value.strip().replace(',', '.'))
    except (InvalidOperation, AttributeError) as exc:
        raise ValueError(f'Número inválido: {value!r}') from exc
    if not result.is_finite() or result < 0:
        raise ValueError(f'Número no finito o negativo: {value!r}')
    Decimal128(result)  # Comprobar representabilidad antes de escribir en PostgreSQL.
    return result


def integer(value):
    result = number(value)
    if result != result.to_integral_value():
        raise ValueError(f'Se esperaba un entero: {value!r}')
    return int(result)


def measurement(raw, field, errors, whole=False, maximum=None):
    """Una medición inválida se conserva en raw, pero no en mediciones limpias."""
    try:
        value = number(raw)
        if whole and value != value.to_integral_value():
            raise ValueError('Se esperaba un entero')
        if maximum is not None and value > maximum:
            raise ValueError(f'Valor superior a {maximum}')
        return value
    except (ValueError, DecimalException, OverflowError) as exc:
        errors.append({'campo': field, 'motivo': str(exc)})
        return None


def parse_files(folder: Path, parking_timezone='UTC'):
    """Valida ambos archivos antes de cargar. Las mediciones inválidas se excluyen; errores de identidad o estructura detienen la carga."""
    result = []
    tz = ZoneInfo(parking_timezone)
    for filename, delimiter, fields in [('parking.csv', ',', PARKING), ('trafico.csv', ';', TRAFFIC)]:
        seen = {}
        with (folder / filename).open(encoding='utf-8-sig', newline='') as stream:
            reader = csv.DictReader(stream, delimiter=delimiter)
            if reader.fieldnames != fields:
                raise ValueError(f'{filename}: encabezado esperado: {delimiter.join(fields)}')
            for row in reader:
                line = reader.line_num
                try:
                    if None in row or any(v is None for v in row.values()):
                        raise ValueError('Faltan valores o sobran columnas')
                    errors = []
                    if filename == 'parking.csv':
                        name = row['SystemCodeNumber'].strip()
                        if not name:
                            raise ValueError('SystemCodeNumber vacío')
                        capacity = measurement(row['Capacity'], 'Capacity', errors, whole=True)
                        occupancy = measurement(row['Occupancy'], 'Occupancy', errors, whole=True)
                        if capacity is not None and occupancy is not None and occupancy > capacity:
                            errors.append({'campo': 'Occupancy', 'motivo': 'Occupancy supera Capacity; no se puede determinar cuál es incorrecto'})
                            # Ambas mediciones son dudosas: ninguna pasa a las mediciones limpias.
                            capacity = occupancy = None
                        local = datetime.strptime(row['LastUpdated'].strip(), '%Y-%m-%d %H:%M:%S')
                        dt = local.replace(tzinfo=tz).astimezone(timezone.utc)
                        vals = [capacity, occupancy]
                        key = json.dumps([name, row['LastUpdated'].strip()], ensure_ascii=False)
                        year = None
                    else:
                        name = row['City'].strip()
                        if not name:
                            raise ValueError('City vacío')
                        year = integer(row['Year'])
                        if not 1 <= year <= 9998:
                            raise ValueError('Year debe estar entre 1 y 9998')
                        dt = datetime(year, 1, 1, tzinfo=timezone.utc)
                        vals = [measurement(row[field], field, errors,
                                            whole=(field == 'Number_of_Road_Accidents'),
                                            maximum=100 if field == 'Percentage_of_Commercial_Vehicles' else None)
                                for field in TRAFFIC[2:]]
                        key = json.dumps([name, year], ensure_ascii=False)
                    if key in seen:
                        if seen[key] != row:
                            raise ValueError('Clave duplicada con valores diferentes')
                        continue
                    seen[key] = row
                    quality = 'valida' if not errors else ('parcial' if any(v is not None for v in vals) else 'sin_valores_validos')
                    result.append(dict(file=filename, line=line, name=name, key=key,
                                       dt=dt, vals=vals, raw=row, year=year, errors=errors, quality=quality))
                except (ValueError, InvalidOperation, OverflowError) as exc:
                    raise ValueError(f'{filename}, línea {line}: {exc}') from exc
    for filename in ('parking.csv', 'trafico.csv'):
        affected = [r for r in result if r['file'] == filename and r['errors']]
        print(f'  Calidad {filename}: {len(affected):,} lecturas con anomalías; originales conservados en raw.', flush=True)
        for r in affected[:5]:
            print(f"    Línea {r['line']}: {r['errors']}", flush=True)
    return result


def scalar(cur, sql, args):
    cur.execute(sql, args)
    return cur.fetchone()[0]


def catalogs(conn):
    sources, variables = {}, {}
    with conn:
        with conn.cursor() as cur:
            for filename in ('parking.csv', 'trafico.csv'):
                sources[filename] = scalar(cur, """INSERT INTO fuentes_datos
                    (nombre,version,licencia,naturaleza_datos) VALUES (%s,'csv-v1','No proporcionada','no_verificada')
                    ON CONFLICT(nombre,version) DO UPDATE SET nombre=EXCLUDED.nombre RETURNING id_fuente""", (filename,))
            cur.execute("SELECT id_variable,codigo_variable,unidad FROM variables_medicion WHERE codigo_variable IN ('capacidad','ocupacion')")
            for vid, code, unit in cur.fetchall():
                variables[code] = (vid, code, unit)
            for code, unit in METRICS:
                vid = scalar(cur, """INSERT INTO variables_medicion(codigo_variable,nombre,definicion,unidad,criterio_agregacion)
                    VALUES (%s,%s,'Estadística anual del CSV; no es una lectura instantánea',%s,'no_agregar')
                    ON CONFLICT(codigo_variable) DO UPDATE SET codigo_variable=EXCLUDED.codigo_variable RETURNING id_variable""", (code, code, unit))
                variables[code] = (vid, code, unit)
                cur.execute('INSERT INTO tipos_sensor_variables VALUES (2,%s) ON CONFLICT DO NOTHING', (vid,))
    return sources, variables


def context(cur, row, source):
    parking = row['file'] == 'parking.csv'
    city_name = 'Ubicación no informada (parking.csv)' if parking else row['name']
    city = scalar(cur, """INSERT INTO ciudades(nombre,pais) VALUES (%s,'No informado')
        ON CONFLICT(pais,nombre) DO UPDATE SET nombre=EXCLUDED.nombre RETURNING id_ciudad""", (city_name,))
    zone_code = ('parking:' + row['name']) if parking else 'estadistica_anual_csv'
    loc = scalar(cur, """INSERT INTO ubicaciones(id_ciudad,codigo_zona,nombre_zona) VALUES (%s,%s,%s)
        ON CONFLICT(id_ciudad,codigo_zona) DO UPDATE SET codigo_zona=EXCLUDED.codigo_zona RETURNING id_ubicacion""", (city, zone_code, row['name']))
    stype = 1 if parking else 2
    sensor_code = 'csv:' + row['file'] + ':' + row['name']
    sensor = scalar(cur, """INSERT INTO sensores(codigo_sensor,nombre,id_tipo_sensor,id_ubicacion,estado_administrativo,naturaleza_sensor)
        VALUES (%s,%s,%s,%s,'activo','logico') ON CONFLICT(codigo_sensor) DO UPDATE SET codigo_sensor=EXCLUDED.codigo_sensor RETURNING id_sensor""", (sensor_code, row['name'], stype, loc))
    ctx = dict(id_ciudad=Int64(city), id_ubicacion=Int64(loc), id_tipo_sensor=Int64(stype), id_categoria=Int64(1))
    if parking:
        park = scalar(cur, """INSERT INTO estacionamientos(id_fuente,id_ubicacion,codigo_origen,nombre) VALUES (%s,%s,%s,%s)
            ON CONFLICT(id_fuente,codigo_origen) DO UPDATE SET nombre=EXCLUDED.nombre RETURNING id_estacionamiento""", (source, loc, row['name'], row['name']))
        ctx['id_estacionamiento'] = Int64(park)
    return sensor, ctx


def load_csv(conn, database, rows, parking_timezone='UTC'):
    sources, variables = catalogs(conn)
    cache = {}
    received = datetime.now(timezone.utc)
    for start in range(0, len(rows), 1000):
        docs = []
        with conn:
            with conn.cursor() as cur:
                for row in rows[start:start + 1000]:
                    source = sources[row['file']]
                    ck = (source, row['name'])
                    if ck not in cache:
                        cache[ck] = context(cur, row, source)
                    sensor, ctx = cache[ck]
                    parking = row['file'] == 'parking.csv'
                    kind = 'parking' if parking else 'trafico'
                    docid = f'csv:{source}:' + hashlib.sha256(row['key'].encode()).hexdigest()
                    interval = None if parking else int((datetime(row['year'] + 1, 1, 1, tzinfo=timezone.utc) - row['dt']).total_seconds())
                    rid = scalar(cur, """INSERT INTO lecturas_limpias
                        (id_sensor,id_fuente,clave_origen,id_documento_mongo,fecha_medicion,fecha_recepcion,calidad,clase_lectura,intervalo_segundos)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT(id_fuente,clave_origen) DO UPDATE SET fecha_recepcion=EXCLUDED.fecha_recepcion,
                        fecha_medicion=EXCLUDED.fecha_medicion,intervalo_segundos=EXCLUDED.intervalo_segundos,calidad=EXCLUDED.calidad
                        RETURNING id_lectura""", (sensor, source, row['key'], docid, row['dt'], received, row['quality'], kind, interval))
                    codes = ['capacidad', 'ocupacion'] if parking else [m[0] for m in METRICS]
                    measures = []
                    sql_measures = []
                    for code, val in zip(codes, row['vals']):
                        if val is None:
                            continue
                        vid, _, unit = variables[code]
                        sql_measures.append((rid, vid, val))
                        measures.append(dict(id_variable=Int64(vid), codigo=code, valor=Decimal128(val), unidad=unit))
                    # Reemplazar SOLO mediciones de esta lectura importada, dentro de la transacción.
                    # También retira valores antes aceptados que ahora se detectan como inválidos.
                    cur.execute('DELETE FROM mediciones_limpias WHERE id_lectura=%s', (rid,))
                    if sql_measures:
                        execute_values(cur, 'INSERT INTO mediciones_limpias VALUES %s', sql_measures)
                    if parking:
                        cur.execute('INSERT INTO lecturas_parking VALUES (%s,%s) ON CONFLICT DO NOTHING', (rid, int(ctx['id_estacionamiento'])))
                    else:
                        cur.execute('INSERT INTO lecturas_trafico(id_lectura) VALUES (%s) ON CONFLICT DO NOTHING', (rid,))
                    doc = dict(_id=docid, schema_version=1, id_fuente=Int64(source), clave_origen=row['key'],
                               naturaleza='no_verificada', procedencia='original', id_sensor=Int64(sensor), tipo=kind,
                               fecha_medicion=row['dt'], fecha_recepcion=received, contexto=ctx, mediciones=measures,
                               calidad=row['quality'], errores=row['errors'], raw=row['raw'], trazabilidad=dict(archivo=row['file'], fila=Int64(row['line']), version_ingesta='csv-v2-calidad'))
                    if interval:
                        doc.update(intervalo_segundos=interval, granularidad='anual', anio=row['year'], fecha_representativa=True)
                    else:
                        doc['trazabilidad']['zona_horaria_asumida'] = parking_timezone
                    docs.append(doc)
        database.lecturas.bulk_write([ReplaceOne({'_id': d['_id']}, d, upsert=True) for d in docs], ordered=False)
        print(f'  CSV: {min(start + 1000, len(rows)):,}/{len(rows):,} registros procesados.', flush=True)
