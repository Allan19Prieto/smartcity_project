# Arquitectura del proyecto

## Flujo de la mini demo

El archivo demos/mini_demo.py crea una muestra pequeña: tres sensores en PostgreSQL y cinco lecturas en MongoDB. Spark en modo local cruza ambos conjuntos, calcula promedios y escribe el resultado en HDFS.

    flowchart LR
        A[demos/mini_demo.py: muestra] --> P[(PostgreSQL catalogo_sensores)]
        A --> M[(MongoDB telemetria_iot)]
        P --> S[Spark local: JOIN y promedios]
        M --> S
        S --> H[(HDFS resumen_contaminacion)]

## Función de cada tecnología

- PostgreSQL: catálogos y datos estructurados. El modelo está en base-de-datos/README.md.
- MongoDB: lecturas y datos con estructura flexible. El diseño está en el PDF de esa carpeta.
- Hadoop HDFS: almacenamiento de archivos históricos.
- Spark: combinación y análisis de datos.

## Límite de la demostración

La demo usa local[*], procesa cinco lecturas y no ejecuta un trabajo en un clúster Spark. Docker Compose incluye un Spark Master, pero no un Spark Worker. Por eso ilustra el flujo técnico; no demuestra procesamiento distribuido a escala.
