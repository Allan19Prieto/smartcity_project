# Ejecutar la mini demo

La mini demo ilustra conexiones entre las cuatro tecnologías con pocos datos. No es una prueba de volumen.

1. Abrir Docker Desktop.
2. Abrir el proyecto en VS Code y seleccionar Reopen in Container.
3. En una terminal del Dev Container, ejecutar: python demos/mini_demo.py.
4. Revisar la salida de Spark y el directorio HDFS hdfs://namenode:9000/historico_smartcity/resumen_contaminacion.

La demo crea o reutiliza tres sensores en PostgreSQL y reemplaza el contenido de la colección MongoDB telemetria_iot por cinco documentos de ejemplo. Spark calcula promedios por zona y tipo de sensor y escribe el resultado en HDFS. No usar esa colección para datos que se quieran conservar.
