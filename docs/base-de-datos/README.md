# Diseño de base de datos — SmartCity Analytics

## Objetivo

Documentar el diseño de PostgreSQL para SmartCity Analytics,
incluyendo las entidades, relaciones, claves y reglas de integridad
que servirán como base para su implementación.

Este trabajo corresponde a la historia **US-1.01: Diseño del modelo
relacional en tercera forma normal (3FN)**.

## Estado

Los diagramas describen la estructura de los datos. La creación
de tablas, validación de restricciones y carga de datos se realizará
durante la implementación.

## Archivos

| Archivo | Descripción |
|---|---|
| [Modelo conceptual](./SmartCity_Modelo_Conceptual_Chen.pdf) | Entidades, relaciones y reglas del dominio mediante notación Chen. |
| [Modelo relacional editable](./SmartCity_Modelo_Relacional_PostgreSQL.drawio.xml) | Tablas, atributos, tipos de datos, PK, FK y cardinalidades. |
| [Diseño MongoDB](./SmartCity_Diseno_Documental_MongoDB%20(1).pdf) | Colecciones documentales y correspondencia con PostgreSQL. |

El archivo `.drawio` contiene dos pestañas:
1. Modelo relacional.
2. Mapeo y reglas de integridad.

## Función de PostgreSQL

PostgreSQL almacena los catálogos del sistema y las lecturas
estructuradas resultantes del procesamiento de datos.

Los catálogos permiten identificar sensores, ubicaciones, organismos,
fuentes y variables de medición. Las lecturas y sus mediciones permiten
realizar consultas históricas y alimentar los indicadores del proyecto.

MongoDB cuenta con un diseño documental separado para lecturas,
eventos, alertas e incidentes. Ambos motores utilizan identificadores
comunes definidos por el proceso de integración.

## Tablas del modelo

| Tabla | Función |
|---|---|
| categorias_sensor | Agrupa los tipos de sensores. |
| tipos_sensor | Define las clases de sensores existentes. |
| sensores | Registra cada sensor o dispositivo lógico de observación. |
| organismos_responsables | Identifica las organizaciones responsables de los sensores. |
| ciudades | Registra las ciudades incluidas en las fuentes. |
| ubicaciones | Identifica las zonas donde se localizan los sensores. |
| usuarios_sistema | Registra la identificación, nombre y correo de los usuarios. |
| fuentes_datos | Identifica cada fuente y versión del conjunto de datos. |
| variables_medicion | Define las variables, unidades y criterios de agregación. |
| tipos_sensor_variables | Establece qué variables puede medir cada tipo de sensor. |
| lecturas_limpias | Registra la fuente, sensor, fechas y calidad de cada lectura. |
| mediciones_limpias | Almacena el valor de cada variable dentro de una lectura. |
| estacionamientos | Identifica los estacionamientos observados. |
| rutas | Identifica las rutas presentes en los datos de tráfico. |
| niveles_congestion | Define los niveles de congestión utilizados. |
| lecturas_parking | Asocia una lectura de parking con su estacionamiento. |
| lecturas_trafico | Añade el contexto de ruta y nivel de congestión a una lectura. |

## Relaciones principales

- Cada tipo de sensor pertenece a una categoría.
- Cada sensor tiene un tipo y una ubicación.
- Un sensor puede tener un organismo responsable; esta referencia
  puede estar vacía cuando se desconoce.
- Cada ubicación pertenece a una ciudad.
- Cada lectura corresponde a un sensor y a una fuente.
- Una lectura puede contener varias mediciones.
- Cada medición corresponde a una variable.
- Un tipo de sensor puede admitir varias variables, y una variable
  puede ser admitida por varios tipos de sensores.

Las relaciones muchos-a-muchos se representan mediante:

- `tipos_sensor_variables`: clave primaria compuesta por
  `id_tipo_sensor` e `id_variable`.
- `mediciones_limpias`: clave primaria compuesta por
  `id_lectura` e `id_variable`.

## Decisiones de normalización

### Primera forma normal

Los atributos contienen valores individuales. Las mediciones se
almacenan como filas independientes, sin listas de valores dentro
de una columna.

Las coordenadas del modelo conceptual se separan en los atributos
`latitud` y `longitud`.

### Segunda forma normal

En `mediciones_limpias`, el atributo `valor` depende de la combinación
completa de lectura y variable.

Los datos propios de la lectura se mantienen en `lecturas_limpias`;
los datos propios de la variable se mantienen en `variables_medicion`.

### Tercera forma normal

Los atributos descriptivos se almacenan en la tabla del concepto
al que pertenecen.

Por ejemplo, el nombre de una categoría se conserva en
`categorias_sensor`; no se repite en cada sensor. La ciudad de una
ubicación se obtiene mediante su relación con `ciudades`.

Esta organización evita dependencias transitivas y reduce
inconsistencias al modificar los catálogos.

## Reglas de integridad

1. Todas las tablas tienen una clave primaria.

2. Las claves foráneas deben referenciar registros existentes.

3. No puede repetirse una lectura con la misma combinación de
   `id_fuente` y `clave_origen`.

4. Una lectura no puede registrar dos valores para la misma variable.

5. Una variable registrada debe estar permitida para el tipo
   del sensor que produjo la lectura.

6. Una lectura de parking debe tener un contexto en
   `lecturas_parking` y ninguno en `lecturas_trafico`.

7. Una lectura de tráfico debe tener un contexto en
   `lecturas_trafico` y ninguno en `lecturas_parking`.
   La ruta y el nivel de congestión pueden omitirse cuando
   la fuente no los proporciona.

8. Las lecturas de otras clases no utilizan esos dos contextos.

9. Capacidad y ocupación deben ser valores enteros no negativos.
   Cuando ambos están presentes y son válidos, la ocupación
   no puede superar la capacidad.

10. La tasa de ocupación se calcula a partir de ocupación y
    capacidad. No se almacena como un dato independiente.
    El cálculo solo se realiza si la capacidad es mayor que cero.

11. La fecha de medición y la fecha de recepción representan
    momentos distintos y se conservan por separado.

12. No se inventan organismos, rutas ni coordenadas para completar
    información ausente.

Las reglas que comparan varias tablas requieren validación adicional
mediante el proceso de carga y/o mecanismos de la base de datos.
Las claves foráneas por sí solas no garantizan todas estas condiciones.

## Integración con MongoDB

El campo `id_documento_mongo` permite relacionar una lectura
estructurada con su documento de origen.

Esta referencia es de trazabilidad: no constituye una clave foránea
física entre PostgreSQL y MongoDB.

El proceso de integración debe conservar la correspondencia de
identificadores y evitar duplicados cuando se repita una carga.

## Supuestos y pendientes

- Validar el mapeo de los campos contra los CSV definitivos.
- Confirmar unidades, códigos y fechas de cada fuente.
- Se supone que el tipo y la ubicación de un sensor no cambian
  durante el periodo analizado. Si cambian, será necesario
  representar su vigencia histórica.
- Definir los índices según las consultas que se implementarán.
- Verificar las restricciones con datos de prueba.
- Las fuentes de parking y tráfico no cubren por sí solas los
  indicadores ambientales y energéticos del enunciado.

## Criterios de aceptación de US-1.01

- [ ] Modelo conceptual revisado.
- [ ] Modelo relacional alineado con el conceptual.
- [ ] Entidades obligatorias incluidas.
- [ ] Atributos y tipos de datos definidos.
- [ ] Claves primarias y foráneas identificadas.
- [ ] Cardinalidades y campos opcionales definidos.
- [ ] Relaciones muchos-a-muchos resueltas.
- [ ] Justificación de normalización documentada.
- [ ] Reglas de integridad documentadas.
- [ ] Revisión de otro integrante registrada en el pull request.

## Cómo proponer cambios

1. Crear una rama para el cambio.
2. Editar el archivo `.drawio`.
3. Actualizar la documentación y las exportaciones afectadas.
4. Abrir un pull request explicando el motivo del cambio.
5. Solicitar revisión a otro integrante del equipo.
6. Integrar los cambios aprobados.

## Responsable

**Diseño de base de datos y arquitectura:** Allan Prieto Badilla.

**Historia relacionada:** US-1.01.