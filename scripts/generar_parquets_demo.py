"""Script para generar los diez archivos Parquet de referencia para Apache Spark.

Crea los archivos binarios .parquet en el directorio data_lake/analitica_spark/
para comprobar la admisión y lectura en tiempo real desde la interfaz gráfica.
"""

import os
import sys
from pathlib import Path

# Agregar directorio del dashboard para importar mock_data
root_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root_dir / "dashboard"))

import pandas as pd
from services.mock_data import get_mock_spark_10_analytics

def main():
    output_dir = root_dir / "data_lake" / "analitica_spark"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    analytics = get_mock_spark_10_analytics()
    
    print(f"Generando archivos Apache Parquet en: {output_dir}")
    for key, df in analytics.items():
        file_path = output_dir / f"{key}.parquet"
        df.to_parquet(file_path, engine="pyarrow", index=False)
        print(f"  -> Creado: {file_path.name} ({len(df)} filas, {os.path.getsize(file_path)} bytes)")

    print("Generación de datasets Parquet completada con éxito.")

if __name__ == "__main__":
    main()
