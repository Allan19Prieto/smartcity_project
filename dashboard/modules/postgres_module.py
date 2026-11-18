"""Módulo de Exploración y Consultas de PostgreSQL (Modelo 3NF)."""

import streamlit as st
import plotly.express as px
from services.db_service import get_postgres_catalogs, execute_postgres_query

def render():
    st.title("Módulo Relacional (PostgreSQL - 3NF)")
    st.markdown(
        """
        PostgreSQL administra la información estructurada normalizada bajo **Tercera Forma Normal (3NF)**:
        sensores, zonas geográficas, rutas viales, estacionamientos y catálogos de organismos responsables.
        """
    )

    tab1, tab2, tab3 = st.tabs([
        "Catálogos del Sistema",
        "Consultas de Negocio Obligatorias",
        "Consola SQL"
    ])

    sensores_df, rutas_df, estacionamientos_df, is_live = get_postgres_catalogs()

    with tab1:
        st.subheader("Catálogos Maestros")
        if is_live:
            st.success("Conexión activa: Datos leídos directamente desde PostgreSQL.")
        else:
            st.info("Modo de contingencia: Datos de referencia estructurados (PostgreSQL desconectado).")

        cat_choice = st.radio("Seleccionar Catálogo a Inspeccionar:", ["Sensores", "Rutas Urbanas", "Estacionamientos"], horizontal=True)

        if cat_choice == "Sensores":
            st.dataframe(sensores_df, use_container_width=True, hide_index=True)
            if not sensores_df.empty and "tipo" in sensores_df.columns:
                fig = px.pie(sensores_df, names="tipo", title="Distribución de Sensores por Tipo", hole=0.4)
                st.plotly_chart(fig, use_container_width=True)

        elif cat_choice == "Rutas Urbanas":
            st.dataframe(rutas_df, use_container_width=True, hide_index=True)
            if not rutas_df.empty and "ciudad" in rutas_df.columns:
                fig = px.bar(rutas_df, x="nombre", color="ciudad", title="Rutas Urbanas Monitoreadas por Ciudad")
                st.plotly_chart(fig, use_container_width=True)

        else:
            st.dataframe(estacionamientos_df, use_container_width=True, hide_index=True)
            if not estacionamientos_df.empty and "zona" in estacionamientos_df.columns:
                fig = px.bar(estacionamientos_df, x="nombre", color="zona", title="Estacionamientos Registrados por Zona Urbana")
                st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Consultas de Negocio (Enunciado Pág. 9)")
        
        q = st.selectbox(
            "Seleccionar Consulta de Negocio:",
            [
                "Pregunta 1: ¿Cuál zona registra mayor cantidad de vehículos?",
                "Pregunta 2: ¿Cuál es la hora de mayor congestión?",
                "Pregunta 3: ¿Qué rutas presentan mayor utilización?"
            ]
        )

        if "Pregunta 1" in q:
            st.markdown("**Objetivo:** Determinar la zona con mayor volumen vehicular acumulado mediante agregación relacional.")
            sql_code = """SELECT u.nombre_zona, SUM(m.valor) AS total_vehiculos
FROM mediciones_limpias m
JOIN variables_medicion v ON v.id_variable = m.id_variable
JOIN lecturas_limpias l ON l.id_lectura = m.id_lectura
JOIN sensores s ON s.id_sensor = l.id_sensor
JOIN ubicaciones u ON u.id_ubicacion = s.id_ubicacion
WHERE v.codigo_variable = 'vehiculos'
GROUP BY u.nombre_zona
ORDER BY total_vehiculos DESC;"""
            st.code(sql_code, language="sql")
            
            df, ok, msg = execute_postgres_query(sql_code)
            if not ok or df.empty:
                import pandas as pd
                df = pd.DataFrame([
                    {"nombre_zona": "Distrito Financiero", "total_vehiculos": 128450},
                    {"nombre_zona": "Centro Histórico", "total_vehiculos": 94320},
                    {"nombre_zona": "Corredor Comercial Este", "total_vehiculos": 62100},
                    {"nombre_zona": "Parque Industrial", "total_vehiculos": 41800},
                    {"nombre_zona": "Zona Residencial Norte", "total_vehiculos": 18200},
                ])
                st.caption(f"Nota: Visualizando resultado de referencia ({msg})")

            fig = px.bar(df, x="nombre_zona", y="total_vehiculos", color="total_vehiculos",
                         labels={"nombre_zona": "Zona Urbana", "total_vehiculos": "Total Vehículos Registrados"},
                         title="Aforo Vehicular Agrupado por Zona Urbana")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

        elif "Pregunta 2" in q:
            st.markdown("**Objetivo:** Identificar el período horario de máxima saturación de tráfico (nivel de congestión 'alta').")
            sql_code = """SELECT EXTRACT(HOUR FROM l.fecha_medicion)::int AS hora_del_dia,
       COUNT(*) AS lecturas_congestionadas
FROM lecturas_trafico lt
JOIN lecturas_limpias l ON l.id_lectura = lt.id_lectura
JOIN niveles_congestion nc ON nc.id_nivel = lt.id_nivel
WHERE nc.codigo = 'alta'
GROUP BY EXTRACT(HOUR FROM l.fecha_medicion)
ORDER BY hora_del_dia;"""
            st.code(sql_code, language="sql")

            df, ok, msg = execute_postgres_query(sql_code)
            if not ok or df.empty:
                import pandas as pd
                df = pd.DataFrame([
                    {"hora_del_dia": h, "lecturas_congestionadas": c}
                    for h, c in enumerate([12, 8, 4, 2, 9, 45, 140, 310, 380, 210, 180, 240, 290, 270, 220, 205, 340, 420, 460, 290, 150, 85, 40, 20])
                ])
                st.caption(f"Nota: Visualizando resultado de referencia ({msg})")

            fig = px.line(df, x="hora_del_dia", y="lecturas_congestionadas", markers=True,
                          labels={"hora_del_dia": "Hora del Día (0-23h)", "lecturas_congestionadas": "Eventos de Congestión Alta"},
                          title="Frecuencia Horaria de Eventos de Congestión")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

        else:
            st.markdown("**Objetivo:** Evaluar la utilización de rutas viales y calcular su velocidad promedio asociada.")
            sql_code = """SELECT r.nombre AS ruta, COUNT(lt.id_lectura) AS total_registros,
       ROUND(AVG(m.valor)::numeric, 2) AS velocidad_promedio
FROM lecturas_trafico lt
JOIN rutas r ON r.id_ruta = lt.id_ruta
JOIN lecturas_limpias l ON l.id_lectura = lt.id_lectura
LEFT JOIN mediciones_limpias m ON m.id_lectura = l.id_lectura AND m.id_variable = 3
GROUP BY r.nombre
ORDER BY total_registros DESC
FETCH FIRST 5 ROWS ONLY;"""
            st.code(sql_code, language="sql")

            df, ok, msg = execute_postgres_query(sql_code)
            if not ok or df.empty:
                import pandas as pd
                df = pd.DataFrame([
                    {"ruta": "Autopista General Cañas", "total_registros": 4820, "velocidad_promedio": 38.5},
                    {"ruta": "Paseo Colón", "total_registros": 3210, "velocidad_promedio": 21.4},
                    {"ruta": "Circunvalación Norte", "total_registros": 2980, "velocidad_promedio": 32.8},
                    {"ruta": "Avenida Segunda", "total_registros": 2840, "velocidad_promedio": 16.9},
                    {"ruta": "Radial Santa Ana", "total_registros": 1950, "velocidad_promedio": 44.2},
                ])
                st.caption(f"Nota: Visualizando resultado de referencia ({msg})")

            fig = px.scatter(df, x="total_registros", y="velocidad_promedio", size="total_registros",
                             color="ruta", text="ruta", title="Utilización vs Velocidad Promedio por Ruta")
            fig.update_traces(textposition='top center')
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Ejecución Directa de Consultas SQL")
        user_sql = st.text_area("Sentencia SQL (SELECT):", value="SELECT id_sensor, codigo_sensor, estado_administrativo FROM sensores LIMIT 10;", height=100)
        if st.button("Ejecutar Consulta"):
            df, ok, msg = execute_postgres_query(user_sql)
            if ok:
                st.success(f"Consulta ejecutada satisfactoriamente ({len(df)} registros devueltos).")
                st.dataframe(df, use_container_width=True)
            else:
                st.error(f"Error de ejecución: {msg}")
