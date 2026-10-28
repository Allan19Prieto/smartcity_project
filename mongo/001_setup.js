// SmartCity Analytics: crear colecciones, validadores e índices en mongosh.
// Ejecutar contra la base smartcity_db. Repetirlo actualiza validadores e índices.

const dbName = "smartcity_db";
const target = db.getSiblingDB(dbName);

const common = {
  _id: { bsonType: "string", minLength: 1 },
  schema_version: { bsonType: "int", enum: [1] },
  id_fuente: { bsonType: "long", minimum: 1 },
  clave_origen: { bsonType: "string", minLength: 1 },
  naturaleza: { enum: ["real", "sintetica", "no_verificada"] },
  procedencia: { enum: ["original", "derivado", "simulado"] },
  contexto: {
    bsonType: "object",
    required: ["id_ubicacion", "id_ciudad"],
    properties: {
      id_ubicacion: { bsonType: "long", minimum: 1 },
      id_ciudad: { bsonType: "long", minimum: 1 },
      nombre_zona: { bsonType: "string" },
      id_tipo_sensor: { bsonType: "long", minimum: 1 },
      id_categoria: { bsonType: "long", minimum: 1 },
      id_organismo: { bsonType: "long", minimum: 1 },
      id_estacionamiento: { bsonType: "long", minimum: 1 },
      id_ruta: { bsonType: "long", minimum: 1 },
      id_nivel: { bsonType: "long", minimum: 1 },
      geo: {
        bsonType: "object",
        required: ["type", "coordinates"],
        properties: {
          type: { enum: ["Point"] },
          coordinates: { bsonType: "array", items: { bsonType: "double" }, minItems: 2, maxItems: 2 }
        }
      }
    }
  },
  id_sensor: { bsonType: "long", minimum: 1 }
};

function commonProperties(extra) {
  return Object.assign({}, common, extra);
}

function spec(required, properties) {
  return {
    $jsonSchema: {
      bsonType: "object",
      required: required,
      properties: properties,
      additionalProperties: true
    }
  };
}

const definitions = {
  lecturas: spec(
    ["_id", "schema_version", "id_fuente", "clave_origen", "naturaleza", "procedencia", "id_sensor", "tipo", "fecha_medicion", "fecha_recepcion", "contexto", "mediciones", "calidad", "raw", "trazabilidad"],
    commonProperties({
      tipo: { enum: ["parking", "trafico", "otro"] },
      fecha_medicion: { bsonType: "date" },
      fecha_recepcion: { bsonType: "date" },
      intervalo_segundos: { bsonType: "int", minimum: 1 },
      mediciones: {
        bsonType: "array", minItems: 0, maxItems: 64,
        items: {
          bsonType: "object", required: ["id_variable", "codigo", "valor", "unidad"],
          properties: {
            id_variable: { bsonType: "long", minimum: 1 },
            codigo: { bsonType: "string", minLength: 1 },
            valor: { bsonType: "decimal" },
            unidad: { bsonType: "string", minLength: 1 }
          }
        }
      },
      calidad: { enum: ["valida", "parcial", "sin_valores_validos"] },
      errores: { bsonType: "array", items: { bsonType: "object", required: ["campo", "motivo"], properties: { campo: { bsonType: "string" }, motivo: { bsonType: "string" } } } },
      raw: { bsonType: "object" },
      trazabilidad: { bsonType: "object", required: ["archivo", "fila", "version_ingesta"], properties: { archivo: { bsonType: "string" }, fila: { bsonType: ["int", "long"], minimum: 1 }, version_ingesta: { bsonType: "string" } } }
    })
  ),
  eventos: spec(
    ["_id", "schema_version", "id_fuente", "clave_origen", "naturaleza", "procedencia", "id_sensor", "id_lectura", "contexto", "tipo_evento", "fecha_evento", "severidad", "detector", "evidencia"],
    commonProperties({
      id_lectura: { bsonType: "string", minLength: 1 }, tipo_evento: { bsonType: "string", minLength: 1 }, fecha_evento: { bsonType: "date" },
      severidad: { enum: ["informativo", "advertencia", "critico"] },
      detector: { bsonType: "object", required: ["codigo", "version"], properties: { codigo: { bsonType: "string" }, version: { bsonType: "string" } } },
      evidencia: { bsonType: "object" }
    })
  ),
  alertas: spec(
    ["_id", "schema_version", "id_fuente", "clave_origen", "naturaleza", "procedencia", "id_sensor", "id_evento", "contexto", "fecha_emision", "severidad", "estado", "regla", "evidencia"],
    commonProperties({
      id_evento: { bsonType: "string", minLength: 1 }, fecha_emision: { bsonType: "date" }, fecha_cierre: { bsonType: "date" },
      severidad: { enum: ["informativo", "advertencia", "critico"] }, estado: { enum: ["activa", "atendida", "cerrada"] },
      regla: { bsonType: "object", required: ["codigo", "version", "indicador", "operador", "umbral", "unidad"], properties: { codigo: { bsonType: "string" }, version: { bsonType: "string" }, indicador: { bsonType: "string" }, operador: { enum: ["<", "<=", "=", ">=", ">"] }, umbral: { bsonType: "decimal" }, unidad: { bsonType: "string" } } },
      evidencia: { bsonType: "object" }
    })
  ),
  incidentes: spec(
    ["_id", "schema_version", "id_fuente", "clave_origen", "naturaleza", "procedencia", "contexto", "categoria", "descripcion", "fecha_inicio", "fecha_registro", "estado", "detalle"],
    commonProperties({
      id_evento: { bsonType: "string", minLength: 1 }, categoria: { bsonType: "string", minLength: 1 }, descripcion: { bsonType: "string" },
      fecha_inicio: { bsonType: "date" }, fecha_registro: { bsonType: "date" }, fecha_fin: { bsonType: "date" },
      estado: { enum: ["abierto", "en_atencion", "resuelto"] }, detalle: { bsonType: "object" }
    })
  )
};

for (const [name, validator] of Object.entries(definitions)) {
  if (!target.getCollectionNames().includes(name)) {
    target.createCollection(name, { validator: validator, validationLevel: "strict", validationAction: "error" });
  } else {
    target.runCommand({ collMod: name, validator: validator, validationLevel: "strict", validationAction: "error" });
  }
  const collection = target.getCollection(name);
  collection.createIndex({ id_fuente: 1, clave_origen: 1 }, { unique: true, name: "uq_fuente_clave_origen" });
}

target.lecturas.createIndex({ id_sensor: 1, fecha_medicion: -1 }, { name: "ix_sensor_fecha" });
target.lecturas.createIndex({ fecha_medicion: 1 }, { name: "ix_fecha_medicion" });
target.lecturas.createIndex({ "contexto.id_ubicacion": 1, fecha_medicion: 1 }, { name: "ix_ubicacion_fecha" });
target.lecturas.createIndex({ "contexto.id_tipo_sensor": 1, fecha_medicion: 1 }, { name: "ix_tipo_fecha" });
target.lecturas.createIndex({ "mediciones.id_variable": 1, fecha_medicion: 1 }, { name: "ix_variable_fecha" });
target.eventos.createIndex({ severidad: 1, fecha_evento: -1 }, { name: "ix_severidad_fecha" });
target.eventos.createIndex({ id_lectura: 1 }, { name: "ix_evento_lectura" });
target.alertas.createIndex({ "contexto.id_ubicacion": 1, fecha_emision: -1 }, { name: "ix_alerta_zona_fecha" });
target.alertas.createIndex({ id_evento: 1 }, { name: "ix_alerta_evento" });
target.incidentes.createIndex({ categoria: 1, fecha_inicio: -1 }, { name: "ix_categoria_fecha" });
target.incidentes.createIndex({ id_evento: 1 }, { name: "ix_incidente_evento" });

print(`MongoDB listo: ${dbName} (${Object.keys(definitions).join(", ")})`);
