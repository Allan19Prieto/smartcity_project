"""CSV primero; luego generación sintética independiente. Ejecutar en Dev Container."""
from __future__ import annotations
import argparse
import os
import sys
import time
from pathlib import Path
import psycopg2
from pymongo import MongoClient
from carga_csv import parse_files, load_csv
from carga_sintetica import load_data, upsert_catalog
from consultas import ejecutar

ROOT = Path(__file__).resolve().parent
SQL_FILE = ROOT / 'sql' / '001_schema.sql'


def wait_for_databases():
    last = None
    for _ in range(60):
        pg = mongo = None
        try:
            pg = psycopg2.connect(host=os.getenv('PGHOST', 'postgres'), port=int(os.getenv('PGPORT', '5432')),
                dbname=os.getenv('PGDATABASE', 'smartcity_db'), user=os.getenv('PGUSER', 'admin'),
                password=os.getenv('PGPASSWORD', 'password123'), connect_timeout=3)
            mongo = MongoClient(os.getenv('MONGODB_URI', 'mongodb://admin:password123@mongodb:27017/?authSource=admin'), serverSelectionTimeoutMS=3000)
            mongo.admin.command('ping')
            return pg, mongo
        except Exception as exc:
            last = exc
            if pg is not None:
                pg.close()
            if mongo is not None:
                mongo.close()
            time.sleep(2)
    raise RuntimeError(f'No pude conectar después de 60 intentos: {last}')


def main(args):
    pg = mongo = None
    try:
        if args.synthetic_count < 0:
            raise ValueError('--synthetic-count debe ser cero o positivo')
        print('1/6  Validando archivos...', flush=True)
        sql = SQL_FILE.read_text(encoding='utf-8')
        rows = [] if args.skip_load else parse_files(args.dataset_dir, args.parking_timezone)
        if not args.skip_load:
            for filename in ('parking.csv', 'trafico.csv'):
                n = sum(r['file'] == filename for r in rows)
                if not n:
                    raise ValueError(f'{filename}: no contiene registros')
                print(f'  {filename}: {n:,} registros únicos válidos.', flush=True)
        print('2/6  Esperando PostgreSQL y MongoDB...', flush=True)
        pg, mongo = wait_for_databases()
        db = mongo[os.getenv('MONGO_DATABASE', 'smartcity_db')]
        # Excluir ejecuciones simultáneas del mismo cargador.
        with pg.cursor() as cur:
            cur.execute('SELECT pg_try_advisory_lock(20261028, 1)')
            if not cur.fetchone()[0]:
                raise RuntimeError('Ya hay otro sprint1.py ejecutándose en esta base')
        pg.commit()
        print('3/6  Preparando esquema y comprobando colecciones...', flush=True)
        with pg:
            with pg.cursor() as cur:
                cur.execute(sql)
        for _ in range(60):
            if {'lecturas', 'eventos', 'alertas', 'incidentes'}.issubset(db.list_collection_names()):
                break
            time.sleep(2)
        else:
            raise RuntimeError('Faltan colecciones. Ejecuta mongo/001_setup.js en la base indicada por MONGO_DATABASE.')
        if args.skip_load:
            print('4–5/6  Cargas CSV y sintética omitidas.', flush=True)
        else:
            # El catálogo se prepara primero, pero no crea ninguna lectura sintética.
            upsert_catalog(pg)
            # Sincronizar la secuencia también para bases cargadas con la versión anterior.
            with pg:
                with pg.cursor() as cur:
                    cur.execute("SELECT setval(pg_get_serial_sequence('lecturas_limpias','id_lectura'), GREATEST(COALESCE((SELECT max(id_lectura) FROM lecturas_limpias),0),1))")
            print('4/6  Cargando CSV en ambas bases...', flush=True)
            load_csv(pg, db, rows, args.parking_timezone)
            if args.synthetic_count:
                load_data(pg, db, args.synthetic_count)
        print('6/6  Consultas y conteos por fuente...', flush=True)
        ejecutar(pg, db)
        with pg.cursor() as cur:
            cur.execute('''SELECT f.id_fuente,f.nombre,f.naturaleza_datos,count(l.id_lectura)
                FROM fuentes_datos f LEFT JOIN lecturas_limpias l USING(id_fuente)
                GROUP BY f.id_fuente,f.nombre,f.naturaleza_datos ORDER BY f.id_fuente''')
            counts = cur.fetchall()
        consistent = True
        for fid, name, nature, count in counts:
            mc = db.lecturas.count_documents({'id_fuente': fid})
            consistent &= count == mc
            print(f'  {name} [{nature}]: PostgreSQL={count:,}; MongoDB={mc:,}', flush=True)
        with pg.cursor() as cur:
            cur.execute('SELECT count(*) FROM lecturas_limpias')
            pc = cur.fetchone()[0]
        mc = db.lecturas.count_documents({})
        if not consistent or pc != mc:
            print('FALTA: los conteos difieren. Repite la carga para reparar una interrupción.', file=sys.stderr)
            return 1
        if pc < 100000 or mc < 500000:
            print(f'FALTA: conteos bajo el mínimo del proyecto. PostgreSQL={pc:,}, MongoDB={mc:,}.', flush=True)
            return 1
        print(f'LISTO: PostgreSQL={pc:,}; MongoDB={mc:,}.', flush=True)
        return 0
    except Exception as exc:
        print(f'ERROR: {type(exc).__name__}: {exc}', file=sys.stderr, flush=True)
        return 1
    finally:
        if pg is not None:
            pg.close()
        if mongo is not None:
            mongo.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-load', action='store_true', help='Omite ambas cargas; ejecuta estructura, consultas y conteos')
    parser.add_argument('--dataset-dir', type=Path, default=ROOT / 'dataset')
    parser.add_argument('--synthetic-count', type=int, default=os.getenv('SPRINT1_READING_COUNT', '500000'), help='Cantidad objetivo de lecturas sintéticas; no incluye CSV')
    parser.add_argument('--parking-timezone', default=os.getenv('PARKING_TIMEZONE', 'UTC'), help='Zona IANA asumida para LastUpdated; predeterminada UTC')
    raise SystemExit(main(parser.parse_args()))
