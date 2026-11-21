"""SmartCity Analytics - Interfaz Centralizada (Sprint 2).

Sistema de visualización y monitoreo urbano que unifica:
- PostgreSQL (Catálogos relacionales en Tercera Forma Normal)
- MongoDB (Telemetría IoT semiestructurada y eventos)
- Apache Spark (Procesamiento analítico distribuido)
- Hadoop HDFS (Data Lake distribuido y linaje de datos)
"""

import sys
from pathlib import Path

# Inclusión del directorio del dashboard en el path de módulos
dashboard_dir = Path(__file__).resolve().parent
if str(dashboard_dir) not in sys.path:
    sys.path.insert(0, str(dashboard_dir))

import streamlit as st

# Configuración inicial de la página
st.set_page_config(
    page_title="SmartCity Analytics | Panel Centralizado",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos visuales estructurados
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .tech-badge {
        display: inline-block;
        padding: 4px 10px;
        font-size: 0.85rem;
        font-weight: 600;
        border-radius: 6px;
        margin-right: 5px;
    }
    .badge-pg { background-color: #E3F2FD; color: #1565C0; }
    .badge-mg { background-color: #E8F8F5; color: #00897B; }
    .badge-sp { background-color: #FBE9E7; color: #D84315; }
    .badge-hd { background-color: #FFF8E1; color: #F57F17; }
</style>
""", unsafe_allow_html=True)

# Importar submódulos del sistema
from modules import overview, postgres_module, mongo_module, spark_module, hdfs_module, benchmark_module

def main():
    # Menú lateral de navegación
    with st.sidebar:
        st.title("SmartCity Analytics")
        st.caption("CE-3101 Bases de Datos | II Semestre 2026")
        st.markdown("**Equipo RIC** (Arce, Elizondo, Prieto)")
        st.divider()

        modulo = st.radio(
            "Navegación del Sistema:",
            [
                "Visión General de la Arquitectura",
                "Módulo Relacional (PostgreSQL)",
                "Módulo Documental (MongoDB)",
                "Módulo Analítico Distribuido (Apache Spark)",
                "Data Lake Distribuido (Hadoop HDFS)",
                "Evaluación de Rendimiento (Benchmark)",
                "Ficha Técnica de la Entrega"
            ]
        )

        st.divider()
        st.caption("Tecnologías Integradas:")
        st.markdown(
            """
            <span class="tech-badge badge-pg">PostgreSQL 15</span>
            <span class="tech-badge badge-mg">MongoDB 6.0</span>
            <br/><br/>
            <span class="tech-badge badge-sp">Apache Spark 3.5</span>
            <span class="tech-badge badge-hd">Hadoop HDFS 3.2</span>
            """,
            unsafe_allow_html=True
        )

    # Renderizado condicional según el módulo seleccionado
    if modulo == "Visión General de la Arquitectura":
        overview.render()

    elif modulo == "Módulo Relacional (PostgreSQL)":
        postgres_module.render()

    elif modulo == "Módulo Documental (MongoDB)":
        mongo_module.render()

    elif modulo == "Módulo Analítico Distribuido (Apache Spark)":
        spark_module.render()

    elif modulo == "Data Lake Distribuido (Hadoop HDFS)":
        hdfs_module.render()

    elif modulo == "Evaluación de Rendimiento (Benchmark)":
        benchmark_module.render()

    elif modulo == "Ficha Técnica de la Entrega":
        st.title("Ficha Técnica de la Entrega (Sprint 2)")
        st.markdown(
            """
            ### Proyecto: SmartCity Analytics
            * **Institución:** Instituto Tecnológico de Costa Rica (TEC)
            * **Escuela:** Escuela de Ingeniería en Computadores
            * **Curso:** CE-3101 Bases de Datos — II Semestre 2026
            * **Equipo de Trabajo (RIC):**
              * Rodrigo Arce Bastos (2024115582)
              * Dylan Elizondo Picado (2023086320)
              * Allan Rubén Prieto Badilla (2021032988)
            * **Profesor:** Marco Rivera Meneses
            
            ---

            ### Justificación Técnica de la Etapa 7 (*Publicación e Interfaz*):
            > *"Guardar resultados y conectarlos al panel. Consultas por tecnología y gráfico con procedencia Spark demostrable."*
            
            La presente interfaz centralizada satisface dicho criterio a través de los siguientes componentes:
            1. **Segmentación Tecnológica:** Vistas especializadas y desacopladas para PostgreSQL, MongoDB, Hadoop HDFS y Apache Spark.
            2. **Consultas Analíticas y de Negocio:** Incorporación de las preguntas de negocio sobre el esquema relacional y los diez análisis distribuidos masivos.
            3. **Trazabilidad y Linaje:** Inclusión de metadatos explícitos de procedencia técnica (`[SPARK LINEAGE]`) en cada agregación analítica.
            4. **Comprobación de Operaciones CRUD:** Interfaz funcional para la verificación de operaciones de manipulación documental en MongoDB (`insertOne`, `find`, `updateOne`, `deleteOne`).
            5. **Tolerancia a Desconexión:** Capacidad de operar tanto contra los servicios activos en contenedores Docker como mediante datasets representativos locales en caso de mantenimiento de la infraestructura.
            """
        )

if __name__ == "__main__":
    main()
