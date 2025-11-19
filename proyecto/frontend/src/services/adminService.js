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

// SANCIONES
export const sancionesApi = {
  fetchAll: () => api.get("/admin/sanciones/"),
  create: (data) => api.post("/admin/sanciones", data),
  update: (data) => api.put(`/admin/sanciones/${data.id_sancion}`, data),
  remove: (row) => api.delete(`/admin/sanciones/${row.id_sancion}`),
};
