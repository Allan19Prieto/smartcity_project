"""Módulo de Exploración y Operaciones CRUD en MongoDB (Colecciones IoT)."""

import json
import streamlit as st
import pandas as pd
from datetime import datetime
from services.db_service import get_mongo_telemetry, get_mongo_alerts, check_mongo_connection
from config import MONGO_URI, MONGO_DB

def render():
    st.title("Módulo Documental (MongoDB - Telemetría IoT)")
    st.markdown(
        """
        MongoDB almacena las observaciones semiestructuradas de los sensores urbanos,
        eventos de anomalía, alertas operativas y registros de incidentes.
        """
    )

    tab1, tab2, tab3 = st.tabs([
        "Telemetría de Sensores",
        "Registro de Alertas e Incidentes",
        "Verificación de Operaciones CRUD"
    ])

    with tab1:
        st.subheader("Observaciones Recientes (Colección 'lecturas')")
        limit = st.slider("Cantidad de documentos a recuperar:", 5, 50, 15)
        df_telemetry, is_live = get_mongo_telemetry(limit=limit)

        if is_live:
            st.success("Conexión activa: Lectura directa desde la base de datos 'smartcity_db' en MongoDB.")
        else:
            st.info("Modo de contingencia: Datos de telemetría de referencia (MongoDB desconectado).")

        st.dataframe(df_telemetry, use_container_width=True)

        st.markdown("#### Estructura del Documento BSON / JSON")
        if not df_telemetry.empty:
            doc_idx = st.selectbox("Seleccionar documento para inspección:", range(len(df_telemetry)))
            selected_row = df_telemetry.iloc[doc_idx].to_dict()
            st.json(selected_row)

    with tab2:
        st.subheader("Histórico de Alertas Urbanas")
        df_alerts, is_live_alt = get_mongo_alerts()
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            niveles = ["TODOS"] + list(df_alerts["nivel"].unique()) if "nivel" in df_alerts.columns else ["TODOS"]
            nivel_sel = st.selectbox("Filtrar por Nivel de Severidad:", niveles)
        with col_f2:
            tipos = ["TODOS"] + list(df_alerts["tipo"].unique()) if "tipo" in df_alerts.columns else ["TODOS"]
            tipo_sel = st.selectbox("Filtrar por Tipología:", tipos)

        filtered_alerts = df_alerts.copy()
        if nivel_sel != "TODOS":
            filtered_alerts = filtered_alerts[filtered_alerts["nivel"] == nivel_sel]
        if tipo_sel != "TODOS":
            filtered_alerts = filtered_alerts[filtered_alerts["tipo"] == tipo_sel]

        st.dataframe(filtered_alerts, use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Comprobación de Operaciones de Manipulación Documental (CRUD)")
        st.markdown(
            """
            Validación interactiva de las cuatro operaciones fundamentales sobre la colección `crud_demo`:
            inserción (`insertOne`), consulta (`find`), actualización (`updateOne`) y eliminación (`deleteOne`).
            """
        )

        crud_op = st.radio("Operación a Ejecutar:", ["1. Creación (insertOne)", "2. Lectura (find)", "3. Actualización (updateOne)", "4. Eliminación (deleteOne)"], horizontal=True)

        mongo_ok, _ = check_mongo_connection()

        if "Creación" in crud_op:
            st.markdown("##### Inserción de Documento (`insertOne`)")
            col_i1, col_i2 = st.columns(2)
            with col_i1:
                ins_id = st.text_input("Identificador Único (_id):", value=f"demo-{int(datetime.now().timestamp())}")
                ins_proyecto = st.text_input("Atributo 'proyecto':", value="smartcity-sprint2")
            with col_i2:
                ins_valor = st.number_input("Atributo 'valor':", value=42)
                ins_activo = st.checkbox("Atributo 'activo':", value=True)

            if st.button("Ejecutar Inserción"):
                if mongo_ok:
                    try:
                        from pymongo import MongoClient
                        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
                        db = client[MONGO_DB]
                        db.crud_demo.insert_one({"_id": ins_id, "proyecto": ins_proyecto, "valor": ins_valor, "activo": ins_activo, "fecha": datetime.now()})
                        client.close()
                        st.success(f"Documento '{ins_id}' insertado correctamente en la colección 'crud_demo'.")
                    except Exception as e:
                        st.error(f"Fallo en la operación de inserción: {e}")
                else:
                    st.success(f"Operación simulada: Documento '{ins_id}' registrado en memoria.")

        elif "Lectura" in crud_op:
            st.markdown("##### Consulta de Documentos (`find`)")
            if st.button("Consultar Registros en crud_demo"):
                if mongo_ok:
                    try:
                        from pymongo import MongoClient
                        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
                        db = client[MONGO_DB]
                        docs = list(db.crud_demo.find({}).limit(20))
                        client.close()
                        for d in docs:
                            d["_id"] = str(d.get("_id", ""))
                        st.dataframe(pd.DataFrame(docs), use_container_width=True)
                    except Exception as e:
                        st.error(f"Fallo en la consulta: {e}")
                else:
                    st.info("Registros de demostración en 'crud_demo':")
                    st.json([
                        {"_id": "demo-1", "proyecto": "smartcity-sprint2", "valor": 99, "activo": False},
                        {"_id": "demo-2", "proyecto": "smartcity-sprint2", "valor": 20, "activo": True},
                    ])

        elif "Actualización" in crud_op:
            st.markdown("##### Actualización de Documento (`updateOne`)")
            upd_id = st.text_input("Identificador del Documento a Modificar (_id):", value="demo-1")
            nuevo_valor = st.number_input("Nuevo valor a asignar:", value=150)
            if st.button("Ejecutar Actualización"):
                if mongo_ok:
                    try:
                        from pymongo import MongoClient
                        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
                        db = client[MONGO_DB]
                        res = db.crud_demo.update_one({"_id": upd_id}, {"$set": {"valor": nuevo_valor}})
                        client.close()
                        st.success(f"Documentos modificados en la colección: {res.modified_count}")
                    except Exception as e:
                        st.error(f"Fallo en la actualización: {e}")
                else:
                    st.success(f"Operación simulada: Documento '{upd_id}' actualizado con valor {nuevo_valor}.")

        else:
            st.markdown("##### Eliminación de Documento (`deleteOne`)")
            del_id = st.text_input("Identificador del Documento a Eliminar (_id):", value="demo-1")
            if st.button("Ejecutar Eliminación"):
                if mongo_ok:
                    try:
                        from pymongo import MongoClient
                        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
                        db = client[MONGO_DB]
                        res = db.crud_demo.delete_one({"_id": del_id})
                        client.close()
                        st.success(f"Documentos eliminados de la colección: {res.deleted_count}")
                    except Exception as e:
                        st.error(f"Fallo en la eliminación: {e}")
                else:
                    st.success(f"Operación simulada: Documento '{del_id}' eliminado.")
