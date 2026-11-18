"""Generador de datos de respaldo y demostración (alta fidelidad).

Basado exactamente en los esquemas de:
- Birmingham Parking Dataset (capacidad y ocupación en tiempo real).
- Multi-City Traffic Dataset (volumen horario, velocidad, AQI, accidentes).
- Esquema relacional PostgreSQL (17 tablas normalizadas en 3NF).
- Colecciones MongoDB (lecturas, eventos, alertas, incidentes).
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

def get_mock_zones():
    return [
        {"id": 1, "nombre": "Centro Histórico", "ciudad": "San José", "sensores": 14, "estado": "Activo"},
        {"id": 2, "nombre": "Distrito Financiero", "ciudad": "San José", "sensores": 18, "estado": "Activo"},
        {"id": 3, "nombre": "Zona Residencial Norte", "ciudad": "Heredia", "sensores": 10, "estado": "Activo"},
        {"id": 4, "nombre": "Parque Industrial", "ciudad": "Alajuela", "sensores": 12, "estado": "Activo"},
        {"id": 5, "nombre": "Corredor Comercial Este", "ciudad": "Cartago", "sensores": 16, "estado": "Activo"},
    ]

def get_mock_postgres_catalogs():
    sensores = pd.DataFrame([
        {"id_sensor": 1, "codigo": "SEN-PRK-001", "tipo": "Estacionamiento", "zona": "Centro Histórico", "organismo": "Dirección General de Tránsito", "estado": "activo", "instalacion": "2024-01-15"},
        {"id_sensor": 2, "codigo": "SEN-PRK-002", "tipo": "Estacionamiento", "zona": "Distrito Financiero", "organismo": "Dirección General de Tránsito", "estado": "activo", "instalacion": "2024-02-10"},
        {"id_sensor": 3, "codigo": "SEN-TRF-001", "tipo": "Tráfico Vehicular", "zona": "Distrito Financiero", "organismo": "Ministerio de Obras Públicas", "estado": "activo", "instalacion": "2024-03-01"},
        {"id_sensor": 4, "codigo": "SEN-TRF-002", "tipo": "Tráfico Vehicular", "zona": "Corredor Comercial Este", "organismo": "Ministerio de Obras Públicas", "estado": "activo", "instalacion": "2024-03-22"},
        {"id_sensor": 5, "codigo": "SEN-ENV-001", "tipo": "Calidad del Aire", "zona": "Parque Industrial", "organismo": "Ministerio de Ambiente", "estado": "activo", "instalacion": "2024-04-05"},
        {"id_sensor": 6, "codigo": "SEN-PRK-003", "tipo": "Estacionamiento", "zona": "Zona Residencial Norte", "organismo": "Dirección General de Tránsito", "estado": "mantenimiento", "instalacion": "2024-05-18"},
        {"id_sensor": 7, "codigo": "SEN-TRF-003", "tipo": "Tráfico Vehicular", "zona": "Centro Histórico", "organismo": "Policía Municipal", "estado": "activo", "instalacion": "2024-06-12"},
    ])

    rutas = pd.DataFrame([
        {"id_ruta": 1, "nombre": "Avenida Segunda", "sentido": "Este-Oeste", "longitud_km": 4.5, "carriles": 3},
        {"id_ruta": 2, "nombre": "Paseo Colón", "sentido": "Oeste-Este", "longitud_km": 3.2, "carriles": 4},
        {"id_ruta": 3, "nombre": "Autopista General Cañas", "sentido": "Norte-Sur", "longitud_km": 12.0, "carriles": 6},
        {"id_ruta": 4, "nombre": "Circunvalación Norte", "sentido": "Anillo", "longitud_km": 8.7, "carriles": 4},
        {"id_ruta": 5, "nombre": "Radial Santa Ana", "sentido": "Sur-Norte", "longitud_km": 5.1, "carriles": 2},
    ])

    estacionamientos = pd.DataFrame([
        {"id_estacionamiento": 1, "nombre": "Parqueo Central Mercado", "zona": "Centro Histórico", "capacidad_total": 450, "tarifa_hora": 1200},
        {"id_estacionamiento": 2, "nombre": "Torre Financiera Plaza", "zona": "Distrito Financiero", "capacidad_total": 780, "tarifa_hora": 1800},
        {"id_estacionamiento": 3, "nombre": "Estación del Este", "zona": "Corredor Comercial Este", "capacidad_total": 320, "tarifa_hora": 950},
        {"id_estacionamiento": 4, "nombre": "Terminal Ferial", "zona": "Parque Industrial", "capacidad_total": 600, "tarifa_hora": 800},
        {"id_estacionamiento": 5, "nombre": "Parque Metropolitano", "zona": "Zona Residencial Norte", "capacidad_total": 250, "tarifa_hora": 500},
    ])
    return sensores, rutas, estacionamientos

def get_mock_mongo_telemetry(n=20):
    now = datetime.now()
    records = []
    tipos = ["estacionamiento", "trafico"]
    zonas = ["Centro Histórico", "Distrito Financiero", "Zona Residencial Norte", "Parque Industrial"]
    
    for i in range(1, n + 1):
        tipo = tipos[i % len(tipos)]
        zona = zonas[i % len(zonas)]
        ts = now - timedelta(minutes=i * 12)
        
        if tipo == "estacionamiento":
            cap = int(np.random.choice([250, 450, 600, 780]))
            occ = int(np.random.randint(int(cap * 0.3), int(cap * 0.95)))
            mediciones = [
                {"codigo": "capacidad", "valor": cap, "unidad": "plazas"},
                {"codigo": "ocupacion", "valor": occ, "unidad": "plazas"}
            ]
        else:
            mediciones = [
                {"codigo": "vehiculos", "valor": int(np.random.randint(20, 180)), "unidad": "veh/min"},
                {"codigo": "velocidad_media", "valor": round(float(np.random.uniform(15.0, 65.0)), 1), "unidad": "km/h"}
            ]

        records.append({
            "_id": f"lec:mock:{i:06d}",
            "id_sensor": (i % 7) + 1,
            "tipo": tipo,
            "fecha_medicion": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "contexto": {"id_ubicacion": (i % 4) + 1, "nombre_zona": zona},
            "mediciones": mediciones,
            "calidad": "valido"
        })
    return pd.DataFrame(records)

def get_mock_mongo_alerts():
    return pd.DataFrame([
        {"id_alerta": "alt:001", "nivel": "CRITICO", "tipo": "Sobreocupación", "zona": "Distrito Financiero", "sensor": "SEN-PRK-002", "detalle": "Ocupación superó 96% de la capacidad de plazas", "fecha": "2026-11-18 10:15:00"},
        {"id_alerta": "alt:002", "nivel": "ALTO", "tipo": "Congestión Severa", "zona": "Centro Histórico", "sensor": "SEN-TRF-001", "detalle": "Velocidad media cayó a 8.5 km/h en Avenida Segunda", "fecha": "2026-11-18 11:30:00"},
        {"id_alerta": "alt:003", "nivel": "MEDIO", "tipo": "Calidad del Aire (AQI)", "zona": "Parque Industrial", "sensor": "SEN-ENV-001", "detalle": "AQI alcanzó 128 (no saludable para grupos sensibles)", "fecha": "2026-11-18 12:05:00"},
        {"id_alerta": "alt:004", "nivel": "ALTO", "tipo": "Flujo Pico Extremo", "zona": "Distrito Financiero", "sensor": "SEN-TRF-003", "detalle": "Caudal de 175 veh/min supera límite de diseño", "fecha": "2026-11-18 12:45:00"},
        {"id_alerta": "alt:005", "nivel": "CRITICO", "tipo": "Incidente Bloqueante", "zona": "Corredor Comercial Este", "sensor": "SEN-TRF-002", "detalle": "Colisión múltiple obstruyendo dos carriles", "fecha": "2026-11-18 13:10:00"},
    ])

def get_mock_spark_10_analytics():
    """Genera exactamente los 10 análisis obligatorios del Sprint 2 calculados por Spark."""
    
    # 1. Ocupación promedio de parqueos por zona
    q1 = pd.DataFrame([
        {"zona": "Distrito Financiero", "ocupacion_promedio_pct": 84.6, "plazas_ocupadas": 660, "capacidad_total": 780},
        {"zona": "Centro Histórico", "ocupacion_promedio_pct": 79.2, "plazas_ocupadas": 356, "capacidad_total": 450},
        {"zona": "Corredor Comercial Este", "ocupacion_promedio_pct": 68.5, "plazas_ocupadas": 219, "capacidad_total": 320},
        {"zona": "Parque Industrial", "ocupacion_promedio_pct": 52.1, "plazas_ocupadas": 313, "capacidad_total": 600},
        {"zona": "Zona Residencial Norte", "ocupacion_promedio_pct": 41.8, "plazas_ocupadas": 105, "capacidad_total": 250},
    ])

    # 2. Congestión horaria (0 a 23h)
    horas = list(range(24))
    vehiculos = [
        120, 85, 60, 45, 90, 240, 680, 1150, 1420, 980, 850, 920,
        1050, 1120, 960, 890, 1180, 1510, 1680, 1340, 920, 610, 390, 210
    ]
    velocidades = [
        58, 60, 62, 63, 56, 45, 28, 19, 16, 26, 32, 30,
        25, 24, 28, 29, 21, 14, 12, 18, 28, 38, 48, 54
    ]
    q2 = pd.DataFrame({"hora": horas, "volumen_vehicular": vehiculos, "velocidad_kmh": velocidades})

    # 3. Ranking de rutas viales más transitadas
    q3 = pd.DataFrame([
        {"ruta": "Autopista General Cañas", "volumen_diario_estimado": 68400, "velocidad_media": 38.5, "nivel_congestion": "Severo"},
        {"ruta": "Paseo Colón", "volumen_diario_estimado": 45200, "velocidad_media": 21.4, "nivel_congestion": "Alto"},
        {"ruta": "Circunvalación Norte", "volumen_diario_estimado": 41800, "velocidad_media": 32.8, "nivel_congestion": "Medio-Alto"},
        {"ruta": "Avenida Segunda", "volumen_diario_estimado": 38900, "velocidad_media": 16.9, "nivel_congestion": "Severo"},
        {"ruta": "Radial Santa Ana", "volumen_diario_estimado": 26500, "velocidad_media": 44.2, "nivel_congestion": "Moderado"},
    ])

    # 4. Eventos críticos y anomalías detectadas
    q4 = pd.DataFrame([
        {"tipo_evento": "Sobreocupación Crítica (>95%)", "ocurrencias": 342, "porcentaje_del_total": 41.5, "severidad": "Critico"},
        {"tipo_evento": "Colapso de Velocidad (<10 km/h)", "ocurrencias": 288, "porcentaje_del_total": 35.0, "severidad": "Critico"},
        {"tipo_evento": "Pico de Contaminación AQI (>150)", "ocurrencias": 115, "porcentaje_del_total": 13.9, "severidad": "Alto"},
        {"tipo_evento": "Sensor Sin Respuesta / Timeout", "ocurrencias": 79, "porcentaje_del_total": 9.6, "severidad": "Medio"},
    ])

    # 5. Correlación: Velocidad media vs Calidad del Aire (AQI)
    ciudades = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego"]
    q5 = pd.DataFrame([
        {"ciudad": c, "velocidad_media_kmh": v, "aqi_promedio": a, "poblacion_millones": p}
        for c, v, a, p in zip(
            ciudades,
            [30.7, 24.2, 28.5, 36.1, 42.0, 27.8, 38.4, 34.2],
            [113, 142, 98, 125, 85, 108, 92, 88],
            [11.24, 8.95, 5.42, 4.88, 3.12, 4.15, 2.80, 3.25]
        )
    ])

    # 6. Distribución de vehículos comerciales vs particulares
    q6 = pd.DataFrame([
        {"ciudad": "New York", "comerciales_pct": 15.3, "particulares_pct": 84.7},
        {"ciudad": "Los Angeles", "comerciales_pct": 18.7, "particulares_pct": 81.3},
        {"ciudad": "Chicago", "comerciales_pct": 14.2, "particulares_pct": 85.8},
        {"ciudad": "Houston", "comerciales_pct": 22.4, "particulares_pct": 77.6},
        {"ciudad": "Phoenix", "comerciales_pct": 12.9, "particulares_pct": 87.1},
    ])

    # 7. Incidentes y siniestros viales por cuadrante urbano
    q7 = pd.DataFrame([
        {"zona": "Distrito Financiero", "accidentes_anuales": 245, "tasa_por_km": 18.2, "criticidad": "Alta"},
        {"zona": "Centro Histórico", "accidentes_anuales": 198, "tasa_por_km": 15.6, "criticidad": "Alta"},
        {"zona": "Corredor Comercial Este", "accidentes_anuales": 134, "tasa_por_km": 9.8, "criticidad": "Media"},
        {"zona": "Autopista General Cañas", "accidentes_anuales": 182, "tasa_por_km": 12.4, "criticidad": "Alta"},
        {"zona": "Zona Residencial Norte", "accidentes_anuales": 56, "tasa_por_km": 4.1, "criticidad": "Baja"},
    ])

    # 8. Comparativa Capacidad vs Ocupación Máxima por Estacionamiento
    q8 = pd.DataFrame([
        {"parqueo": "Torre Financiera Plaza", "capacidad": 780, "max_ocupacion_registrada": 772, "sobrepasado": False},
        {"parqueo": "Terminal Ferial", "capacidad": 600, "max_ocupacion_registrada": 594, "sobrepasado": False},
        {"parqueo": "Parqueo Central Mercado", "capacidad": 450, "max_ocupacion_registrada": 448, "sobrepasado": False},
        {"parqueo": "Estación del Este", "capacidad": 320, "max_ocupacion_registrada": 319, "sobrepasado": False},
        {"parqueo": "Parque Metropolitano", "capacidad": 250, "max_ocupacion_registrada": 242, "sobrepasado": False},
    ])

    # 9. Tendencia Mensual de Congestión e Índice de Emisiones
    meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Set", "Oct", "Nov", "Dic"]
    q9 = pd.DataFrame({
        "mes": meses,
        "indice_congestion": [65, 68, 74, 70, 78, 82, 80, 84, 88, 91, 89, 94],
        "emisiones_co2_ton": [1240, 1290, 1380, 1310, 1420, 1490, 1450, 1510, 1590, 1640, 1600, 1720]
    })

    # 10. Plazas libres y disponibilidad estimada en tiempo real
    q10 = pd.DataFrame([
        {"cuadrante": "Cuadrante Central A", "plazas_libres": 84, "probabilidad_encontrar_parqueo": "Media (62%)"},
        {"cuadrante": "Cuadrante Financiero B", "plazas_libres": 22, "probabilidad_encontrar_parqueo": "Muy Baja (18%)"},
        {"cuadrante": "Cuadrante Este C", "plazas_libres": 101, "probabilidad_encontrar_parqueo": "Alta (84%)"},
        {"cuadrante": "Cuadrante Norte D", "plazas_libres": 145, "probabilidad_encontrar_parqueo": "Muy Alta (92%)"},
        {"cuadrante": "Cuadrante Industrial E", "plazas_libres": 287, "probabilidad_encontrar_parqueo": "Óptima (98%)"},
    ])

    return {
        "q1_ocupacion_zona": q1,
        "q2_congestion_hora": q2,
        "q3_rutas_ranking": q3,
        "q4_eventos_criticos": q4,
        "q5_velocidad_aqi": q5,
        "q6_vehiculos_tipo": q6,
        "q7_incidentes_zona": q7,
        "q8_capacidad_max": q8,
        "q9_tendencia_mensual": q9,
        "q10_plazas_libres": q10,
    }

def get_mock_hdfs_tree():
    return [
        {"path": "/historico_smartcity/crudo/parking_2025_01.csv", "owner": "hadoop", "size": "42.8 MB", "replication": 3, "modified": "2026-11-17 08:30:15"},
        {"path": "/historico_smartcity/crudo/trafico_multi_city.csv", "owner": "hadoop", "size": "18.4 MB", "replication": 3, "modified": "2026-11-17 08:31:02"},
        {"path": "/historico_smartcity/crudo/telemetria_iot_export.json", "owner": "hadoop", "size": "154.2 MB", "replication": 3, "modified": "2026-11-17 09:12:44"},
        {"path": "/historico_smartcity/depurado/part-00000.parquet", "owner": "spark", "size": "28.1 MB", "replication": 2, "modified": "2026-11-18 01:45:00"},
        {"path": "/historico_smartcity/depurado/part-00001.parquet", "owner": "spark", "size": "27.9 MB", "replication": 2, "modified": "2026-11-18 01:45:05"},
        {"path": "/historico_smartcity/analitica/resumen_zonas.parquet", "owner": "spark", "size": "4.2 MB", "replication": 2, "modified": "2026-11-18 02:10:22"},
        {"path": "/historico_smartcity/analitica/ranking_rutas.parquet", "owner": "spark", "size": "2.8 MB", "replication": 2, "modified": "2026-11-18 02:10:30"},
    ]
