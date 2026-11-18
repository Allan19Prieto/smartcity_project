"""Módulo de Visión General y Estado del Ecosistema SmartCity."""

import streamlit as st
from services.db_service import get_cluster_status

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

    # 3. DIAGRAMA ARQUITECTÓNICO DEL PIPELINE DE DATOS
    st.subheader("Flujo y Transformación de la Información (Pipeline Extremo a Extremo)")
    st.markdown(
        """
        El recorrido de los datos se estructura en cinco etapas secuenciales y desacopladas, garantizando
        inmutabilidad en el almacenamiento en crudo y alta eficiencia en el procesamiento distribuido:
        """
    )

    pipeline_html = """
    <div style="display: flex; flex-direction: row; flex-wrap: wrap; gap: 12px; justify-content: space-between; margin-top: 15px; margin-bottom: 25px;">
        
        <!-- Etapa 1 -->
        <div style="flex: 1; min-width: 180px; background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; border-radius: 8px; padding: 14px;">
            <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Etapa 1</div>
            <div style="font-size: 1rem; font-weight: 700; color: #38BDF8; margin-top: 4px; margin-bottom: 8px;">Fuentes Primarias</div>
            <div style="font-size: 0.85rem; color: #CBD5E1; line-height: 1.4;">
                • CSV Parking Birmingham<br/>
                • CSV Tráfico Multi-Ciudad<br/>
                • Generador Sintético IoT
            </div>
            <div style="margin-top: 10px; font-size: 0.75rem; background: rgba(56, 189, 248, 0.15); color: #38BDF8; padding: 3px 6px; border-radius: 4px; display: inline-block;">
                Formato CSV / JSON
            </div>
        </div>

        <div style="display: flex; align-items: center; color: #64748B; font-size: 1.2rem;">➔</div>

        <!-- Etapa 2 -->
        <div style="flex: 1; min-width: 180px; background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; border-radius: 8px; padding: 14px;">
            <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Etapa 2</div>
            <div style="font-size: 1rem; font-weight: 700; color: #4ADE80; margin-top: 4px; margin-bottom: 8px;">Ingesta y Validación</div>
            <div style="font-size: 0.85rem; color: #CBD5E1; line-height: 1.4;">
                • Normalización temporal UTC<br/>
                • Filtrado de no numéricos<br/>
                • Reglas de integridad 3NF
            </div>
            <div style="margin-top: 10px; font-size: 0.75rem; background: rgba(74, 222, 128, 0.15); color: #4ADE80; padding: 3px 6px; border-radius: 4px; display: inline-block;">
                Validación Python
            </div>
        </div>

        <div style="display: flex; align-items: center; color: #64748B; font-size: 1.2rem;">➔</div>

        <!-- Etapa 3 -->
        <div style="flex: 1; min-width: 180px; background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; border-radius: 8px; padding: 14px;">
            <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Etapa 3</div>
            <div style="font-size: 1rem; font-weight: 700; color: #A78BFA; margin-top: 4px; margin-bottom: 8px;">Persistencia Base</div>
            <div style="font-size: 0.85rem; color: #CBD5E1; line-height: 1.4;">
                • <b>PostgreSQL:</b> 17 tablas en 3NF<br/>
                • <b>MongoDB:</b> Telemetría IoT<br/>
                • Enlace por claves cruzadas
            </div>
            <div style="margin-top: 10px; font-size: 0.75rem; background: rgba(167, 139, 250, 0.15); color: #A78BFA; padding: 3px 6px; border-radius: 4px; display: inline-block;">
                SQL Relacional + NoSQL
            </div>
        </div>

        <div style="display: flex; align-items: center; color: #64748B; font-size: 1.2rem;">➔</div>

        <!-- Etapa 4 -->
        <div style="flex: 1; min-width: 180px; background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; border-radius: 8px; padding: 14px;">
            <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Etapa 4</div>
            <div style="font-size: 1rem; font-weight: 700; color: #FB923C; margin-top: 4px; margin-bottom: 8px;">Data Lake & Spark</div>
            <div style="font-size: 0.85rem; color: #CBD5E1; line-height: 1.4;">
                • <b>HDFS:</b> Histórico crudo y Parquet<br/>
                • <b>Apache Spark 3.5:</b> Motor masivo<br/>
                • 10 Análisis obligatorios
            </div>
            <div style="margin-top: 10px; font-size: 0.75rem; background: rgba(251, 146, 60, 0.15); color: #FB923C; padding: 3px 6px; border-radius: 4px; display: inline-block;">
                Big Data Distribuido
            </div>
        </div>

        <div style="display: flex; align-items: center; color: #64748B; font-size: 1.2rem;">➔</div>

        <!-- Etapa 5 -->
        <div style="flex: 1; min-width: 180px; background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; border-radius: 8px; padding: 14px;">
            <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Etapa 5</div>
            <div style="font-size: 1rem; font-weight: 700; color: #F472B6; margin-top: 4px; margin-bottom: 8px;">Publicación e Interfaz</div>
            <div style="font-size: 0.85rem; color: #CBD5E1; line-height: 1.4;">
                • Dashboard Centralizado<br/>
                • Trazabilidad [SPARK LINEAGE]<br/>
                • Consultas por tecnología
            </div>
            <div style="margin-top: 10px; font-size: 0.75rem; background: rgba(244, 114, 182, 0.15); color: #F472B6; padding: 3px 6px; border-radius: 4px; display: inline-block;">
                Streamlit + Plotly
            </div>
        </div>

    </div>
    """
    st.markdown(pipeline_html, unsafe_allow_html=True)
