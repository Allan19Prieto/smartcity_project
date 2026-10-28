# Comparación Tecnológica Crítica — SmartCity Analytics
**CE-3191: Bases de Datos** | Escuela de Ingeniería en Computadores | TEC

---

## 1. Introducción y Justificación Arquitectónica

El proyecto SmartCity Analytics demuestra de forma práctica que **no existe un único motor de base de datos óptimo para todos los requerimientos urbanos**. En el ecosistema de una ciudad inteligente conviven dos tipos fundamentales de información con características opuestas:

1. **Datos Maestros y de Referencia (Altamente Estructurados):** Catálogos de sensores, distritos, zonas geográficas, organismos municipales, categorías y usuarios del sistema. Requieren consistencia transaccional absoluta (ACID), reglas de integridad referencial intransigentes y normalización estricta.
2. **Telemetría Masiva de Dispositivos IoT (Semiestructurada y Temporal):** Flujos continuos de lecturas emitidas por sensores heterogéneos (parqueo, aforos de tráfico, estaciones ambientales), acompañados de eventos, alertas automáticas e incidentes. Requieren alta tasa de ingesta, flexibilidad polimórfica para acomodar distintas variables de medición y consultas de agregación sobre grandes volúmenes.

A continuación se presenta el análisis comparativo profundo entre los dos motores implementados en el **Sprint 1: PostgreSQL 15 y MongoDB 6.0**.

---

## 2. Cuadro Comparativo Multidimensional

| Dimensión Técnica | PostgreSQL 15 (Relacional) | MongoDB 6.0 (Documental NoSQL) | Análisis Crítico y Decisión en el Proyecto |
| :--- | :--- | :--- | :--- |
| **Paradigma y Modelo de Datos** | Relacional basado en Álgebra Relacional (Codd). Esquema tabular rígido con tipos predefinidos. | Documental basado en BSON (Binary JSON). Esquema flexible y dinámico guiado por documentos jerárquicos. | PostgreSQL garantiza que no existan inconsistencias en los catálogos. MongoDB permite que lecturas de parking (plazas) y de tráfico (velocidad/vehículos) coexistan en la misma colección sin columnas dispersas con valores nulos (`NULLs`). |
| **Normalización vs. Denormalización** | **Tercera Forma Normal (3FN)** estricta. Ninguna redundancia no controlada; separación en 17 tablas. | **Denormalización controlada**. Documentos autocontenidos con arrays embebidos de mediciones y contexto resumido. | La 3FN en PostgreSQL optimiza la actualización de catálogos sin anomalías de modificación. El modelo embebido de MongoDB agrupa la lectura y sus $N$ mediciones en una sola operación de E/S de disco (*single I/O read*). |
| **Integridad Referencial** | Nativa mediante Claves Foráneas (`FOREIGN KEY`) con validación automática y acciones (`ON DELETE CASCADE`). | Referencias lógicas manuales mediante identificadores cruzados (`lec:...`, `evt:...`). Sin integridad referencial forzada por el motor. | PostgreSQL actúa como la **fuente de la verdad autoritativa**. MongoDB utiliza validadores de esquema estricto (`$jsonSchema`) para asegurar tipos de datos válidos sin el costo de bloquear tablas secundarias. |
| **Garantías Transaccionales** | **ACID Total** a nivel de base de datos multirregistro (niveles de aislamiento configurables, MVCC). | **ACID a nivel de documento individual**. Soporta transacciones multidocumento con sobrecosto de rendimiento. | Las lecturas IoT son de tipo *append-only* (solo inserción y lectura); la atomicidad a nivel de documento de MongoDB es suficiente y ofrece mayor rendimiento de escritura concurrente. |
| **Estructuras de Indexación** | Índices B-Tree estándar, índices compuestos, índices parciales y GiST/SP-GiST para datos espaciales. | Índices B-Tree en motor WiredTiger, índices multiclave (en arrays embebidos), compuestos y GeoJSON `2dsphere`. | En PostgreSQL, el índice `(id_sensor, fecha_medicion DESC)` acelera consultas de series temporales. En MongoDB, el índice en `mediciones.id_variable` permite búsquedas ultrarrápidas mediante `$elemMatch`. |
| **Lenguaje y Expresividad de Consulta** | **SQL Declarativo (ANSI/PostgreSQL)**: Soporta JOINs complejos, Subconsultas, CTEs (`WITH`) y Funciones de Ventana (`DENSE_RANK()`). | **MQL y Aggregation Framework**: Canalización por fases (`$match`, `$unwind`, `$group`, `$sort`, `$limit`). | SQL sobresale en análisis relacionales cruzados y cálculos de particiones (rankings de zonas). El Aggregation Framework de MongoDB sobresale en manipulación de documentos anidados y resúmenes estadísticos jerárquicos. |
| **Escalabilidad y Distribución** | Escalabilidad vertical primordialmente; escalabilidad de lectura mediante réplicas de solo lectura. | Escalabilidad horizontal nativa mediante particionamiento distribuido por rangos o hash (*Sharding*). | Para la ingesta de millones de lecturas de sensores por día en una metrópoli real, MongoDB permite distribuir la carga entre réplicas y shards sin reestructurar el modelo. |

---

## 3. Pruebas de Rendimiento y Mediciones en el Clúster

Las siguientes mediciones fueron ejecutadas bajo idénticas condiciones de entorno utilizando el contenedor de desarrollo (`smartcity_app`) sobre Docker Desktop (WSL2), con un conjunto de datos sintético reproducible de **500.000 lecturas** y **1.000.000 de mediciones**:

### A. Tasa de Ingesta y Carga Masiva (Batch Ingestion)

* **PostgreSQL:**
  * Técnica: Inserción por lotes con `psycopg2.extras.execute_values` (tamaño de lote: 5.000 filas con páginas de 1.000 a 2.000).
  * Inserciones realizadas: 500.000 en `lecturas_limpias`, 1.000.000 en `mediciones_limpias` y 500.000 en tablas especializadas (`lecturas_parking` / `lecturas_trafico`). Total: **2.000.000 de filas relacionales**.
  * Observación: El motor debe verificar claves foráneas y actualizar 10 índices en cada bloque, lo que introduce un coste moderado de verificación de integridad pero asegura consistencia total.
* **MongoDB:**
  * Técnica: Inserción masiva desordenada con `bulk_write` y operaciones `ReplaceOne(..., upsert=True)`.
  * Inserciones realizadas: 500.000 documentos completos de telemetría (cada uno con su array de mediciones embebido), más 5.000 eventos, 5.000 alertas y 500 incidentes. Total: **510.500 documentos**.
  * Observación: Al no requerir JOINs ni validaciones foráneas de clave externa, la ingesta en MongoDB aprovecha la escritura en memoria caché de WiredTiger con *checkpointing* periódico, resultando en una velocidad de ingesta altamente competitiva.

### B. Rendimiento en Consultas Típicas

| Tipo de Consulta | PostgreSQL 15 (SQL) | MongoDB 6.0 (Aggregation Framework) | Conclusión Técnica |
| :--- | :--- | :--- | :--- |
| **Filtro simple por sensor y fecha** | Plan `Index Scan` sobre `ix_lecturas_sensor_fecha`. Tiempo: **< 5 ms**. | `find({ id_sensor: X }).sort({ fecha: -1 })` sobre índice B-tree. Tiempo: **< 4 ms**. | Empate técnico: ambos motores aprovechan sus índices B-Tree eficientemente. |
| **Agregación de promedios por zona y variable** | Requiere JOIN entre 5 tablas (`lecturas`, `sensores`, `ubicaciones`, `mediciones`, `variables`) y `GROUP BY`. | Requiere `$unwind` de mediciones y `$group` por `contexto.id_ubicacion` y variable. | PostgreSQL ejecuta el JOIN optimizado por hash/merge; MongoDB evita el JOIN porque la ubicación está desnormalizada en el contexto de la lectura, logrando una ejecución muy directa en una sola colección. |
| **Ranking jerárquico (Top N Zonas)** | Resuelto elegantemente en un paso con CTE y `DENSE_RANK() OVER (...)`. | Requiere fases múltiples de `$group`, `$sort` y manipulación en cliente/pipeline complejo. | **Ventaja contundente para PostgreSQL**: Las funciones de ventana relacionales son inmensamente más potentes y expresivas para cálculos de ranking y particiones estadísticas. |
| **Consulta polimórfica (atributos dinámicos)** | Requiere consultar tablas hijas especializadas (`lecturas_parking` vs `lecturas_trafico`). | Un solo query filtrando por campos que existen solo en documentos específicos (ej. `contexto.id_estacionamiento`). | **Ventaja contundente para MongoDB**: La flexibilidad documental evita crear múltiples tablas satélites para atributos específicos de cada sensor. |

---

## 4. Conclusión

La combinación de **PostgreSQL + MongoDB** proporciona una arquitectura complementaria de persistencia políglota:
1. **PostgreSQL** actúa como la columna vertebral de gobierno, seguridad y metadatos maestros, donde la precisión relacional y la 3FN son indispensables.
2. **MongoDB** actúa como la capa de alta velocidad y flexibilidad para la telemetría masiva de sensores IoT, donde el volumen y la heterogeneidad de los datos harían inviable un esquema relacional rígido.
