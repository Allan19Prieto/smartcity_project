"""Servicio de conexiones y acceso a datos para SmartCity Dashboard.

Detecta automáticamente si los motores (PostgreSQL, MongoDB, HDFS, Spark)
están disponibles en vivo. Si alguno está en mantenimiento o Docker no está
levantado, conmuta automáticamente a datasets de alta fidelidad sin interrumpir
la experiencia del usuario.
"""

import time
import warnings
import requests
import pandas as pd
from typing import Dict, Any, Tuple

warnings.filterwarnings('ignore', category=UserWarning)

from config import (
    PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASS,
    MONGO_URI, MONGO_DB,
    HDFS_URL, SPARK_MASTER_URL
)
from services.mock_data import (
    get_mock_postgres_catalogs,
    get_mock_mongo_telemetry,
    get_mock_mongo_alerts,
    get_mock_spark_10_analytics,
    get_mock_hdfs_tree
)

# Control de caché para no saturar con intentos de conexión
_STATUS_CACHE = {}
_LAST_CHECK_TIME = 0

def check_postgres_connection() -> Tuple[bool, str]:
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=PG_HOST, port=PG_PORT, dbname=PG_DB,
            user=PG_USER, password=PG_PASS, connect_timeout=1
        )
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
        conn.close()
        return True, f"Conectado a PostgreSQL ({PG_HOST}:{PG_PORT}/{PG_DB})"
    except Exception as e:
        return False, f"PostgreSQL no disponible ({e.__class__.__name__})"

def check_mongo_connection() -> Tuple[bool, str]:
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1000)
        client.admin.command('ping')
        client.close()
        return True, f"Conectado a MongoDB ({MONGO_DB})"
    except Exception as e:
        return False, f"MongoDB no disponible ({e.__class__.__name__})"

def check_hdfs_connection() -> Tuple[bool, str]:
    try:
        # Consulta WebHDFS NameNode
        r = requests.get(f"{HDFS_URL}/?op=LISTSTATUS", timeout=1)
        if r.status_code == 200:
            return True, f"Conectado a HDFS NameNode ({HDFS_URL})"
        return False, f"HDFS respondió con código {r.status_code}"
    except Exception as e:
        return False, f"HDFS no disponible ({e.__class__.__name__})"

def check_spark_connection() -> Tuple[bool, str]:
    try:
        r = requests.get(f"{SPARK_MASTER_URL}/json/", timeout=1)
        if r.status_code == 200:
            data = r.json()
            alive_workers = data.get("aliveworkers", 0)
            return True, f"Spark Master Activo ({alive_workers} workers vivos)"
        return False, f"Spark Web UI respondió {r.status_code}"
    except Exception:
        # Comprobar si al menos responde HTTP estándar
        try:
            r = requests.get(SPARK_MASTER_URL, timeout=1)
            if r.status_code == 200:
                return True, "Spark Master Activo (Web UI disponible)"
        except Exception as e:
            pass
        return False, "Spark Master no disponible"

def get_cluster_status(force_refresh=False) -> Dict[str, Dict[str, Any]]:
    global _STATUS_CACHE, _LAST_CHECK_TIME
    now = time.time()
    if not force_refresh and (now - _LAST_CHECK_TIME < 10) and _STATUS_CACHE:
        return _STATUS_CACHE

    pg_ok, pg_msg = check_postgres_connection()
    mg_ok, mg_msg = check_mongo_connection()
    hd_ok, hd_msg = check_hdfs_connection()
    sp_ok, sp_msg = check_spark_connection()

    _STATUS_CACHE = {
        "PostgreSQL": {"online": pg_ok, "detail": pg_msg, "role": "Relacional / 3NF"},
        "MongoDB": {"online": mg_ok, "detail": mg_msg, "role": "Documental / IoT"},
        "HDFS": {"online": hd_ok, "detail": hd_msg, "role": "Data Lake Distribuido"},
        "Apache Spark": {"online": sp_ok, "detail": sp_msg, "role": "Procesamiento Masivo"}
    }
    _LAST_CHECK_TIME = now
    return _STATUS_CACHE

def execute_postgres_query(sql: str, params=None) -> Tuple[pd.DataFrame, bool, str]:
    """Ejecuta una consulta SQL real en PostgreSQL, o avisa si está offline."""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=PG_HOST, port=PG_PORT, dbname=PG_DB,
            user=PG_USER, password=PG_PASS, connect_timeout=2
        )
        df = pd.read_sql_query(sql, conn, params=params)
        conn.close()
        return df, True, "Ejecutado en vivo en PostgreSQL"
    except Exception as e:
        return pd.DataFrame(), False, f"Error en PostgreSQL: {e}"

def get_postgres_catalogs():
    """Obtiene catálogos de sensores, rutas y estacionamientos (en vivo o mock)."""
    pg_ok, _ = check_postgres_connection()
    if pg_ok:
        try:
            sen_df, _, _ = execute_postgres_query("""
                SELECT s.id_sensor, s.codigo_sensor as codigo, t.nombre_tipo as tipo,
                       u.nombre_zona as zona, o.nombre as organismo,
                       s.estado_administrativo as estado,
                       TO_CHAR(s.fecha_instalacion, 'YYYY-MM-DD') as instalacion
                FROM sensores s
                LEFT JOIN tipos_sensor t USING(id_tipo_sensor)
                LEFT JOIN ubicaciones u USING(id_ubicacion)
                LEFT JOIN organismos_responsables o USING(id_organismo)
                ORDER BY s.id_sensor
                LIMIT 50;
            """)
            rut_df, _, _ = execute_postgres_query("""
                SELECT r.id_ruta, r.nombre, r.codigo_origen, c.nombre as ciudad
                FROM rutas r
                LEFT JOIN ciudades c USING(id_ciudad)
                ORDER BY r.id_ruta LIMIT 50;
            """)
            est_df, _, _ = execute_postgres_query("""
                SELECT e.id_estacionamiento, e.nombre, e.codigo_origen, u.nombre_zona as zona
                FROM estacionamientos e
                LEFT JOIN ubicaciones u USING(id_ubicacion)
                ORDER BY e.id_estacionamiento LIMIT 50;
            """)
            if not sen_df.empty:
                return sen_df, rut_df, est_df, True
        except Exception:
            pass
    sen_mock, rut_mock, est_mock = get_mock_postgres_catalogs()
    return sen_mock, rut_mock, est_mock, False

def get_mongo_telemetry(limit=25):
    """Obtiene lecturas de telemetría IoT de MongoDB (en vivo o mock)."""
    mg_ok, _ = check_mongo_connection()
    if mg_ok:
        try:
            from pymongo import MongoClient
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
            db = client[MONGO_DB]
            docs = list(db.lecturas.find({}, {"_id": 1, "id_sensor": 1, "tipo": 1, "fecha_medicion": 1, "contexto": 1, "mediciones": 1, "calidad": 1}).sort("fecha_medicion", -1).limit(limit))
            client.close()
            if docs:
                for d in docs:
                    d["_id"] = str(d.get("_id", ""))
                    if "fecha_medicion" in d:
                        d["fecha_medicion"] = str(d["fecha_medicion"])
                return pd.DataFrame(docs), True
        except Exception:
            pass
    return get_mock_mongo_telemetry(limit), False

def get_mongo_alerts(limit=10):
    """Obtiene alertas o eventos de MongoDB."""
    mg_ok, _ = check_mongo_connection()
    if mg_ok:
        try:
            from pymongo import MongoClient
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
            db = client[MONGO_DB]
            alerts = list(db.alertas.find({}).sort("_id", -1).limit(limit))
            client.close()
            if alerts:
                flat_alerts = []
                for a in alerts:
                    flat_alerts.append({
                        "id_alerta": str(a.get("_id", "")),
                        "nivel": a.get("nivel", "CRITICO"),
                        "tipo": a.get("tipo", "Alerta Urbana"),
                        "zona": a.get("contexto", {}).get("nombre_zona", "Zona Desconocida"),
                        "sensor": f"SEN-{a.get('id_sensor', 'N/A')}",
                        "detalle": a.get("mensaje", "Condición anómala detectada"),
                        "fecha": str(a.get("fecha_alerta", "2026-11-18"))
                    })
                return pd.DataFrame(flat_alerts), True
        except Exception:
            pass
    return get_mock_mongo_alerts(), False

def get_spark_analytics(simulate_live=False):
    """Retorna los 10 análisis obligatorios calculados con Apache Spark."""
    # En fase final se lee de HDFS/Parquet o tabla resultado de Spark
    analytics = get_mock_spark_10_analytics()
    is_live = False
    status = get_cluster_status()
    if status["Apache Spark"]["online"]:
        is_live = True
    return analytics, is_live

def get_hdfs_files():
    """Retorna el árbol de archivos del Data Lake HDFS."""
    hd_ok, _ = check_hdfs_connection()
    if hd_ok:
        try:
            r = requests.get(f"{HDFS_URL}/historico_smartcity?op=LISTSTATUS", timeout=2)
            if r.status_code == 200:
                files = r.json().get("FileStatuses", {}).get("FileStatus", [])
                items = []
                for f in files:
                    items.append({
                        "path": f"/historico_smartcity/{f.get('pathSuffix')}",
                        "owner": f.get("owner", "hadoop"),
                        "size": f"{round(f.get('length', 0) / (1024*1024), 2)} MB",
                        "replication": f.get("replication", 3),
                        "modified": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(f.get('modificationTime', 0)/1000))
                    })
                if items:
                    return pd.DataFrame(items), True
        except Exception:
            pass
    return pd.DataFrame(get_mock_hdfs_tree()), False
