# 🏙️ SmartCity Analytics - Entorno y Arquitectura de Datos
**CE-3191: Bases de Datos** | Escuela de Ingeniería en Computadores | TEC

---

## 📋 Contenido
1. [Descripción de la Arquitectura](#1-descripción-de-la-arquitectura)
2. [Requisitos del Sistema](#2-requisitos-del-sistema)
3. [¿Por qué este entorno? (¿Por qué no instalar todo directo en Windows?)](#3-por-qué-este-entorno-por-qué-no-instalar-todo-directo-en-windows)
4. [Guía de Instalación Paso a Paso (Windows 11)](#4-guía-de-instalación-paso-a-paso-windows-11)
5. [Matriz de Accesos, URLs y Credenciales](#5-matriz-de-accesos-urls-y-credenciales)
6. [Flujo de Trabajo Diario con Dev Containers](#6-flujo-de-trabajo-diario-con-dev-containers)
7. [Validación con la Mini Demo (demos/mini_demo.py)](#7-validación-con-la-mini-demo-minidemopy)
8. [Problemas Comunes y Soluciones](#8-problemas-comunes-y-soluciones)

---

## 1. Descripción de la Arquitectura

El objetivo del proyecto es simular el ecosistema de datos de una Ciudad Inteligente. Cada una de las 4 tecnologías se eligió para resolver un problema específico del flujo de datos:

* **PostgreSQL (Datos estructurados):** Guarda los datos maestros con integridad referencial (tablas de catálogo de sensores, zonas, distritos y entidades responsables).
* **MongoDB (Datos semiestructurados):** Recibe los eventos y telemetría de sensores IoT en formato JSON (mediciones dinámicas de contaminantes como PM2.5, CO₂, flujo vehicular y alertas).
* **Apache Hadoop HDFS (Almacenamiento distribuido):** Repositorio para guardar históricos masivos y reportes consolidados en archivos planos (CSV/Parquet), asegurando tolerancia a fallos mediante replicación en bloques.
* **Apache Spark (Procesamiento distribuido en memoria):** Realiza el cruce de datos (JOIN entre los datos de Postgres y Mongo), filtrados, promedios por zona y detección de anomalías.
* **Interfaces Gráficas y Streamlit:** Herramientas web para administrar los datos (pgAdmin, Mongo Express) y el dashboard final para presentar los indicadores requeridos.

---

## 2. Requisitos del Sistema

* **Sistema Operativo:** Windows 11 (Home, Pro o Enterprise) con soporte de virtualización habilitado.
* **Procesador:** CPU x86_64 con virtualización por hardware (VT-x o AMD-V).
* **Memoria RAM:** Mínimo 8 GB (16 GB recomendado para correr el clúster con soltura).
* **Almacenamiento:** Mínimo 15-20 GB libres (para imágenes de Docker y volúmenes de datos).

---

## 3. ¿Por qué este entorno? (¿Por qué no instalar todo directo en Windows?)

Antes de ponerse a instalar WSL y Docker, la pregunta obligatoria es: **¿por qué no simplemente descargar los instaladores normales de Postgres, Mongo, Hadoop y Spark en Windows y ahorrarse todo esto?**

La respuesta corta es que hacerlo directo en Windows es una pésima idea para este tipo de proyecto:

1. **Hadoop y Spark en Windows son un dolor de cabeza:** No existen como programas nativos para Windows. Para correr Hadoop en Windows hay que buscar parches de terceros (`winutils.exe`), configurar variables de entorno a mano (`HADOOP_HOME`, `JAVA_HOME`), y lidiar con errores constantes de permisos de carpetas estilo Linux.
2. **Conflictos con versiones de Java:** Spark y Hadoop son muy quisquillosos con la versión de Java (normalmente piden Java 8, 11 o 17). Si ya tienes otra versión de Java instalada en tu máquina para otros cursos o IDEs, te va a desconfigurar el entorno.
3. **Consumo de memoria en segundo plano:** Si instalas PostgreSQL y MongoDB con el instalador de Windows, te van a dejar servicios corriendo en segundo plano que gastan RAM todo el día, incluso cuando no estés tocando este proyecto. Con Docker, todo el clúster se enciende cuando vas a trabajar y se apaga por completo cuando terminas.
4. **Evitar el clásico "en mi compu sí compila":** Si cada uno del grupo instala las cosas por su cuenta en Windows, uno va a tener problemas de versiones, otro de puertos y otro de librerías. Con **Docker + Dev Containers**, todos usamos exactamente la misma versión de Linux, Python, Java y bases de datos con un solo clic.

---

## 4. Guía de Instalación Paso a Paso (Windows 11)

### Paso 1: Habilitar Virtualización y WSL 2
1. Abrir **PowerShell como Administrador** y correr:
   ```powershell
   wsl --install
   ```
2. Reiniciar la computadora cuando lo pida.
3. Al encender, Ubuntu se abrirá solo y te pedirá definir un usuario y contraseña para Linux (guárdalos bien).
4. *Si sale error de virtualización deshabilitada:*
   - Reiniciar la compu y entrar a la BIOS/UEFI (usualmente tecla F2, Supr o F10).
   - En procesadores Intel: habilitar **Intel Virtualization Technology (VT-x)**.
   - En procesadores AMD: habilitar **SVM Mode**.
   - En PowerShell (Administrador), activar las funciones de Windows:
     ```powershell
     dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
     ```
   - Reiniciar de nuevo.

### Paso 2: Instalar y configurar Docker Desktop
1. Descargar e instalar [Docker Desktop](https://www.docker.com/products/docker-desktop/).
2. Asegurarse de que durante la instalación esté marcada la casilla **Use WSL 2 instead of Hyper-V**.
3. Abrir Docker Desktop, entrar a la configuración (**Settings ⚙️**) y verificar:
   - En **General:** que esté activo *Use the WSL 2 based engine*.
   - En **Resources > WSL Integration:** que esté activo el switch principal y la casilla de **Ubuntu**.
   - Darle a *Apply & restart*.
4. Para que Windows reconozca el comando `docker` en cualquier terminal, abrir PowerShell (Administrador) y correr:
   ```powershell
   [Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\Docker\Docker\resources\bin", [EnvironmentVariableTarget]::Machine)
   ```

### Paso 3: Extensiones de VS Code
1. Tener instalado [Visual Studio Code](https://code.visualstudio.com/).
2. En la pestaña de extensiones, instalar **Dev Containers** (de Microsoft).

---

## 5. Matriz de Accesos, URLs y Credenciales

Una vez que Docker está corriendo, todos los paneles están accesibles desde el navegador de Windows:

| Servicio | URL Local | Usuario | Contraseña | Notas de Uso |
| :--- | :--- | :--- | :--- | :--- |
| **🍃 Mongo Express** | [http://localhost:8081](http://localhost:8081) | `admin` | `pass` | Panel visual para explorar colecciones y documentos JSON. |
| **🐘 pgAdmin 4** | [http://localhost:5050](http://localhost:5050) | `admin@smartcity.com` | `password123` | Administrador visual de PostgreSQL. Ver registro abajo. |
| **🐘 Hadoop NameNode** | [http://localhost:9870](http://localhost:9870) | *No requiere* | *No requiere* | Explorador HDFS en *Utilities > Browse the file system*. |
| **⚡ Spark Master UI** | [http://localhost:8080](http://localhost:8080) | *No requiere* | *No requiere* | Monitoreo de memoria, workers y jobs de Spark. |
| **📊 Streamlit Dashboard**| [http://localhost:8501](http://localhost:8501) | *No requiere* | *No requiere* | Dashboard interactivo al correr la aplicación web. |

### Cómo vincular pgAdmin con PostgreSQL (solo se hace una vez):
1. Entrar a [http://localhost:5050](http://localhost:5050) e iniciar sesión con las credenciales de la tabla.
2. En el menú izquierdo, dar clic derecho en **Servers** > **Register** > **Server...**
3. En la pestaña **General**, poner de nombre: `SmartCity`
4. En la pestaña **Connection**, llenar exactamente estos datos:
   * **Host name/address:** `postgres` *(usar la palabra `postgres`, no localhost)*
   * **Port:** `5432`
   * **Maintenance database:** `smartcity_db`
   * **Username:** `admin`
   * **Password:** `password123`
5. Clic en **Save**. Ahora las tablas se pueden explorar en `Databases > smartcity_db > Schemas > public > Tables`.

---

## 6. Flujo de Trabajo Diario con Dev Containers

No hay que instalar Python, Java ni librerías en Windows. El contenedor ya tiene todo preconfigurado:

1. Abrir **Docker Desktop**.
2. Abrir la carpeta del proyecto en **VS Code**.
3. Presionar **`F1`** y seleccionar:  
   👉 **`Dev Containers: Reopen in Container`**
4. VS Code cargará el contenedor. La terminal que se abre dentro ya tiene Python, PySpark, Java 17, `pandas` y las conexiones listas para empezar a programar.

---

## 7. Validación con la Mini Demo (`demos/mini_demo.py`)

Para probar que las 4 tecnologías se comunican bien entre sí, el script de prueba está en la carpeta demos: `demos/mini_demo.py`.

### Ejecución
En la terminal de VS Code (dentro del contenedor):
```bash
python demos/mini_demo.py
```

### ¿Qué hace la prueba?
1. **PostgreSQL:** Crea la tabla de catálogo de sensores y guarda zonas de prueba.
2. **MongoDB:** Inserta un lote de telemetría IoT en JSON con mediciones de contaminantes (`pm25`, `co2`) y alertas.
3. **Apache Spark:** Lee ambas fuentes en memoria, hace un **INNER JOIN** entre el catálogo y la telemetría, y calcula los promedios de contaminación por zona.
4. **Hadoop HDFS:** Spark guarda la tabla resultante como un archivo CSV particionado directamente en HDFS bajo:  
   `hdfs://namenode:9000/historico_smartcity/resumen_contaminacion`

### Verificación del resultado en Hadoop
* **En el navegador:** Entrar a [http://localhost:9870/explorer.html#/historico_smartcity/resumen_contaminacion](http://localhost:9870/explorer.html#/historico_smartcity/resumen_contaminacion) para ver el archivo `part-00000-...csv`.
* **En la terminal:**
  ```bash
  curl -L -s "http://namenode:9870/webhdfs/v1/historico_smartcity/resumen_contaminacion/part-00000*.csv?op=OPEN"
  ```

---

### Sprint 1: PostgreSQL y MongoDB

Desde una terminal del Dev Container, ejecutar: python sprint1.py. La primera ejecucion crea el esquema y carga los datos sinteticos requeridos. Para volver a ejecutar las consultas sin repetir la carga, usar: python sprint1.py --skip-load.

## 8. Problemas Comunes y Soluciones

### 1. `bash: docker: command not found` en la terminal de VS Code
* **Por qué pasa:** Estás corriendo comandos dentro del Dev Container. Los contenedores no tienen acceso al Docker de tu sistema.
* **Solución:** Si necesitas reconstruir el contenedor, presiona `F1` y dale a **`Dev Containers: Rebuild Container`**. Si necesitas correr comandos de Docker en consola, hazlo desde una terminal de PowerShell normal en Windows.

### 2. Error al intentar descargar archivos en la web de Hadoop (`DNS_PROBE_FINISHED_NXDOMAIN`)
* **Por qué pasa:** Cuando das clic en "Download" en la interfaz de Hadoop (`localhost:9870`), el NameNode redirige al navegador al DataNode usando su ID interno de contenedor (tipo `50f04cc86ee6:9864`). Como tu Windows no conoce ese nombre interno de Docker, el navegador da error de DNS.
* **Solución:** El archivo sí está bien guardado. Para leer los datos se hace por medio de Spark, con el comando `curl` indicado arriba, o con la opción *"Head the file"* de la web de Hadoop.

### 3. Mongo Express pide usuario y contraseña
* **Por qué pasa:** Viene con autenticación básica activa por defecto.
* **Solución:** Poner usuario **`admin`** y contraseña **`pass`** *(no poner password123 ahí)*.

### 4. Error de Java al correr PySpark (`JAVA_HOME is not set` o `Java gateway exited`)
* **Por qué pasa:** PySpark ocupa Java para levantar el motor de procesamiento en memoria.
* **Solución:** La configuración de `.devcontainer/devcontainer.json` ya instala Java 17 automáticamente. Si por alguna razón te sale este error, presiona `F1` y dale a **`Dev Containers: Rebuild Container`** para refrescar el entorno.

### 5. pgAdmin no conecta a la base de datos
* **Por qué pasa:** En el campo *Host name/address* se puso `localhost` en lugar de `postgres`.
* **Solución:** Poner siempre **`postgres`**. Como pgAdmin corre dentro de Docker, `postgres` es el nombre con el que se encuentran dentro de la red del clúster.