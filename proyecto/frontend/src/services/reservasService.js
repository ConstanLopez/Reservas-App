const API_URL = 'http://localhost:5000/api';

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : ''
  };
};

// ========== RESERVAS ==========
export const getMisReservas = async (incluirCanceladas = false) => {
  const response = await fetch(
    `${API_URL}/reservas/mis-reservas?incluir_canceladas=${incluirCanceladas}`,
    {
      headers: getAuthHeaders()
    }
  );
  return response.json();
};

export const getReservasActivas = async () => {
  const response = await fetch(`${API_URL}/reservas/activas`, {
    headers: getAuthHeaders()
  });
  return response.json();
};

export const getReservaDetalle = async (idReserva) => {
  const response = await fetch(`${API_URL}/reservas/${idReserva}`, {
    headers: getAuthHeaders()
  });
  return response.json();
};

export const crearReserva = async (reservaData) => {
  const response = await fetch(`${API_URL}/reservas`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(reservaData)
  });
  return response.json();
};

export const cancelarReserva = async (idReserva) => {
  const response = await fetch(`${API_URL}/reservas/${idReserva}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  });
  return response.json();
};

// ========== SALAS ==========
export const getSalas = async () => {
  const response = await fetch(`${API_URL}/salas`, {
    headers: getAuthHeaders()
  });
  return response.json();
};

export const getSalasDisponibles = async (fecha, idTurno) => {
  const response = await fetch(
    `${API_URL}/salas/disponibles?fecha=${fecha}&id_turno=${idTurno}`,
    {
      headers: getAuthHeaders()
    }
  );
  return response.json();
};

export const getSalaDetalle = async (nombreSala, edificio) => {
  const response = await fetch(`${API_URL}/salas/${nombreSala}/${edificio}`, {
    headers: getAuthHeaders()
  });
  return response.json();
};

// ========== TURNOS ==========
export const getTurnos = async () => {
  const response = await fetch(`${API_URL}/turnos`, {
    headers: getAuthHeaders()
  });
  return response.json();
};

export const getTurnoDetalle = async (idTurno) => {
  const response = await fetch(`${API_URL}/turnos/${idTurno}`, {
    headers: getAuthHeaders()
  });
  return response.json();
};

export const getTurnosDisponibles = async (fecha, nombreSala, edificio) => {
  const response = await fetch(
    `${API_URL}/turnos/disponibles?fecha=${fecha}&nombre_sala=${nombreSala}&edificio=${edificio}`,
    {
      headers: getAuthHeaders()
    }
  );
  return response.json();
};