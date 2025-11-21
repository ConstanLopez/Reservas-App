// Usa el axios que ya tenés configurado con baseURL y token
import api from "./api";

// PARTICIPANTES
export const participantesApi = {
  fetchAll: () => api.get("/admin/participantes/"),
  create: (data) => api.post("/admin/participantes/", data),
  update: (data) => api.put(`/admin/participantes/${data.ci}`, data),
  remove: (row) => api.delete(`/admin/participantes/${row.ci}`),
};

// SALAS
export const salasApi = {
  fetchAll: () => api.get("/admin/salas/"),
  create: (data) => api.post("/admin/salas/", data),
  update: (data) => api.put("/admin/salas/", data),
  // tu backend delete recibe nombre_sala + edificio en el body
  remove: (row) =>
    api.delete("/admin/salas/", {
      data: { nombre_sala: row.nombre_sala, edificio: row.edificio },
    }),
};

// RESERVAS
export const reservasApi = {
  fetchAll: () => api.get("/admin/reservas/"),
  create: (data) => api.post("/admin/reservas", data), // si no usás alta admin, podés no usar esto
  update: (data) => api.put(`/admin/reservas/${data.id_reserva}`, data),
  remove: (row) => api.delete(`/admin/reservas/${row.id_reserva}`),
};

// SANCIONES - Nota: la tabla usa PK compuesta (ci_participante, fecha_inicio, fecha_fin)
// Se guarda el estado original en memoria para poder actualizar/eliminar
let sancionOriginal = null;

// Función auxiliar para formatear fechas
const formatDate = (dateStr) => {
  if (!dateStr) return dateStr;
  // Si ya está en formato YYYY-MM-DD, devolverlo tal cual
  if (typeof dateStr === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
    return dateStr;
  }
  const d = new Date(dateStr);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

export const sancionesApi = {
  fetchAll: () => api.get("/admin/sanciones/"),
  create: (data) => {
    sancionOriginal = null; // Limpiar al crear
    return api.post("/admin/sanciones/", {
      ...data,
      fecha_inicio: formatDate(data.fecha_inicio),
      fecha_fin: formatDate(data.fecha_fin)
    });
  },
  update: (data) => {
    // Para actualizar necesitamos los valores originales de la PK
    // Si no tenemos los valores _old, significa que es la primera vez que editamos
    // y debemos usar los valores actuales como originales
    const payload = {
      ...data,
      ci_participante_old: data.ci_participante_old || sancionOriginal?.ci_participante || data.ci_participante,
      fecha_inicio_old: formatDate(data.fecha_inicio_old || sancionOriginal?.fecha_inicio || data.fecha_inicio),
      fecha_fin_old: formatDate(data.fecha_fin_old || sancionOriginal?.fecha_fin || data.fecha_fin),
      fecha_inicio: formatDate(data.fecha_inicio),
      fecha_fin: formatDate(data.fecha_fin)
    };
    console.log('[SANCIONES UPDATE] sancionOriginal:', sancionOriginal);
    console.log('[SANCIONES UPDATE] data recibida:', data);
    console.log('[SANCIONES UPDATE] payload enviado:', payload);
    sancionOriginal = null; // Limpiar después de usar
    return api.put("/admin/sanciones/", payload);
  },
  remove: (row) => {
    const deleteData = {
      ci_participante: row.ci_participante,
      fecha_inicio: formatDate(row.fecha_inicio),
      fecha_fin: formatDate(row.fecha_fin)
    };
    console.log('[SANCIONES DELETE] row:', row);
    console.log('[SANCIONES DELETE] data enviada:', deleteData);
    return api.delete("/admin/sanciones/", {
      data: deleteData
    });
  },
  // Método especial para guardar los valores originales antes de editar
  setOriginal: (row) => {
    sancionOriginal = {
      ci_participante: row.ci_participante,
      fecha_inicio: row.fecha_inicio,
      fecha_fin: row.fecha_fin
    };
    console.log('[SANCIONES setOriginal] Valores guardados:', sancionOriginal);
  }
};

// TURNOS
export const turnosApi = {
  fetchAll: () => api.get("/admin/turnos/"),
  create: (data) => api.post("/admin/turnos/", data),
  update: (data) => api.put(`/admin/turnos/${data.id_turno}`, data),
  remove: (row) => api.delete(`/admin/turnos/${row.id_turno}`),
};
