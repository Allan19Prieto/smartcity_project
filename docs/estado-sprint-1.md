# Sprint 1: PostgreSQL y MongoDB

## Criterios de la entrega

- PostgreSQL: modelo relacional, tablas, restricciones, índices y consultas requeridas.
- MongoDB: colecciones de lecturas, eventos, alertas e incidentes; operaciones CRUD, consultas, agregaciones e índices.
- Volumen mínimo indicado en el enunciado: 100.000 registros PostgreSQL, 500.000 documentos MongoDB y 1.000.000 de registros procesados con Spark.
- Carga reproducible y evidencia de los resultados.

El [diseño relacional](base-de-datos/README.md) y el [diseño documental](base-de-datos/SmartCity_Diseno_Documental_MongoDB%20(1).pdf) describen los modelos.

## Alcance de la mini demo

La mini demo crea tres sensores de ejemplo en PostgreSQL y cinco documentos en MongoDB. Ejecuta un JOIN con Spark en modo local y escribe un resultado en HDFS. Sirve para ilustrar el flujo entre tecnologías, pero no sustituye las consultas, la carga ni los volúmenes requeridos para Sprint 1.

## Cierre de la entrega

Antes de reportar Sprint 1 como terminado, ejecutar desde cero la creación y carga, comprobar conteos, probar restricciones e índices, ejecutar las consultas obligatorias y guardar resultados verificables en evidencia/sprint1/.
