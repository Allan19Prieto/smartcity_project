// Consultas manuales para ejecutar con mongosh en smartcity_db.
const ciudad = db.getSiblingDB("smartcity_db");

// Lecturas de un sensor y rango de fechas
ciudad.lecturas.find({ id_sensor: NumberLong(1) }).sort({ fecha_medicion: -1 }).limit(5).toArray();
ciudad.lecturas.find({ fecha_medicion: { $gte: ISODate("2025-02-01T00:00:00Z"), $lt: ISODate("2025-02-08T00:00:00Z") } }).limit(5).toArray();

// Máximos y mínimos por variable
ciudad.lecturas.aggregate([
  { $unwind: "$mediciones" },
  { $group: { _id: "$mediciones.codigo", minimo: { $min: "$mediciones.valor" }, maximo: { $max: "$mediciones.valor" } } }
]).toArray();

// Eventos críticos y alertas por zona
ciudad.eventos.find({ severidad: "critico" }).limit(5).toArray();
ciudad.alertas.aggregate([
  { $group: { _id: "$contexto.id_ubicacion", cantidad: { $sum: 1 } } },
  { $sort: { cantidad: -1 } }
]).toArray();

// Promedio por zona y variable
ciudad.lecturas.aggregate([
  { $unwind: "$mediciones" },
  { $group: { _id: { zona: "$contexto.id_ubicacion", variable: "$mediciones.codigo" }, promedio: { $avg: "$mediciones.valor" } } },
  { $sort: { "_id.zona": 1 } }, { $limit: 20 }
]).toArray();

// Promedio por tipo de sensor y variable
ciudad.lecturas.aggregate([
  { $unwind: "$mediciones" },
  { $group: { _id: { tipo: "$contexto.id_tipo_sensor", variable: "$mediciones.codigo" }, promedio: { $avg: "$mediciones.valor" } } }
]).toArray();

// Incidentes por categoría; cantidad de lecturas y mediciones por sensor
ciudad.incidentes.aggregate([{ $group: { _id: "$categoria", cantidad: { $sum: 1 } } }]).toArray();
ciudad.lecturas.aggregate([
  { $group: { _id: "$id_sensor", lecturas: { $sum: 1 }, mediciones: { $sum: { $size: "$mediciones" } } } },
  { $sort: { lecturas: -1 } }, { $limit: 10 }
]).toArray();

// Filtros múltiples sobre la misma medición
ciudad.lecturas.find({
  id_sensor: NumberLong(1),
  "contexto.id_ubicacion": NumberLong(1),
  "mediciones": { $elemMatch: { id_variable: NumberLong(2), valor: { $gt: NumberDecimal("50") } } }
}).limit(5).toArray();
