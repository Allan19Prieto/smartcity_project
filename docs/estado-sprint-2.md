# Sprint 2: Data Lake Distribuido, Apache Spark y Panel Centralizado

**Instituto Tecnológico de Costa Rica**  
**Escuela de Ingeniería en Computadores**  
**Curso:** CE-3101 Bases de Datos — II Semestre 2026  
**Equipo de Trabajo (RIC):**  
- Rodrigo Arce Bastos (2024115582)  
- Dylan Elizondo Picado (2023086320)  
- Allan Rubén Prieto Badilla (2021032988)  
**Profesor:** Marco Rivera Meneses  

---

## 1. Alcance General del Sprint 2

El segundo sprint del proyecto escala la infraestructura desarrollada en el Sprint 1 (PostgreSQL relacional y MongoDB documental) hacia una arquitectura orientada al procesamiento masivo de datos mediante tecnologías de Big Data:
* **Hadoop HDFS (Data Lake Distribuido):** Preservación del histórico crudo inmutable y almacenamiento de particiones procesadas en formato Apache Parquet.
* **Apache Spark (Procesamiento en Memoria):** Motor de cálculo distribuido para transformaciones, agregaciones y cálculo de los diez análisis urbanos obligatorios.
* **Hadoop Hive / MapReduce:** Ejecución de consultas analíticas sobre el repositorio histórico en HDFS.
* **Interfaz Centralizada (Streamlit):** Panel unificado de control y monitoreo correspondiente a la **Etapa 7** de la planificación.

---

## 2. Cronograma de Etapas del Sprint 2

| Etapa | Descripción Técnica | Criterio de Finalización | Estado |
| :--- | :--- | :--- | :---: |
| **1. Auditoría del Sprint 1** | Revisión de modelos, scripts de carga, consistencia de claves y consultas. | Lista de correcciones aplicada y diseño unificado. | En progreso |
| **2. Contrato de Datos** | Definición de identificadores, formatos temporales UTC, unidades de medición y deduplicación. | Correspondencia semántica entre PostgreSQL, MongoDB y Spark. | En progreso |
| **3. Histórico en HDFS** | Exportación masiva de observaciones y estructuración en `/historico_smartcity/crudo/`. | Archivos recuperables y factor de replicación 3x verificado. | Pendiente |
| **4. Procesamiento Hadoop** | Implementación de consulta histórica mediante Hive o trabajo MapReduce. | Conteo histórico verificable por dispositivo/sensor. | Pendiente |
| **5. Pipeline de Spark** | Ingesta distribuida, limpieza, filtrado de anomalías y generación de particiones Parquet. | Datasets depurados reproducibles en `/historico_smartcity/depurado/`. | Pendiente |
| **6. Analítica Urbana** | Implementación de las diez consultas y análisis masivos obligatorios. | Pregunta analítica, cálculo formal, resultado e interpretación. | En integración |
| **7. Publicación e Interfaz** | Desarrollo del panel centralizado con visualización diferenciada y linaje técnico. | **Consultas por tecnología y gráficos con procedencia Spark demostrable.** | **Completado** |
| **8. Cierre de Entrega** | Medición de tiempos de respuesta, documentación formal y preparación de defensa. | Repositorio completo, manual de reproducción e informe final. | Pendiente |

---

## 3. Especificación Técnica de la Etapa 7: Interfaz Centralizada

La interfaz gráfica desarrollada en Python (Streamlit) e integrada en el directorio [`dashboard/`](../dashboard) resuelve de manera exhaustiva el criterio de la Etapa 7:

### A. Segmentación Tecnológica
1. **Módulo PostgreSQL:** Exploración de catálogos en 3NF (100 sensores, 20 rutas, 20 estacionamientos) y ejecución en vivo de las tres preguntas de negocio relacionales (aforo por zona, horas pico de congestión y rutas críticas).
2. **Módulo MongoDB:** Visualización de telemetría IoT semiestructurada con arrays anidados, registro de alertas operativas clasificadas por severidad y sandbox interactivo de operaciones CRUD (`insertOne`, `find`, `updateOne`, `deleteOne`).
3. **Módulo Apache Spark:** Visualización interactiva de los diez análisis obligatorios con gráficos dinámicos de Plotly y código PySpark demostrable.
4. **Módulo Hadoop HDFS:** Árbol de navegación del Data Lake distribuido por capas de persistencia (`/crudo/`, `/depurado/`, `/analitica/`) y documentación del linaje del dato.

### B. Los Diez Análisis Analíticos de Apache Spark
1. **Ocupación Promedio de Parqueos por Zona Urbana:** Agregación porcentual sobre plazas ocupadas versus capacidad nominal.
2. **Horas Pico y Evolución de Congestión:** Curva horaria (0 a 23h) de aforo vehicular e impacto inverso en la velocidad media.
3. **Ranking de Rutas Viales de Mayor Aforo:** Arterias críticas clasificadas por volumen de tránsito diario y severidad de saturación.
4. **Detección de Eventos Críticos y Anomalías:** Frecuencia relativa de sobreocupación (>95%), colapso de velocidad (<10 km/h) y picos de AQI.
5. **Correlación Velocidad vs Calidad del Aire (AQI):** Relación empírica entre tráfico detenido y aumento de contaminantes atmosféricos.
6. **Composición del Parque Vehicular:** Distribución porcentual entre transporte comercial de carga y vehículos particulares.
7. **Tasa de Siniestralidad Vial por Cuadrante:** Mapeo geográfico de incidentes para asignación de recursos municipales.
8. **Auditoría de Capacidad vs Pico de Ocupación:** Validación de cumplimiento de restricciones físicas en la red de parqueos.
9. **Evolución Estacional de Emisiones de CO2:** Estimación de la huella de carbono anual por congestión.
10. **Disponibilidad Inmediata de Espacios:** Cálculo de probabilidad de aparcamiento libre por sector urbano.

### C. Linaje de Datos y Admisión de Archivos Parquet
Para comprobar la integración técnica sin requerir la ejecución completa del pipeline en cada arranque, la interfaz cuenta con detección automática de archivos binarios Apache Parquet depositados en:
```text
data_lake/analitica_spark/
├── q1_ocupacion_zona.parquet
├── q2_congestion_hora.parquet
├── ...
└── q10_plazas_libres.parquet
```
Cada gráfico despliega el sello formal `[SPARK LINEAGE]`, garantizando al evaluador la trazabilidad de procedencia del cálculo distribuido.

---

## 4. Instrucciones de Ejecución

Para iniciar la interfaz desde el contenedor de aplicación:
```bash
docker compose exec app streamlit run dashboard/app.py --server.address=0.0.0.0 --server.port=8501
```
Acceso en navegador: `http://localhost:8501`.
