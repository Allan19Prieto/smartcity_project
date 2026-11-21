"""Módulo de Visión General y Estado del Ecosistema SmartCity."""

import streamlit as st
import streamlit.components.v1 as components
from services.db_service import get_cluster_status

def render_mermaid(diagram_code: str, height: int = 560):
    """Renderiza diagramas de arquitectura en Mermaid con soporte de subgrafos y tema profesional."""
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{
                startOnLoad: true,
                theme: 'dark',
                securityLevel: 'loose',
                themeVariables: {{
                    darkMode: true,
                    background: 'transparent',
                    primaryColor: '#1e293b',
                    primaryTextColor: '#f8fafc',
                    primaryBorderColor: '#38bdf8',
                    lineColor: '#64748b',
                    secondaryColor: '#0f172a',
                    tertiaryColor: '#1e293b',
                    fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
                    fontSize: '13px'
                }}
            }});
        </script>
        <style>
            body {{
                margin: 0;
                padding: 10px;
                background-color: transparent;
                display: flex;
                justify-content: center;
                align-items: center;
                font-family: Inter, system-ui, -apple-system, sans-serif;
            }}
            .mermaid {{
                width: 100%;
                text-align: center;
            }}
            svg {{
                max-width: 100%;
                height: auto;
            }}
        </style>
    </head>
    <body>
        <pre class="mermaid">
{diagram_code}
        </pre>
    </body>
    </html>
    """
    components.html(html_code, height=height, scrolling=False)

def render():
    st.title("Panel Centralizado de Monitoreo Urbano")
    st.markdown(
        """
        Plataforma unificada para la observación y análisis de la infraestructura urbana de SmartCity Analytics.
        El sistema consolida los cuatro motores principales de la arquitectura: **PostgreSQL** para catálogos
        estructurados en 3NF, **MongoDB** para telemetría IoT semiestructurada, **Hadoop HDFS** como Data Lake distribuido
        y **Apache Spark** para el procesamiento analítico masivo en memoria.
        """
    )
    
    st.divider()

    # 1. ESTADO DE LOS SERVICIOS DEL CLÚSTER
    st.subheader("Estado de Conectividad de los Motores de Datos")
    cluster_status = get_cluster_status(force_refresh=st.button("Actualizar Diagnóstico de Conexión"))

    cols = st.columns(4)
    for col, (engine, data) in zip(cols, cluster_status.items()):
        with col:
            status_indicator = "ACTIVO" if data["online"] else "CONTINGENCIA LOCAL"
            st.metric(
                label=f"{engine}",
                value=status_indicator,
                help=data["detail"]
            )
            st.caption(f"**Función:** {data['role']}")
            st.caption(f"_{data['detail']}_")

    st.divider()

    # 2. MÉTRICAS GLOBALES DEL SISTEMA
    st.subheader("Indicadores Operativos Globales")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Sensores Registrados", "100 Dispositivos", "Catálogo maestro PostgreSQL")
    kpi2.metric("Volumen de Observaciones", "> 535.800 Registros", "PostgreSQL / MongoDB")
    kpi3.metric("Zonas Monitoreadas", "5 Distritos", "Cobertura metropolitana")
    kpi4.metric("Ocupación Media Global", "68.4%", "Red de estacionamientos")

    st.divider()

    # 3. DIAGRAMA ARQUITECTÓNICO DEL PIPELINE DE DATOS EN MERMAID
    st.subheader("Topología Arquitectónica del Pipeline (Extremo a Extremo)")
    st.markdown(
        """
        Diagrama de flujo multicapa que ilustra la ingesta desde fuentes heterogéneas, la persistencia transaccional y documental,
        el ciclo de vida en el Data Lake Hadoop HDFS con Apache Spark, y la entrega final en la interfaz analítica:
        """
    )

    mermaid_pipeline = """
flowchart LR
    subgraph S1 ["1. Fuentes Primarias"]
        F1["CSV Birmingham Parking"]
        F2["CSV Trafico Vehicular"]
        F3["Telemetria IoT Sintetica"]
    end

    subgraph S2 ["2. Ingesta y Limpieza"]
        ETL["Normalizacion UTC y 3NF<br/>Validacion de Integridad"]
    end

    subgraph S3 ["3. Persistencia Base (Sprint 1)"]
        PG[("PostgreSQL 15<br/>17 Tablas en 3NF")]
        MG[("MongoDB 6.0<br/>Coleccion IoT BSON")]
    end

    subgraph S4 ["4. Data Lake y Spark (Sprint 2)"]
        HDFS[("Hadoop HDFS<br/>/crudo y /depurado")]
        SPARK{{"Apache Spark 3.5.1<br/>10 Analisis Masivos"}}
        PARQUET[("Datasets Parquet<br/>Snappy Columnar")]
        HDFS --> SPARK
        SPARK --> PARQUET
    end

    subgraph S5 ["5. Publicacion"]
        DASH["Dashboard Streamlit<br/>Trazabilidad y Benchmark"]
    end

    F1 --> ETL
    F2 --> ETL
    F3 --> ETL
    ETL --> PG
    ETL --> MG
    ETL --> HDFS
    PG --> DASH
    MG --> DASH
    PARQUET --> DASH

    style S1 fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#fff
    style S2 fill:#0f172a,stroke:#4ade80,stroke-width:2px,color:#fff
    style S3 fill:#0f172a,stroke:#a78bfa,stroke-width:2px,color:#fff
    style S4 fill:#0f172a,stroke:#fb923c,stroke-width:2px,color:#fff
    style S5 fill:#0f172a,stroke:#f472b6,stroke-width:2px,color:#fff

    style F1 fill:#1e293b,stroke:#38bdf8,color:#fff
    style F2 fill:#1e293b,stroke:#38bdf8,color:#fff
    style F3 fill:#1e293b,stroke:#38bdf8,color:#fff
    style ETL fill:#1e293b,stroke:#4ade80,color:#fff
    style PG fill:#1e293b,stroke:#a78bfa,color:#fff
    style MG fill:#1e293b,stroke:#a78bfa,color:#fff
    style HDFS fill:#1e293b,stroke:#fb923c,color:#fff
    style SPARK fill:#1e293b,stroke:#fb923c,color:#fff
    style PARQUET fill:#1e293b,stroke:#fb923c,color:#fff
    style DASH fill:#1e293b,stroke:#f472b6,color:#fff
"""
    render_mermaid(mermaid_pipeline, height=480)
