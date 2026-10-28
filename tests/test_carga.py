import sys
import tempfile
import unittest
from contextlib import nullcontext
from datetime import timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bson import BSON
from carga_csv import parse_files, number, load_csv, METRICS
from carga_sintetica import load_data

PARK = 'SystemCodeNumber,Capacity,Occupancy,LastUpdated\nBHMBCCMKT01,577,61,2016-10-04 07:59:42\n'
TRAFFIC = 'City;Year;Average_Daily_Traffic_Counts;Peak_Hourly_Traffic_Volume;Percentage_of_Commercial_Vehicles;Number_of_Road_Accidents;Average_Traffic_Speed_kmh;Air_Quality_Index;Population_Million\nNew York;2015;19967;4705;15,3;159;30,7;113;11,24\n'

class Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'parking.csv').write_text(PARK, encoding='utf-8-sig')
        (self.root / 'trafico.csv').write_text(TRAFFIC, encoding='utf-8-sig')

    def test_samples(self):
        rows = parse_files(self.root)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1]['vals'][2], Decimal('15.3'))
        self.assertEqual(rows[1]['vals'][6], Decimal('11.24'))
        self.assertEqual(rows[0]['dt'].tzinfo, timezone.utc)

    def test_timezone(self):
        self.assertEqual(parse_files(self.root, 'Europe/London')[0]['dt'].hour, 6)

    def test_duplicate(self):
        with (self.root / 'parking.csv').open('a') as f:
            f.write(PARK.splitlines()[1] + '\n')
        self.assertEqual(len(parse_files(self.root)), 2)

    def test_conflicting_duplicate(self):
        with (self.root / 'parking.csv').open('a') as f:
            f.write(PARK.splitlines()[1].replace(',61,', ',62,') + '\n')
        with self.assertRaisesRegex(ValueError, 'línea 3'):
            parse_files(self.root)

    def test_bad_occupancy(self):
        (self.root / 'parking.csv').write_text(PARK.replace(',61,', ',999,'))
        with self.assertRaisesRegex(ValueError, 'parking.csv, línea 2'):
            parse_files(self.root)

    def test_nonfinite(self):
        for value in ('NaN', 'Infinity', '-1', ''):
            with self.assertRaises(ValueError):
                number(value)

    def test_missing_column(self):
        (self.root / 'trafico.csv').write_text(TRAFFIC.replace('City;', 'Ciudad;'))
        with self.assertRaisesRegex(ValueError, 'encabezado'):
            parse_files(self.root)

    def test_csv_documents(self):
        rows = parse_files(self.root)
        variables = {code: (i+1, code, unit) for i,(code,unit) in enumerate([('capacidad','plazas'),('ocupacion','plazas')] + METRICS)}
        conn, db = MagicMock(), MagicMock()
        with patch('carga_csv.catalogs', return_value=({'parking.csv':2,'trafico.csv':3}, variables)), patch('carga_csv.context', return_value=(101, {'id_ciudad':1,'id_ubicacion':1,'id_estacionamiento':21})), patch('carga_csv.scalar', side_effect=[1001,1002]), patch('carga_csv.execute_values'):
            load_csv(conn, db, rows)
        docs = [op._doc for op in db.lecturas.bulk_write.call_args.args[0]]
        for doc in docs:
            BSON.encode(doc)
            self.assertEqual(doc['naturaleza'], 'no_verificada')
        self.assertEqual(len(docs[1]['mediciones']), 7)
        self.assertEqual(docs[1]['intervalo_segundos'], 365*86400)
        self.assertEqual(docs[1]['granularidad'], 'anual')
        self.assertNotIn('intervalo_segundos', docs[0])

    def test_synthetic_ids_use_database_mapping(self):
        conn, db = MagicMock(), MagicMock()
        calls = []
        def values(cur, sql, rows, **kwargs):
            calls.append((sql, rows))
            if 'RETURNING' in sql:
                return [(9001, 'generado:fila0000001'), (9002, 'generado:fila0000002')]
        with patch('carga_sintetica.upsert_catalog'), patch('carga_sintetica.execute_values', side_effect=values), patch('carga_sintetica.create_events_and_alerts') as events:
            load_data(conn, db, 2)
        self.assertEqual(calls[1][1][0][0], 9001)
        self.assertEqual(calls[2][1][1][0], 9002)
        self.assertIn('ON CONFLICT(id_fuente,clave_origen)', calls[0][0])
        events.assert_called_once_with(db, 0)

if __name__ == '__main__':
    unittest.main()
