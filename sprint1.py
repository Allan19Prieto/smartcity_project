"""Un solo punto de entrada para preparar y demostrar PostgreSQL + MongoDB.

Ejecutar desde el Dev Container: python sprint1.py
Genera datos sintéticos claramente marcados; no descarga ni presenta datos reales.
"""

from __future__ import annotations

import os
import argparse
import sys
import time
from pathlib import Path

import psycopg2
from pymongo import MongoClient
from consultas import ejecutar as ejecutar_consultas
from carga_sintetica import load_data as cargar_datos


ROOT = Path(__file__).resolve().parent
SQL_FILE = ROOT / "sql" / "001_schema.sql"
PG = {
    "host": os.getenv("PGHOST", "postgres"),
    "port": int(os.getenv("PGPORT", "5432")),
    "dbname": os.getenv("PGDATABASE", "smartcity_db"),
    "user": os.getenv("PGUSER", "admin"),
    "password": os.getenv("PGPASSWORD", "password123"),
}
MONGO_URI = os.getenv(
    "MONGODB_URI", "mongodb://admin:password123@mongodb:27017/?authSource=admin"
)
DB_NAME = os.getenv("MONGO_DATABASE", "smartcity_db")
READING_COUNT = int(os.getenv("SPRINT1_READING_COUNT", "500000"))


def say(message: str) -> None:
    print(f"\n{message}", flush=True)


def wait_for_databases() -> tuple[psycopg2.extensions.connection, MongoClient]:
    say("1/5  Esperando PostgreSQL y MongoDB...")
    last_error: Exception | None = None
    for attempt in range(1, 61):
        pg = None
        mongo = None
        try:
            pg = psycopg2.connect(**PG, connect_timeout=3)
            mongo = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
            mongo.admin.command("ping")
            print("  PostgreSQL y MongoDB responden.", flush=True)
            return pg, mongo
        except Exception as exc:
            last_error = exc
            if pg:
                pg.close()
            if mongo:
                mongo.close()
            time.sleep(2)
    raise RuntimeError(f"No pude conectar a las bases después de 120 s: {last_error}")


def setup_postgres(conn) -> None:
    say("2/5  Creando el esquema PostgreSQL...")
    with conn:
        with conn.cursor() as cur:
            cur.execute(SQL_FILE.read_text(encoding="utf-8"))
    print("  Esquema, vista y función creados desde sql/001_schema.sql.", flush=True)


def wait_for_mongo_setup(database) -> None:
    """La imagen oficial ejecuta mongo/001_setup.js al crear una base vacía."""
    say("3/5  Esperando las colecciones creadas por mongo/001_setup.js...")
    required = {"lecturas", "eventos", "alertas", "incidentes"}
    for _ in range(60):
        if required.issubset(set(database.list_collection_names())):
            print("  Colecciones e índices listos.", flush=True)
            return
        time.sleep(2)
    raise RuntimeError("No aparecen las colecciones. Revisa el inicio del servicio MongoDB y su archivo 001_setup.js.")


def main(skip_load: bool = False) -> int:
    if not SQL_FILE.exists():
        print(f"No encuentro el esquema SQL: {SQL_FILE}", file=sys.stderr)
        return 2
    if READING_COUNT < 500000:
        print("Aviso: SPRINT1_READING_COUNT está por debajo del mínimo de 500.000.", flush=True)
    pg = mongo_client = None
    try:
        pg, mongo_client = wait_for_databases()
        database = mongo_client[DB_NAME]
        setup_postgres(pg)
        wait_for_mongo_setup(database)
        if skip_load:
            say("4/5  Se conserva la carga existente; omitiendo la generación de datos.")
        else:
            cargar_datos(pg, database, READING_COUNT)
        say("5/5  Ejecutando consultas requeridas de demostración...")
        ejecutar_consultas(pg, database)
        with pg.cursor() as cur:
            cur.execute("SELECT count(*) FROM lecturas_limpias")
            pg_count = cur.fetchone()[0]
        mongo_count = database.lecturas.count_documents({})
        print(f"\nLISTO: PostgreSQL={pg_count:,} lecturas; MongoDB={mongo_count:,} lecturas.", flush=True)
        if pg_count < 100000 or mongo_count < 500000:
            print("FALTA: uno de los conteos está por debajo del mínimo del proyecto.", flush=True)
            return 1
        return 0
    except Exception as exc:
        print(f"\nERROR: {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
        return 1
    finally:
        if pg:
            pg.close()
        if mongo_client:
            mongo_client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preparar y demostrar PostgreSQL y MongoDB del Sprint 1.")
    parser.add_argument("--skip-load", action="store_true", help="Usa los datos ya cargados y ejecuta solo estructura/consultas.")
    args = parser.parse_args()
    raise SystemExit(main(skip_load=args.skip_load))
