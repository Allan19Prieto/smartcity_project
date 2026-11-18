# Interfaz Centralizada de Monitoreo Urbano - SmartCity Analytics

**Instituto Tecnológico de Costa Rica**  
**Escuela de Ingeniería en Computadores**  
**Curso:** CE-3101 Bases de Datos — II Semestre 2026  
**Equipo de Trabajo (RIC):**  
- Rodrigo Arce Bastos (2024115582)  
- Dylan Elizondo Picado (2023086320)  
- Allan Rubén Prieto Badilla (2021032988)  
**Profesor:** Marco Rivera Meneses  

---

## 1. Alcance y Objetivos de la Interfaz

De conformidad con la planificación técnica del Sprint 2 y los requerimientos establecidos en la Etapa 7 (*Publicación e Interfaz*), este componente implementa un panel de control unificado y centralizado orientado a la toma de decisiones basada en datos urbanos. 

El sistema consolida la información proveniente de los cuatro motores principales de la arquitectura:
1. **PostgreSQL:** Persistencia estructurada de catálogos maestros, infraestructura física y entidades relacionales normalizadas bajo Tercera Forma Normal (3NF).
2. **MongoDB:** Repositorio documental de series temporales de telemetría IoT, eventos anómalos y registro histórico de alertas.
3. **Apache Spark:** Motor de computación distribuida responsable del procesamiento analítico masivo de los diez indicadores urbanos obligatorios.
4. **Hadoop HDFS:** Almacenamiento distribuido (Data Lake) para la preservación inmutable del histórico crudo y particiones optimizadas en formato Apache Parquet.

El criterio de finalización estipulado requiere la visualización diferenciada de consultas por tecnología y la trazabilidad demostrable de la procedencia de los cálculos analíticos generados por Apache Spark.

---

## 2. Instrucciones de Despliegue y Ejecución

La aplicación está desarrollada sobre el entorno de Python 3 utilizando la biblioteca Streamlit. Cuenta con una capa de abstracción de datos que permite su operación tanto en clúster activo como en modo de evaluación local independiente.

### Modalidad 1: Ejecución en Entorno Local (Windows / Linux / macOS)

1. Posicionarse en el directorio raíz del proyecto:
   ```bash
   cd c:\Bases\smartcity_project
   ```

2. Instalar los paquetes requeridos especificados en el manifiesto de dependencias:
   ```bash
   pip install -r dashboard/requirements.txt
   ```

3. Iniciar el servidor web de la aplicación:
   ```bash
   streamlit run dashboard/app.py
   ```

4. Acceder al panel de control desde el navegador web en la dirección:
   ```text
   http://localhost:8501
   ```

---

### Modalidad 2: Ejecución en Contenedores Docker

El archivo de orquestación `docker-compose.yml` expone de forma predeterminada el puerto `8501:8501` asociado al servicio `app`.

1. Levantar la infraestructura completa de servicios:
   ```bash
   docker compose up -d
   ```

2. Ejecutar la aplicación dentro del contenedor de aplicación:
   ```bash
   docker compose exec app streamlit run dashboard/app.py --server.address=0.0.0.0 --server.port=8501
   ```

3. Acceder al servicio a través del puerto expuesto en el host:
   ```text
   http://localhost:8501
   ```

---

## 3. Estructura Arquitectónica del Componente

La organización modular del código fuente se distribuye de la siguiente manera:

```text
dashboard/
├── app.py                     # Punto de entrada principal y enrutador de módulos
├── config.py                  # Parámetros de configuración y variables de entorno
├── requirements.txt           # Definición formal de dependencias de software
├── README.md                  # Documentación técnica del componente
├── services/
│   ├── db_service.py          # Servicios de conexión y consulta a los motores
│   └── mock_data.py           # Estructuras de datos de referencia (conmutación)
└── modules/
    ├── overview.py            # Estado de los servicios, KPIs y diagrama de flujo
    ├── postgres_module.py     # Exploración relacional 3NF y consultas SQL
    ├── mongo_module.py        # Telemetría documental IoT y operaciones CRUD
    ├── spark_module.py        # Métricas analíticas masivas y linaje PySpark
    └── hdfs_module.py         # Exploración del Data Lake y particiones Parquet
```

---

## 4. Trazabilidad y Linaje de Datos (Apache Spark y HDFS)

Para satisfacer los requisitos de verificación académica, cada visualización perteneciente al módulo de Apache Spark incorpora metadatos de procedencia técnica (`[SPARK LINEAGE]`):
* **Ruta de origen:** Partición de datos en HDFS (`hdfs://namenode:9000/historico_smartcity/depurado/`).
* **Motor de cálculo:** Transformaciones y acciones ejecutadas mediante la API PySpark DataFrame.
* **Estructura lógica:** Definición del pipeline de agregación disponible en cada sección de análisis para su comprobación técnica.

---

## 5. Integración con los Módulos de Procesamiento Distribuido

Para la fase de unificación con los scripts analíticos desarrollados por los integrantes encargados del procesamiento distribuido:

1. **Persistencia de Resultados en HDFS:** Los trabajos de Spark (`spark-submit`) deberán escribir los DataFrames consolidados en formato Parquet o CSV bajo la ruta `/historico_smartcity/analitica/`.
2. **Consumo Directo:** El servicio `dashboard/services/db_service.py` cuenta con las interfaces requeridas para consumir directamente los conjuntos de datos generados o, alternativamente, leerlos desde las tablas analíticas sincronizadas en PostgreSQL.
