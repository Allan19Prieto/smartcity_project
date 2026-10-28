# Documento de Atributos del Graduado — SmartCity Analytics
**CE-3191: Bases de Datos** | Escuela de Ingeniería en Computadores | TEC

---

## 1. Análisis Financiero (AF)

> *Aplica el conocimiento y la comprensión de los principios de gestión de ingeniería y la toma de decisiones económicas y los aplica al propio trabajo, como miembro y líder de un equipo, y para gestionar proyectos en entornos multidisciplinarios.*

### 1. Aplicación del atributo en la solución del proyecto
Durante la arquitectura y ejecución del proyecto, el equipo evaluó rigurosamente los costos directos e indirectos asociados al ciclo de vida del dato urbano. En lugar de desplegar instancias dispersas o recurrir a infraestructura cloud con costos recurrentes de procesamiento y transferencia de red (egress fees), se tomó la decisión económica de orquestar un clúster local contenedorizado mediante **Docker Compose y Dev Containers**. Esto redujo a cero los costos monetarios de infraestructura durante el desarrollo y pruebas. 

Asimismo, desde la perspectiva del modelado de datos, la decisión de normalizar los datos maestros en **Tercera Forma Normal (3FN)** dentro de PostgreSQL minimizó la redundancia y el consumo de almacenamiento en disco para entidades estáticas, mientras que la separación de la telemetría masiva semiestructurada hacia **MongoDB** evitó costosas operaciones de alteración de esquemas relacionales (*schema migrations*). La implementación de índices selectivos (B-Tree en PostgreSQL e índices compuestos en MongoDB) optimizó el costo computacional de las consultas analíticas complejas, logrando tiempos de respuesta de milisegundos sin requerir escalamiento vertical de hardware.

### 2. Impacto del proyecto en la sociedad
A nivel municipal y social, un sistema analítico de ciudad inteligente optimizado financieramente permite a los gobiernos locales maximizar el rendimiento de los fondos públicos. Al consolidar datos de transporte, flujo vehicular, parqueo y monitoreo ambiental bajo una arquitectura híbrida de bajo costo operativo (OPEX), las municipalidades pueden planificar el mantenimiento preventivo de vías, reducir los tiempos de viaje de los ciudadanos y mitigar la congestión y emisión de contaminantes sin incurrir en licencias privativas prohibitivas de software. Esto democratiza la adopción de tecnologías de Smart Cities en municipalidades con recursos presupuestarios limitados.

### 3. Retroalimentación obtenida gracias al proyecto
El proyecto evidenció que las decisiones puramente técnicas de modelado y arquitectura de datos tienen consecuencias financieras inmediatas. Aprendimos que un esquema relacional no optimizado o consultas que ejecuten escaneos secuenciales completos (*Full Table Scans*) sobre millones de registros elevan drásticamente el consumo de CPU y memoria, lo cual en un entorno de producción o en la nube se traduce directamente en sobrecostos de facturación. En futuras iteraciones, evaluaríamos desde el inicio métricas de costo por millón de lecturas procesadas para definir umbrales de particionamiento de datos y políticas de retención histórica (*data tiering*).

---

## 2. Aprendizaje Continuo (AC - Nivel Medio)

> *Capacidad para ejecutar estrategias con el fin de resolver sus necesidades educativas o de aprendizaje, de acuerdo con los objetivos o las intenciones de aprendizaje.*

### 1. Aplicación del atributo en la solución del proyecto
Dado que los contenidos de clase se enfocaron primordialmente en el paradigma relacional y lenguaje SQL tradicional, el desarrollo de la solución requirió una estrategia autónoma y autodirigida de aprendizaje continuo para asimilar el paradigma NoSQL y el motor documental MongoDB. El equipo debió investigar e internalizar conceptos no cubiertos en las clases magistrales: la sintaxis de validación de esquemas mediante `$jsonSchema` (BSON Types, validación estricta y control de acciones), la indexación multiclave y geoespacial, y particularmente el diseño y depuración de canalizaciones avanzadas en el **Aggregation Framework** (`$match`, `$unwind`, `$group`, proyecciones y cálculo de métricas polimórficas).

Para lograrlo, se establecieron ciclos de autoaprendizaje estructurados: consulta de documentación oficial de MongoDB 6.0, análisis de libros de referencia y especificaciones de diseño documental, formulación de pruebas aisladas en entornos de desarrollo y validación cruzada entre los compañeros de equipo para asegurar que el pipeline de datos sintéticos de 500.000 documentos cumpliera con los estándares de rendimiento esperados.

### 2. Impacto del proyecto en la sociedad
En un entorno tecnológico caracterizado por la constante obsolescencia y la proliferación de tecnologías Big Data y ciudades inteligentes, los profesionales de computación deben poseer la capacidad de aprender e integrar tecnologías emergentes de manera rápida y fundamentada. Esta adaptabilidad impacta directamente a la sociedad al asegurar que los futuros proyectos de infraestructura digital del país sean diseñados por ingenieros versátiles, capaces de evaluar objetivamente los méritos técnicos de cada herramienta y de implementar soluciones robustas y escalables ante problemas no estructurados del mundo real.

### 3. Retroalimentación obtenida gracias al proyecto
La principal lección del proceso de autoaprendizaje fue comprender que las tecnologías NoSQL no sustituyen a las bases de datos relacionales, sino que se complementan en arquitecturas de persistencia políglota (*Polyglot Persistence*). Inicialmente existía la noción preconcebida de que MongoDB era únicamente un repositorio "sin esquema" para almacenar JSONs arbitrarios; sin embargo, el estudio autónomo demostró la importancia crítica de aplicar contratos documentales rigurosos, validadores formales y patrones de diseño para no degradar la integridad analítica. Como oportunidad de mejora identificada, reconocemos el beneficio de generar matrices de prototipado rápido desde las etapas tempranas de un proyecto para acelerar la curva de aprendizaje del equipo.
