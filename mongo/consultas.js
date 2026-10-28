// Consultas manuales para mongosh en smartcity_db.

const ciudad = db.getSiblingDB("smartcity_db");

function mostrar(titulo, resultado) {
  print("\n--- " + titulo + " ---");
  printjson(resultado);
}

// 1. Lecturas de un sensor específico
mostrar("Lecturas de un sensor", ciudad.lecturas.find(
  { id_sensor: NumberLong("1") },
  { _id: 1, fecha_medicion: 1 }
).sort({ fecha_medicion: -1 }).limit(5).toArray());

// 2. Lecturas en un rango de fechas
mostrar("Lecturas entre fechas", ciudad.lecturas.find(
  { fecha_medicion: {
    $gte: ISODate("2025-02-01T00:00:00Z"),
    $lt: ISODate("2025-02-08T00:00:00Z")
  } },
  { _id: 1, fecha_medicion: 1 }
).limit(5).toArray());

// 3. Máximos y mínimos por variable
mostrar("Máximo y mínimo por variable", ciudad.lecturas.aggregate([
  { $unwind: "$mediciones" },
  { $group: {
    _id: "$mediciones.codigo",
    minimo: { $min: "$mediciones.valor" },
    maximo: { $max: "$mediciones.valor" }
  } }
]).toArray());

// 4. Eventos críticos
mostrar("Eventos críticos", ciudad.eventos.find(
  { severidad: "critico" },
  { _id: 1, tipo_evento: 1 }
).limit(5).toArray());

// 5. Alertas por zona
mostrar("Alertas por zona", ciudad.alertas.aggregate([
  { $group: { _id: "$contexto.id_ubicacion", cantidad: { $sum: 1 } } },
  { $sort: { cantidad: -1 } },
  { $limit: 5 }
]).toArray());

// 6. Promedio por zona y variable
mostrar("Promedio por zona y variable", ciudad.lecturas.aggregate([
  { $unwind: "$mediciones" },
  { $group: {
    _id: {
      zona: "$contexto.id_ubicacion",
      variable: "$mediciones.codigo"
    },
    promedio: { $avg: "$mediciones.valor" }
  } },
  { $sort: { "_id.zona": 1 } },
  { $limit: 20 }
]).toArray());

// 7. Promedio por tipo de sensor
mostrar("Promedio por tipo de sensor", ciudad.lecturas.aggregate([
  { $unwind: "$mediciones" },
  { $group: {
    _id: {
      tipo: "$contexto.id_tipo_sensor",
      variable: "$mediciones.codigo"
    },
    promedio: { $avg: "$mediciones.valor" }
  } }
]).toArray());

// 8. Incidentes por categoría
mostrar("Incidentes por categoría", ciudad.incidentes.aggregate([
  { $group: { _id: "$categoria", cantidad: { $sum: 1 } } },
  { $sort: { cantidad: -1 } }
]).toArray());

// 9. Lecturas y mediciones por sensor
mostrar("Lecturas y mediciones por sensor", ciudad.lecturas.aggregate([
  { $group: {
    _id: "$id_sensor",
    lecturas: { $sum: 1 },
    mediciones: { $sum: { $size: "$mediciones" } }
  } },
  { $sort: { lecturas: -1 } },
  { $limit: 10 }
]).toArray());

// 10. Filtros múltiples sobre la misma medición
mostrar("Filtros múltiples", ciudad.lecturas.find({
  id_sensor: NumberLong("1"),
  "contexto.id_ubicacion": NumberLong("1"),
  mediciones: {
    $elemMatch: {
      id_variable: NumberLong("2"),
      valor: { $gt: NumberDecimal("50") }
    }
  }
}, { _id: 1, fecha_medicion: 1 }).limit(5).toArray());

// CRUD en una colección temporal de evidencia.
// Se limpian solo documentos marcados por este ejemplo.
const demo = ciudad.getCollection("crud_demo");
demo.deleteMany({ proyecto: "sprint1-evidencia" });

mostrar("insertOne", demo.insertOne({
  _id: "sprint1-demo-1",
  proyecto: "sprint1-evidencia",
  valor: 1,
  activo: true
}));

mostrar("insertMany", demo.insertMany([
  {
    _id: "sprint1-demo-2",
    proyecto: "sprint1-evidencia",
    valor: 2,
    activo: true
  },
  {
    _id: "sprint1-demo-3",
    proyecto: "sprint1-evidencia",
    valor: 3,
    activo: true
  }
]));

mostrar("findOne", demo.findOne({ _id: "sprint1-demo-1" }));
mostrar("find", demo.find({ proyecto: "sprint1-evidencia" }).toArray());

mostrar("updateOne", demo.updateOne(
  { _id: "sprint1-demo-1" },
  { $set: { valor: 10 } }
));

mostrar("updateMany", demo.updateMany(
  { proyecto: "sprint1-evidencia" },
  { $set: { activo: false } }
));

mostrar("deleteOne", demo.deleteOne({ _id: "sprint1-demo-1" }));

// Se dejan los dos documentos restantes para verlos en Mongo Express.
mostrar("Documentos de evidencia restantes", demo.find().toArray());

