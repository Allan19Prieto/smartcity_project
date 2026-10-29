# Guía Rápida de Uso y Consultas en MongoDB
**CE-3191: Bases de Datos** | SmartCity Analytics | Sprint 1

Esta guía explica cómo acceder, consultar y entender MongoDB tanto desde la consola oficial (`mongosh`) como desde la interfaz gráfica web (`Mongo Express`).

---

## 1. Acceso a la Consola Interactiva (`mongosh`)

Para abrir la terminal nativa de MongoDB directamente en la base de datos `smartcity_db`, ejecuta desde PowerShell (en la carpeta del proyecto):

```powershell
docker exec -it smartcity-sprint1-mongodb-1 mongosh -u admin -p password123 --authenticationDatabase admin smartcity_db
```

Aparecerá el prompt interactivo:
```text
smartcity_db>
```

Para salir de la consola en cualquier momento, escribe:
```javascript
exit
```

---

## 2. Consultas Rápidas en la Consola

Una vez dentro de `smartcity_db>`, puedes ejecutar consultas directamente:

### A. Búsquedas y Filtros Básicos (`find`)
```javascript
// 1. Ver 3 lecturas recientes del sensor 1
db.lecturas.find({ id_sensor: 1 }, { _id: 1, fecha_medicion: 1 }).sort({ fecha_medicion: -1 }).limit(3);

// 2. Ver eventos críticos detectados
db.eventos.find({ severidad: "critico" }, { _id: 1, tipo_evento: 1, fecha_evento: 1 }).limit(3);

// 3. Contar total de incidentes
db.incidentes.countDocuments();
```

### B. Agregaciones y Métricas (`aggregate`)
```javascript
// 1. Valores máximos y mínimos por variable
db.lecturas.aggregate([
  { $unwind: "$mediciones" },
  { $group: {
      _id: "$mediciones.codigo",
      minimo: { $min: "$mediciones.valor" },
      maximo: { $max: "$mediciones.valor" }
  }}
]);

// 2. Ranking de zonas con más alertas emitidas
db.alertas.aggregate([
  { $group: { _id: "$contexto.id_ubicacion", total_alertas: { $sum: 1 } } },
  { $sort: { total_alertas: -1 } },
  { $limit: 5 }
]);

// 3. Promedio de mediciones por zona
db.lecturas.aggregate([
  { $unwind: "$mediciones" },
  { $group: {
      _id: { zona: "$contexto.id_ubicacion", variable: "$mediciones.codigo" },
      promedio: { $avg: "$mediciones.valor" }
  }},
  { $limit: 5 }
]);
```

---

## 3. Ejecución Automatizada del Script Completo de Consultas

Para ejecutar las 10 consultas analíticas obligatorias y la demostración de CRUD de una sola vez imprimiendo todos los resultados en pantalla:

```powershell
docker exec -it smartcity-sprint1-mongodb-1 mongosh -u admin -p password123 --authenticationDatabase admin smartcity_db --file /scripts/consultas.js
```

---

## 4. Uso de la Interfaz Web (Mongo Express)

- **URL:** [http://localhost:8081](http://localhost:8081)
- **Usuario:** `admin` | **Contraseña:** `pass`
- **Base de datos:** Clic en `smartcity_db`.
- **Colecciones disponibles:** `lecturas`, `eventos`, `alertas`, `incidentes`, `crud_demo`.

### Cómo filtrar visualmente:
1. Entrar a una colección dando clic en **`View`**.
2. Cambiar a la pestaña **`Advanced`**.
3. En el campo **`Query`**, escribir el filtro JSON (ej: `{"id_sensor": 1}` o `{"severidad": "critico"}`).
4. Clic en el botón **`Find`**.

---

## 5. Tabla de Equivalencias: SQL (PostgreSQL) ⇄ MQL (MongoDB)

| Concepto / Operación | PostgreSQL | MongoDB |
| :--- | :--- | :--- |
| **Contenedor de tablas/colecciones** | `DATABASE` | `DATABASE` |
| **Estructura de almacenamiento** | `TABLE` (columnas fijas) | `COLLECTION` (documentos BSON flexibles) |
| **Registro individual** | Fila / Tupla | Documento JSON/BSON |
| **Identificador único** | `PRIMARY KEY` | `_id` |
| **Consultar todo** | `SELECT * FROM lecturas;` | `db.lecturas.find();` |
| **Filtrar por valor** | `WHERE id_sensor = 1` | `{ id_sensor: 1 }` |
| **Ordenar** | `ORDER BY fecha DESC` | `.sort({ fecha: -1 })` |
| **Limitar filas** | `LIMIT 5` o `FETCH FIRST 5 ROWS` | `.limit(5)` |
| **Contar registros** | `SELECT COUNT(*) FROM tabla;` | `db.coleccion.countDocuments();` |
| **Descomponer arrays anidados** | `UNNEST(...)` | `$unwind: "$mediciones"` |
| **Agrupar y promediar** | `GROUP BY zona, AVG(valor)` | `$group: { _id: "$zona", prom: { $avg: "$valor" } }` |
| **Insertar** | `INSERT INTO tabla VALUES (...);` | `db.coleccion.insertOne({ ... });` |
| **Modificar** | `UPDATE tabla SET campo = valor;` | `db.coleccion.updateOne({ filtro }, { $set: { campo: valor } });` |
| **Eliminar** | `DELETE FROM tabla WHERE ...;` | `db.coleccion.deleteOne({ filtro });` |
