"""Módulo de Exploración y Linaje en Hadoop HDFS (Data Lake Distribuido)."""

import streamlit as st
from services.db_service import get_hdfs_files, check_hdfs_connection

def render():
    st.title("Data Lake Distribuido (Hadoop HDFS)")
    st.markdown(
        """
        **Hadoop Distributed File System (HDFS)** constituye el repositorio distribuido 
        diseñado para la persistencia del histórico en crudo y la conservación de los conjuntos 
        de datos depurados resultantes de los pipelines de Apache Spark.
        """
    )

    df_hdfs, is_live = get_hdfs_files()

    if is_live:
        st.success("Conexión activa: Servicio WebHDFS operativo (NameNode en puerto 9870).")
    else:
        st.info("Modo de contingencia: Estructura del Data Lake en modo de referencia.")

    tab1, tab2 = st.tabs(["Estructura de Directorios HDFS", "Linaje y Trazabilidad de Datos"])

    with tab1:
        st.subheader("Directorio `/historico_smartcity/`")
        
        capa = st.selectbox("Filtrar por Capa de Persistencia:", ["Todas las Capas", "Capa Cruda (/crudo/)", "Capa Depurada Parquet (/depurado/)", "Capa Analítica (/analitica/)"])

        filtered_df = df_hdfs.copy()
        if "Cruda" in capa:
            filtered_df = filtered_df[filtered_df["path"].str.contains("/crudo/")]
        elif "Depurada" in capa:
            filtered_df = filtered_df[filtered_df["path"].str.contains("/depurado/")]
        elif "Analítica" in capa:
            filtered_df = filtered_df[filtered_df["path"].str.contains("/analitica/")]

        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

        st.markdown("#### Parámetros de Operación del Clúster")
        c1, c2, c3 = st.columns(3)
        c1.metric("Factor de Replicación", "3x", "Tolerancia a fallos de nodo")
        c2.metric("Formato de Almacenamiento", "Apache Parquet", "Compresión columnar Snappy")
        c3.metric("Capacidad Asignada", "500 GB", "Volumen distribuido")

    with tab2:
        st.subheader("Ciclo de Vida y Trazabilidad del Dato")
        st.markdown(
            """
            El ciclo de procesamiento del Data Lake se estructura en las siguientes fases formales:
            
            1. **Preservación Inmutable (Capa Cruda):** Los archivos CSV de sensores de estacionamiento (Birmingham) y tráfico multi-ciudad se ingieren en `/historico_smartcity/crudo/` sin modificaciones para garantizar la reproducibilidad y auditoría histórica.
            2. **Limpieza Distribuida (Spark):** Trabajos en Apache Spark leen la capa cruda, descartan registros que incumplan restricciones de integridad (ej. valores de ocupación que superen la capacidad nominal) y corrigen inconsistencias de formato temporal.
            3. **Persistencia Columnar (Capa Depurada):** Se generan particiones en formato Apache Parquet bajo `/historico_smartcity/depurado/part-*.parquet`, optimizadas para operaciones de escaneo y agregación.
            4. **Agregación Analítica:** Los resultados consolidados se persisten en `/historico_smartcity/analitica/` y son consumidos por esta interfaz centralizada.
            """
        )

        st.code("""# Comandos de auditoría para el NameNode de HDFS
docker exec -it smartcity-sprint1-namenode-1 hdfs dfs -ls /historico_smartcity/
docker exec -it smartcity-sprint1-namenode-1 hdfs dfs -df -h""", language="bash")
