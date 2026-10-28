# Fuentes y datos

## Fuentes propuestas por el equipo

Estas fuentes aparecen en la planificación compartida del proyecto:

| Fuente | Dataset propuesto | Uso | Estado aquí |
|---|---|---|---|
| [CityPulse](http://iot.ee.surrey.ac.uk:8080/datasets.html) | Pollution y weather | Variables ambientales | No hay archivos descargados ni carga registrada. |
| [IoTDataset](https://iotdataset.com/topic/smart-city) | Smart Urban Sensor Network Data; incluye parking Birmingham y tráfico urbano multi-ciudad | Movilidad | No hay archivos descargados ni carga registrada. |
| [Kaggle](https://www.kaggle.com/datasets/datasetengineer/isone-smart-city-energy-dataset) | ISONE Smart City Energy Dataset | Energía | Propuesto; falta confirmar archivo, licencia y carga. |
| [Kaggle](https://www.kaggle.com/datasets/rednivrug/unisys) | Dataset de transporte público indicado en la planificación | Transporte | Propuesto; falta confirmar archivo, licencia y carga. |

La planificación del equipo atribuye licencias a algunos datasets, pero deben verificarse en la página y archivo exactos que se descarguen. No afirmar que una fuente se integró hasta tener el archivo y el proceso de carga documentados.

## Datos que usa la mini demo

La mini demo contiene tres sensores y cinco lecturas de ejemplo escritos directamente en mini_demo.py. Son datos de prueba pequeños; no provienen de los datasets anteriores.

## Contrato común pendiente

Antes de integrar fuentes reales, completar y acordar:

- identificador estable de sensor y de registro de origen;
- zona y ciudad;
- fecha y zona horaria;
- nombre de variable y unidad;
- tratamiento de valores faltantes y duplicados;
- relación entre cada lectura de MongoDB y su registro estructurado en PostgreSQL.
