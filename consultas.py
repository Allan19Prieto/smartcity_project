"""Consultas de demostración para PostgreSQL y MongoDB.

Se puede importar desde sprint1.py o ejecutar por separado: python consultas.py
"""

import os
from datetime import datetime, timedelta, timezone

import psycopg2
from pymongo import MongoClient


START = datetime(2025, 1, 1, tzinfo=timezone.utc)


def consultas_postgres(conn) -> None:
    queries = [
        ("Sensores por tipo", "SELECT t.nombre_tipo, count(*) FROM sensores s JOIN tipos_sensor t USING(id_tipo_sensor) GROUP BY t.nombre_tipo ORDER BY 2 DESC"),
        ("Sensores por ubicación", "SELECT u.nombre_zona, count(s.id_sensor) FROM ubicaciones u LEFT JOIN sensores s USING(id_ubicacion) GROUP BY u.nombre_zona ORDER BY 2 DESC FETCH FIRST 5 ROWS ONLY"),
        ("Activos e inactivos", "SELECT estado_administrativo, count(*) FROM sensores GROUP BY estado_administrativo ORDER BY 1"),
        ("Sensores por organismo", "SELECT o.nombre, count(s.id_sensor) FROM organismos_responsables o LEFT JOIN sensores s USING(id_organismo) GROUP BY o.nombre ORDER BY 2 DESC"),
        ("Zonas con más sensores", "SELECT u.nombre_zona, count(*) total FROM sensores s JOIN ubicaciones u USING(id_ubicacion) GROUP BY u.nombre_zona HAVING count(*) > 0 ORDER BY total DESC FETCH FIRST 5 ROWS ONLY"),
        ("Sensores instalados por año", "SELECT extract(year from fecha_instalacion)::int anio, count(*) FROM sensores WHERE fecha_instalacion IS NOT NULL GROUP BY 1 ORDER BY 1"),
        ("Sensores sin lecturas", "SELECT s.id_sensor,s.codigo_sensor FROM sensores s WHERE NOT EXISTS (SELECT 1 FROM lecturas_limpias l WHERE l.id_sensor=s.id_sensor) ORDER BY 1"),
        ("Ranking de zonas (CTE y ventana)", "WITH x AS (SELECT u.nombre_zona,count(l.id_lectura) n FROM ubicaciones u JOIN sensores s USING(id_ubicacion) LEFT JOIN lecturas_limpias l USING(id_sensor) GROUP BY u.nombre_zona) SELECT nombre_zona,n,dense_rank() OVER(ORDER BY n DESC) ranking FROM x ORDER BY ranking,nombre_zona FETCH FIRST 5 ROWS ONLY"),
        ("Vista de última lectura", "SELECT * FROM vw_ultima_lectura_sensor ORDER BY cantidad_lecturas DESC FETCH FIRST 5 ROWS ONLY"),
        ("Función por tipo de sensor", "SELECT * FROM fn_sensores_por_tipo(1) FETCH FIRST 5 ROWS ONLY"),
        ("Agregados por sensor y variable", "SELECT l.id_fuente,l.id_sensor,v.codigo_variable,count(*) n,sum(m.valor) suma,avg(m.valor) promedio,min(m.valor) minimo,max(m.valor) maximo FROM mediciones_limpias m JOIN lecturas_limpias l USING(id_lectura) JOIN variables_medicion v USING(id_variable) GROUP BY l.id_fuente,l.id_sensor,v.codigo_variable HAVING count(*) > 0 ORDER BY n DESC FETCH FIRST 5 ROWS ONLY"),
        ("Filtro y orden por fecha", "SELECT id_sensor,fecha_medicion FROM lecturas_limpias WHERE fecha_medicion >= %s ORDER BY fecha_medicion DESC FETCH FIRST 5 ROWS ONLY", (START,)),
        ("Consulta por sensor y fecha (columnas indexadas)", "SELECT id_lectura,fecha_medicion FROM lecturas_limpias WHERE id_sensor=1 ORDER BY fecha_medicion DESC FETCH FIRST 5 ROWS ONLY"),
    ]
    for item in queries:
        name, query, *params = item
        with conn.cursor() as cur:
            cur.execute(query, params[0] if params else None)
            print(f"  SQL | {name}: {cur.fetchmany(5)}", flush=True)


def consultas_mongo(database) -> None:
    lecturas = database.lecturas
    start_date = START + timedelta(days=30)
    end_date = start_date + timedelta(days=7)
    examples = [
        ("Lecturas de sensor", list(lecturas.find({"id_sensor": 1}, {"_id": 1, "fecha_medicion": 1}).limit(3))),
        ("Lecturas entre fechas", list(lecturas.find({"fecha_medicion": {"$gte": start_date, "$lt": end_date}}, {"_id": 1}).limit(3))),
        ("Máximo y mínimo por variable", list(lecturas.aggregate([{"$unwind": "$mediciones"}, {"$group": {"_id": {"fuente": "$id_fuente", "variable": "$mediciones.codigo"}, "min": {"$min": "$mediciones.valor"}, "max": {"$max": "$mediciones.valor"}}}, {"$limit": 5}]))),
        ("Eventos críticos", list(database.eventos.find({"severidad": "critico"}, {"_id": 1, "tipo_evento": 1}).limit(3))),
        ("Alertas por zona", list(database.alertas.aggregate([{"$group": {"_id": "$contexto.id_ubicacion", "cantidad": {"$sum": 1}}}, {"$sort": {"cantidad": -1}}, {"$limit": 3}]))),
        ("Promedio por zona", list(lecturas.aggregate([{"$unwind": "$mediciones"}, {"$group": {"_id": {"fuente": "$id_fuente", "zona": "$contexto.id_ubicacion", "variable": "$mediciones.codigo"}, "promedio": {"$avg": "$mediciones.valor"}}}, {"$limit": 5}]))),
        ("Promedio por tipo", list(lecturas.aggregate([{"$unwind": "$mediciones"}, {"$group": {"_id": {"fuente": "$id_fuente", "tipo": "$contexto.id_tipo_sensor", "variable": "$mediciones.codigo"}, "promedio": {"$avg": "$mediciones.valor"}}}, {"$limit": 5}]))),
        ("Incidentes por categoría", list(database.incidentes.aggregate([{"$group": {"_id": "$categoria", "cantidad": {"$sum": 1}}}]))),
        ("Lecturas y mediciones por sensor", list(lecturas.aggregate([{"$group": {"_id": "$id_sensor", "lecturas": {"$sum": 1}, "mediciones": {"$sum": {"$size": "$mediciones"}}}}, {"$sort": {"lecturas": -1}}, {"$limit": 3}]))),
        ("Filtros múltiples", list(lecturas.find({"id_sensor": 1, "contexto.id_ubicacion": 1, "fecha_medicion": {"$gte": start_date, "$lt": end_date}, "mediciones": {"$elemMatch": {"id_variable": 2, "valor": {"$gt": 50}}}}, {"_id": 1}).limit(3))),
    ]
    for name, result in examples:
        print(f"  Mongo | {name}: {result}", flush=True)
    demostracion_crud(database)


def demostracion_crud(database) -> None:
    """Demuestra CRUD y deja dos documentos identificables para Mongo Express."""
    demo = database["crud_demo"]
    demo.delete_many({"proyecto": "sprint1-python-demo"})
    demo.insert_one({"_id": "python-demo-1", "proyecto": "sprint1-python-demo", "tipo": "prueba", "valor": 1, "activo": True})
    demo.insert_many([
        {"_id": f"python-demo-{i}", "proyecto": "sprint1-python-demo", "tipo": "prueba", "valor": i, "activo": True}
        for i in (2, 3)
    ])
    demo.find_one({"_id": "python-demo-1"})
    list(demo.find({"proyecto": "sprint1-python-demo"}).sort("valor", 1))
    demo.update_one({"_id": "python-demo-1"}, {"$set": {"valor": 10}})
    demo.update_many({"proyecto": "sprint1-python-demo"}, {"$set": {"activo": False}})
    demo.delete_one({"_id": "python-demo-1"})
    print("  Mongo | CRUD demostrado; quedan dos documentos de ejemplo en crud_demo.", flush=True)


def ejecutar(conn, database) -> None:
    print("Consultas requeridas de PostgreSQL y MongoDB:", flush=True)
    consultas_postgres(conn)
    consultas_mongo(database)


def main() -> int:
    conn = None
    client = None
    try:
        conn = psycopg2.connect(
            host=os.getenv("PGHOST", "postgres"), port=int(os.getenv("PGPORT", "5432")),
            dbname=os.getenv("PGDATABASE", "smartcity_db"), user=os.getenv("PGUSER", "admin"),
            password=os.getenv("PGPASSWORD", "password123"), connect_timeout=5,
        )
        client = MongoClient(os.getenv("MONGODB_URI", "mongodb://admin:password123@mongodb:27017/?authSource=admin"), serverSelectionTimeoutMS=5000)
        database = client[os.getenv("MONGO_DATABASE", "smartcity_db")]
        ejecutar(conn, database)
        return 0
    finally:
        if conn:
            conn.close()
        if client:
            client.close()


if __name__ == "__main__":
    raise SystemExit(main())
