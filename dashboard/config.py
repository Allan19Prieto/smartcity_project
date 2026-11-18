"""Configuración centralizada para la Interfaz SmartCity Analytics."""

import os
import socket

def resolve_host(candidates: list, fallback: str = "localhost") -> str:
    """Evalúa la lista de nombres de servicio posibles en Docker y devuelve el primero accesible."""
    for name in candidates:
        env_val = os.getenv(f"{name.upper().replace('-', '_')}_HOST")
        if env_val:
            return env_val
        try:
            socket.gethostbyname(name)
            return name
        except Exception:
            continue
    return fallback

# PostgreSQL
PG_HOST = os.getenv("PGHOST", resolve_host(["postgres", "smartcity-desktop-postgres-1", "smartcity-sprint1-postgres-1", "postgres_db"], "localhost"))
PG_PORT = int(os.getenv("PGPORT", "5432"))
PG_DB = os.getenv("PGDATABASE", "smartcity_db")
PG_USER = os.getenv("PGUSER", "admin")
PG_PASS = os.getenv("PGPASSWORD", "password123")

# MongoDB
MONGO_HOST = os.getenv("MONGO_HOST", resolve_host(["mongodb", "smartcity-desktop-mongodb-1", "smartcity-sprint1-mongodb-1", "mongo_db"], "localhost"))
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_USER = os.getenv("MONGO_USER", "admin")
MONGO_PASS = os.getenv("MONGO_PASS", "password123")
MONGO_DB = os.getenv("MONGO_DATABASE", "smartcity_db")
MONGO_URI = os.getenv(
    "MONGODB_URI",
    f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"
)

# Hadoop HDFS (WebHDFS REST API)
HDFS_HOST = os.getenv("HDFS_HOST", resolve_host(["namenode", "hadoop_namenode", "smartcity-desktop-namenode-1", "smartcity-sprint1-namenode-1"], "localhost"))
HDFS_PORT = int(os.getenv("HDFS_PORT", "9870"))
HDFS_URL = f"http://{HDFS_HOST}:{HDFS_PORT}/webhdfs/v1"

# Apache Spark Master UI / API
SPARK_HOST = os.getenv("SPARK_HOST", resolve_host(["spark-master", "smartcity-desktop-spark-master-1", "smartcity-sprint1-spark-master-1", "spark_master"], "localhost"))
SPARK_PORT = int(os.getenv("SPARK_PORT", "8080"))
SPARK_MASTER_URL = f"http://{SPARK_HOST}:{SPARK_PORT}"
