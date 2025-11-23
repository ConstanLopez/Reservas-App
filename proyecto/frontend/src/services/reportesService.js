import api from './api';

export const reportesService = {
  getSalasMasReservadas: () => api.get('/reportes/salas-mas-reservadas'),
  getTurnosMasDemandados: () => api.get('/reportes/turnos-mas-demandados'),
  getPromedioParticipantes: () => api.get('/reportes/promedio-participantes'),
  getReservasPorCarrera: () => api.get('/reportes/reservas-por-carrera'),
  getOcupacionPorEdificio: () => api.get('/reportes/ocupacion-por-edificio'),
  getReservasPorRol: () => api.get('/reportes/reservas-por-rol'),
  getSancionesPorRol: () => api.get('/reportes/sanciones-por-rol'),
  getEfectividadReservas: () => api.get('/reportes/efectividad-reservas'),
  getHorariosPico: () => api.get('/reportes/horarios-pico'),
  getTendenciaMensual: () => api.get('/reportes/tendencia-mensual'),
  getUsuariosActivos: () => api.get('/reportes/usuarios-activos'),
};