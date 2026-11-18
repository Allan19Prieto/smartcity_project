"""Módulo de Analítica Distribuida con Apache Spark (10 Resultados Obligatorios)."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from services.db_service import get_spark_analytics

def render():
    st.title("Módulo Analítico Distribuido (Apache Spark)")
    st.markdown(
        """
        Este módulo presenta los **diez resultados analíticos obligatorios del Sprint 2**,
        procesados sobre volúmenes masivos mediante transformaciones y acciones en **Apache Spark (PySpark DataFrame)**
        a partir de los datos consolidados de las fuentes primarias y el Data Lake HDFS.
        """
    )

    analytics, is_live = get_spark_analytics()

    if is_live:
        st.success("Procedencia técnica: Motor Apache Spark 3.5.1 en clúster activo | API: PySpark DataFrame | Trazabilidad HDFS: Verificada.")
    else:
        st.info("Procedencia técnica: Pipeline analítico de Apache Spark (Datos cacheados de referencia desde Data Lake HDFS).")

    st.divider()

    analisis_lista = [
        "1. Ocupación Promedio de Parqueos por Zona Urbana",
        "2. Horas Pico y Evolución de Congestión Vehicular",
        "3. Ranking de Rutas Viales de Mayor Aforo",
        "4. Detección de Eventos Críticos y Anomalías",
        "5. Correlación: Velocidad Media vs Calidad del Aire (AQI)",
        "6. Proporción de Flota: Vehículos Comerciales vs Particulares",
        "7. Incidentes Viales y Criticidad por Cuadrante",
        "8. Capacidad de Diseño vs Ocupación Máxima Registrada",
        "9. Tendencia Anual de Congestión y Emisiones de CO2",
        "10. Disponibilidad y Plazas Libres Estimadas en Tiempo Real"
    ]

    seleccion = st.selectbox("Seleccionar Indicador Analítico:", analisis_lista)

    st.markdown(
        '<div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; border-left: 4px solid #38BDF8; border-radius: 6px; padding: 10px 14px; margin-bottom: 14px;">'
        '<span style="font-weight: 700; color: #38BDF8; font-family: monospace; font-size: 0.9rem;">[SPARK LINEAGE]</span> '
        '<span style="color: #CBD5E1; font-size: 0.88rem; margin-left: 8px;">'
        'Dataset de origen: <code>hdfs://namenode:9000/historico_smartcity/depurado/</code> &bull; '
        'Transformación: PySpark DataFrame Aggregation &bull; Particionamiento: 8 particiones en clúster'
        '</span>'
        '</div>',
        unsafe_allow_html=True
    )

    # 1. OCUPACIÓN PROMEDIO
    if "1. Ocupación" in seleccion:
        df1 = analytics["q1_ocupacion_zona"]
        st.subheader("1. Ocupación Promedio de Parqueos por Zona Urbana")
        st.markdown("**Planteamiento:** Identificar las zonas con mayor tasa de ocupación porcentual respecto a su capacidad nominal.")

        fig = px.bar(
            df1, x="zona", y="ocupacion_promedio_pct", color="ocupacion_promedio_pct",
            text="ocupacion_promedio_pct", color_continuous_scale="Reds",
            labels={"zona": "Zona Urbana", "ocupacion_promedio_pct": "Ocupación Promedio (%)"},
            title="Porcentaje Promedio de Ocupación por Zona"
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df1, use_container_width=True, hide_index=True)

        with st.expander("Especificación del Pipeline PySpark"):
            st.code("""# Transformación distribuida en Apache Spark
df_spark = spark.read.parquet("hdfs://namenode:9000/historico_smartcity/depurado/")

df_analisis_1 = df_spark.filter(col("tipo") == "estacionamiento") \\
    .groupBy("contexto.nombre_zona") \\
    .agg(
        avg("mediciones.ocupacion").alias("promedio_ocupacion"),
        avg("mediciones.capacidad").alias("promedio_capacidad")
    ) \\
    .withColumn("ocupacion_promedio_pct", (col("promedio_ocupacion") / col("promedio_capacidad")) * 100) \\
    .orderBy(desc("ocupacion_promedio_pct"))

df_analisis_1.show()""", language="python")

    # 2. HORAS PICO
    elif "2. Horas" in seleccion:
        df2 = analytics["q2_congestion_hora"]
        st.subheader("2. Horas Pico y Evolución de Congestión Vehicular")
        st.markdown("**Planteamiento:** Analizar la curva horaria (0 a 23h) de flujo vehicular y su impacto inverso en la velocidad de circulación.")

        fig = go.Figure()
        fig.add_trace(go.Bar(x=df2["hora"], y=df2["volumen_vehicular"], name="Aforo Vehicular (veh/h)", marker_color="#1E88E5", opacity=0.7))
        fig.add_trace(go.Scatter(x=df2["hora"], y=df2["velocidad_kmh"], name="Velocidad Media (km/h)", yaxis="y2", line=dict(color="#D81B60", width=2.5), mode="lines+markers"))

        fig.update_layout(
            title="Aforo Vehicular vs Velocidad Media por Hora",
            xaxis=dict(title="Hora del Día (0 a 23h)", tickmode="linear", dtick=2),
            yaxis=dict(title="Volumen Vehicular"),
            yaxis2=dict(title="Velocidad (km/h)", overlaying="y", side="right"),
            legend=dict(x=0.01, y=0.99)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df2, use_container_width=True, hide_index=True)

    # 3. RANKING DE RUTAS
    elif "3. Ranking" in seleccion:
        df3 = analytics["q3_rutas_ranking"]
        st.subheader("3. Ranking de Rutas Viales de Mayor Aforo")
        st.markdown("**Planteamiento:** Determinar las arterias de la red vial con mayor tráfico acumulado y su nivel de congestión.")

        fig = px.bar(
            df3, y="ruta", x="volumen_diario_estimado", orientation="h",
            color="nivel_congestion", color_discrete_map={"Severo": "#C62828", "Alto": "#EF6C00", "Medio-Alto": "#F9A825", "Moderado": "#2E7D32"},
            labels={"ruta": "Arteria Vial", "volumen_diario_estimado": "Volumen Diario Estimado (vehículos)"},
            title="Aforo Diario en Rutas Principales"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df3, use_container_width=True, hide_index=True)

    # 4. EVENTOS CRÍTICOS
    elif "4. Detección" in seleccion:
        df4 = analytics["q4_eventos_criticos"]
        st.subheader("4. Detección de Eventos Críticos y Anomalías")
        st.markdown("**Planteamiento:** Clasificar y cuantificar las anomalías operativas registradas por los sensores.")

        fig = px.pie(
            df4, names="tipo_evento", values="ocurrencias", hole=0.45,
            color="tipo_evento",
            title="Distribución de Eventos Críticos Identificados"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df4, use_container_width=True, hide_index=True)

    # 5. VELOCIDAD VS AQI
    elif "5. Correlación" in seleccion:
        df5 = analytics["q5_velocidad_aqi"]
        st.subheader("5. Correlación: Velocidad Media vs Calidad del Aire (AQI)")
        st.markdown("**Planteamiento:** Evaluar la relación empírica entre la velocidad media de desplazamiento y el índice de calidad del aire.")

        fig = px.scatter(
            df5, x="velocidad_media_kmh", y="aqi_promedio", size="poblacion_millones",
            color="ciudad", text="ciudad",
            labels={"velocidad_media_kmh": "Velocidad Media (km/h)", "aqi_promedio": "Índice de Calidad del Aire (AQI)"},
            title="Relación entre Flujo Vehicular y Calidad del Aire"
        )
        fig.update_traces(textposition='top center')
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df5, use_container_width=True, hide_index=True)

    # 6. VEHÍCULOS COMERCIALES
    elif "6. Proporción" in seleccion:
        df6 = analytics["q6_vehiculos_tipo"]
        st.subheader("6. Proporción de Flota: Vehículos Comerciales vs Particulares")
        st.markdown("**Planteamiento:** Determinar la composición porcentual de la flota vehicular por metrópoli.")

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Comerciales (%)', x=df6['ciudad'], y=df6['comerciales_pct'], marker_color='#F57C00'))
        fig.add_trace(go.Bar(name='Particulares (%)', x=df6['ciudad'], y=df6['particulares_pct'], marker_color='#1565C0'))
        fig.update_layout(barmode='stack', title="Composición del Parque Vehicular")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df6, use_container_width=True, hide_index=True)

    # 7. INCIDENTES POR ZONA
    elif "7. Incidentes" in seleccion:
        df7 = analytics["q7_incidentes_zona"]
        st.subheader("7. Incidentes Viales y Criticidad por Cuadrante")
        st.markdown("**Planteamiento:** Distribuir geográficamente la tasa de siniestros viales reportados para asignación de recursos.")

        fig = px.bar(
            df7, x="zona", y="accidentes_anuales", color="criticidad",
            color_discrete_map={"Alta": "#C62828", "Media": "#EF6C00", "Baja": "#2E7D32"},
            labels={"zona": "Zona Urbana", "accidentes_anuales": "Total Siniestros Anuales"},
            title="Tasa de Incidentes Viales por Cuadrante Urbano"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df7, use_container_width=True, hide_index=True)

    # 8. CAPACIDAD VS OCUPACIÓN MÁXIMA
    elif "8. Capacidad" in seleccion:
        df8 = analytics["q8_capacidad_max"]
        st.subheader("8. Capacidad de Diseño vs Ocupación Máxima Registrada")
        st.markdown("**Planteamiento:** Contrastar la capacidad teórica con el pico histórico registrado para validar la ausencia de desbordamiento de plazas.")

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Capacidad Total', x=df8['parqueo'], y=df8['capacidad'], marker_color='#78909C'))
        fig.add_trace(go.Bar(name='Ocupación Máxima Registrada', x=df8['parqueo'], y=df8['max_ocupacion_registrada'], marker_color='#00897B'))
        fig.update_layout(barmode='group', title="Auditoría de Capacidad vs Pico de Ocupación")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df8, use_container_width=True, hide_index=True)

    # 9. TENDENCIA ANUAL
    elif "9. Tendencia" in seleccion:
        df9 = analytics["q9_tendencia_mensual"]
        st.subheader("9. Tendencia Anual de Congestión y Emisiones de CO2")
        st.markdown("**Planteamiento:** Mapear la evolución estacional de la congestión y su correspondencia con el volumen de emisiones de CO2.")

        fig = px.area(
            df9, x="mes", y="emisiones_co2_ton", markers=True,
            title="Evolución Mensual de Emisiones de CO2 Estimadas",
            labels={"mes": "Mes", "emisiones_co2_ton": "Toneladas de CO2"}
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df9, use_container_width=True, hide_index=True)

    # 10. PLAZAS LIBRES
    else:
        df10 = analytics["q10_plazas_libres"]
        st.subheader("10. Disponibilidad y Plazas Libres Estimadas en Tiempo Real")
        st.markdown("**Planteamiento:** Calcular la disponibilidad inmediata de estacionamiento para optimizar rutas ciudadanas.")

        fig = px.bar(
            df10, x="cuadrante", y="plazas_libres", color="cuadrante",
            text="plazas_libres",
            labels={"cuadrante": "Cuadrante Urbano", "plazas_libres": "Plazas Libres Disponibles"},
            title="Disponibilidad Inmediata de Espacios"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df10, use_container_width=True, hide_index=True)
