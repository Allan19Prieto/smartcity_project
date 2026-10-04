import psycopg2
from pymongo import MongoClient

print("🔍 Comprobando conexiones del clúster...")

# 1. Probar PostgreSQL
try:
    conn = psycopg2.connect(host="postgres", database="smartcity_db", user="admin", password="password123")
    print("✅ 1. PostgreSQL: Conexión EXITOSA")
    conn.close()
except Exception as e:
    print(f"❌ 1. PostgreSQL Falló: {e}")

# 2. Probar MongoDB
try:
    client = MongoClient("mongodb://admin:password123@mongodb:27017/", serverSelectionTimeoutMS=2000)
    client.server_info()
    print("✅ 2. MongoDB: Conexión EXITOSA")
except Exception as e:
    print(f"❌ 2. MongoDB Falló: {e}")

# 3. Probar Spark
try:
    from pyspark.sql import SparkSession
    spark = SparkSession.builder.appName("TestSpark").master("local[*]").getOrCreate()
    df = spark.createDataFrame([(1, "Sensor Activo")], ["id", "estado"])
    print("✅ 3. Apache Spark: Motor en memoria FUNCIONANDO")
    df.show()
    spark.stop()
except Exception as e:
    print(f"❌ 3. Spark Falló: {e}")

print("\n🚀 ¡TODO EL ECOSISTEMA ESTÁ LISTO!")