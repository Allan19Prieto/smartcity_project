import psycopg2
import pandas as pd
from pymongo import MongoClient
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg

print("===================================================================")
print("🚀 SMARTCITY: DEMO DE INTEGRACIÓN (POSTGRES + MONGO + SPARK + HDFS)")
print("===================================================================")

# -------------------------------------------------------------
# 1. POSTGRESQL: Crear datos maestros de sensores (Estructurados)
# -------------------------------------------------------------
print("\n[Paso 1] Insertando metadatos maestros en PostgreSQL...")
conn_pg = psycopg2.connect(
    host="postgres",
    database="smartcity_db",
    user="admin",
    password="password123"
)
cursor = conn_pg.cursor()

# Crear tabla de catálogo de sensores
cursor.execute("""
    CREATE TABLE IF NOT EXISTS catalogo_sensores (
        id_sensor VARCHAR(10) PRIMARY KEY,
        tipo_sensor VARCHAR(50),
        zona VARCHAR(50)
    );
""")

# Insertar registros de prueba
cursor.execute("""
    INSERT INTO catalogo_sensores (id_sensor, tipo_sensor, zona) VALUES
    ('S-01', 'Calidad del Aire', 'Centro Urbano'),
    ('S-02', 'Calidad del Aire', 'Parque Industrial'),
    ('S-03', 'Calidad del Aire', 'Zona Residencial')
    ON CONFLICT (id_sensor) DO NOTHING;
""")
conn_pg.commit()

# Leer de Postgres a DataFrame
df_postgres_pd = pd.read_sql("SELECT * FROM catalogo_sensores;", conn_pg)
cursor.close()
conn_pg.close()
print("✅ Datos obtenidos de PostgreSQL:")
print(df_postgres_pd)

# -------------------------------------------------------------
# 2. MONGODB: Insertar lecturas de telemetría IoT (Semi-estructurado)
# -------------------------------------------------------------
print("\n[Paso 2] Insertando telemetría de sensores en MongoDB...")
client_mongo = MongoClient("mongodb://admin:password123@mongodb:27017/")
db = client_mongo["smartcity_db"]
coleccion = db["telemetria_iot"]

# Limpiar pruebas viejas e insertar documentos JSON
coleccion.delete_many({})
datos_iot = [
    {"id_sensor": "S-01", "pm25": 35.5, "co2": 420, "alerta": False},
    {"id_sensor": "S-01", "pm25": 42.0, "co2": 450, "alerta": False},
    {"id_sensor": "S-02", "pm25": 85.0, "co2": 890, "alerta": True},
    {"id_sensor": "S-02", "pm25": 92.3, "co2": 910, "alerta": True},
    {"id_sensor": "S-03", "pm25": 12.1, "co2": 380, "alerta": False}
]
coleccion.insert_many(datos_iot)

# Extraer de Mongo a DataFrame
lecturas_mongo = list(coleccion.find({}, {"_id": 0}))
df_mongo_pd = pd.DataFrame(lecturas_mongo)
print("✅ Datos obtenidos de MongoDB (JSON):")
print(df_mongo_pd)

# -------------------------------------------------------------
# 3. APACHE SPARK: Cruzar datos (JOIN) y procesamiento analítico
# -------------------------------------------------------------
print("\n[Paso 3] Procesando con Apache Spark en memoria...")
spark = SparkSession.builder \
    .appName("DemoSmartCityIntegration") \
    .master("local[*]") \
    .getOrCreate()

# Convertir datos a DataFrames nativos de Spark
spark_sensores = spark.createDataFrame(df_postgres_pd)
spark_telemetria = spark.createDataFrame(df_mongo_pd)

# Realizar el JOIN de las dos fuentes y calcular promedios por zona
print("👉 Realizando JOIN (Postgres + Mongo) y cálculo analítico...")
df_resultado = spark_telemetria.join(spark_sensores, on="id_sensor", how="inner") \
    .groupBy("zona", "tipo_sensor") \
    .agg(
        avg("pm25").alias("promedio_pm25"),
        avg("co2").alias("promedio_co2")
    )

print("\n📊 RESULTADO ANALÍTICO PROCESADO POR SPARK:")
df_resultado.show()

# -------------------------------------------------------------
# 4. HADOOP HDFS: Almacenar el resultado en el sistema distribuido
# -------------------------------------------------------------
print("[Paso 4] Guardando resultado final en Hadoop (HDFS)...")
ruta_hdfs = "hdfs://namenode:9000/historico_smartcity/resumen_contaminacion"

# Spark escribe directamente en HDFS en formato CSV
df_resultado.write \
    .mode("overwrite") \
    .option("header", "true") \
    .csv(ruta_hdfs)

print(f"✅ ¡Datos exportados con éxito a HDFS en: {ruta_hdfs}!")

spark.stop()
print("\n🎉 DEMO FINALIZADA: Las 4 tecnologías funcionaron integradas.")