import { useState, useEffect } from 'react';
import { getMisReservas, cancelarReserva } from '../services/reservasService';

export default function MisReservas() {
  const [reservas, setReservas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [incluirCanceladas, setIncluirCanceladas] = useState(false);
  const [filtro, setFiltro] = useState('todas'); // 'todas', 'activas', 'pasadas'

  useEffect(() => {
    cargarReservas();
  }, [incluirCanceladas]);

  const cargarReservas = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getMisReservas(incluirCanceladas);
      
      if (response.success) {
        setReservas(response.data);
      } else {
        setError(response.message || 'Error al cargar las reservas');
      }
    } catch (err) {
      setError('Error de conexión con el servidor');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelar = async (idReserva) => {
    if (!window.confirm('¿Estás seguro de que deseas cancelar esta reserva?')) {
      return;
    }

    try {
      const response = await cancelarReserva(idReserva);
      
      if (response.success) {
        alert('Reserva cancelada exitosamente');
        cargarReservas(); // Recargar lista
      } else {
        alert(response.message || 'Error al cancelar la reserva');
      }
    } catch (err) {
      alert('Error de conexión con el servidor');
      console.error(err);
    }
  };

  const getEstadoBadge = (estado) => {
    const badges = {
      'activa': 'badge bg-success',
      'cancelada': 'badge bg-secondary',
      'sin asistencia': 'badge bg-warning text-dark',
      'finalizada': 'badge bg-info'
    };
    return badges[estado] || 'badge bg-secondary';
  };

  const getTipoSalaBadge = (tipo) => {
    const badges = {
      'libre': 'badge bg-primary',
      'docente': 'badge bg-danger',
      'posgrado': 'badge bg-warning text-dark'
    };
    return badges[tipo] || 'badge bg-secondary';
  };

  const reservasFiltradas = reservas.filter(reserva => {
    const hoy = new Date().toISOString().split('T')[0];
    const fechaReserva = reserva.fecha;

    if (filtro === 'activas') {
      return reserva.estado === 'activa' && fechaReserva >= hoy;
    } else if (filtro === 'pasadas') {
      return fechaReserva < hoy;
    }
    return true; // 'todas'
  });

  if (loading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border" style={{color: '#E6F0FA'}} role="status">
          <span className="visually-hidden">Cargando...</span>
        </div>
        <p className="mt-3" style={{color: '#E6F0FA'}}>Cargando reservas...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        <h5 className="alert-heading">Error</h5>
        <p>{error}</p>
        <button className="btn btn-sm btn-outline-danger" onClick={cargarReservas}>
          Reintentar
        </button>
      </div>
    );
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 style={{color: '#E6F0FA'}}>Mis Reservas</h2>
        <button className="btn btn-sm" style={{backgroundColor: '#0056A6', color: '#E6F0FA', borderColor: '#E6F0FA'}} onClick={cargarReservas}>
          🔄 Actualizar
        </button>
      </div>

      {/* Filtros */}
      <div className="card mb-4" style={{backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid #0056A6'}}>
        <div className="card-body">
          <div className="row align-items-center">
            <div className="col-md-6">
              <div className="btn-group" role="group">
                <button
                  className="btn"
                  style={filtro === 'todas' ? {backgroundColor: '#0056A6', color: '#E6F0FA', borderColor: '#003366'} : {backgroundColor: 'transparent', color: '#0056A6', borderColor: '#0056A6'}}
                  onClick={() => setFiltro('todas')}
                >
                  Todas
                </button>
                <button
                  className="btn"
                  style={filtro === 'activas' ? {backgroundColor: '#0056A6', color: '#E6F0FA', borderColor: '#003366'} : {backgroundColor: 'transparent', color: '#0056A6', borderColor: '#0056A6'}}
                  onClick={() => setFiltro('activas')}
                >
                  Activas
                </button>
                <button
                  className="btn"
                  style={filtro === 'pasadas' ? {backgroundColor: '#0056A6', color: '#E6F0FA', borderColor: '#003366'} : {backgroundColor: 'transparent', color: '#0056A6', borderColor: '#0056A6'}}
                  onClick={() => setFiltro('pasadas')}
                >
                  Pasadas
                </button>
              </div>
            </div>
            <div className="col-md-6 text-md-end mt-3 mt-md-0">
              <div className="form-check form-switch d-inline-block">
                <input
                  className="form-check-input"
                  type="checkbox"
                  id="incluirCanceladas"
                  checked={incluirCanceladas}
                  onChange={(e) => setIncluirCanceladas(e.target.checked)}
                />
                <label className="form-check-label" htmlFor="incluirCanceladas" style={{color: '#003366'}}>
                  Incluir canceladas
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Lista de Reservas */}
      {reservasFiltradas.length === 0 ? (
        <div className="alert alert-info text-center">
          <h5>No hay reservas para mostrar</h5>
          <p className="mb-0">Intenta cambiar los filtros o crea una nueva reserva</p>
        </div>
      ) : (
        <div className="row g-4">
          {reservasFiltradas.map((reserva) => (
            <div key={reserva.id_reserva} className="col-md-6 col-lg-4">
              <div className="card h-100 shadow-sm">
                <div className="card-header bg-white">
                  <div className="d-flex justify-content-between align-items-start">
                    <h5 className="card-title mb-0">
                      {reserva.nombre_sala}
                    </h5>
                    <span className={getEstadoBadge(reserva.estado)}>
                      {reserva.estado}
                    </span>
                  </div>
                  <small className="text-muted">{reserva.edificio}</small>
                </div>
                <div className="card-body">
                  <div className="mb-2">
                    <strong>📅 Fecha:</strong> {new Date(reserva.fecha + 'T00:00:00').toLocaleDateString('es-ES')}
                  </div>
                  <div className="mb-2">
                    <strong>🕐 Horario:</strong> {reserva.hora_inicio} - {reserva.hora_fin}
                  </div>
                  <div className="mb-2">
                    <strong>👥 Capacidad:</strong> {reserva.capacidad} personas
                  </div>
                  <div className="mb-2">
                    <strong>🏢 Tipo:</strong>{' '}
                    <span className={getTipoSalaBadge(reserva.tipo_sala)}>
                      {reserva.tipo_sala}
                    </span>
                  </div>
                  <div>
                    <strong>📍 Ubicación:</strong>
                    <div className="text-muted small">
                      {reserva.direccion}, {reserva.departamento}
                    </div>
                  </div>
                </div>
                {reserva.estado === 'activa' && reserva.fecha >= new Date().toISOString().split('T')[0] && (
                  <div className="card-footer bg-white">
                    <button
                      className="btn btn-sm btn-danger w-100"
                      onClick={() => handleCancelar(reserva.id_reserva)}
                    >
                      ❌ Cancelar Reserva
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Resumen */}
      <div className="card mt-4" style={{backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid #0056A6'}}>
        <div className="card-body">
          <strong style={{color: '#003366'}}>Total de reservas mostradas:</strong> <span style={{color: '#003366'}}>{reservasFiltradas.length}</span>
        </div>
      </div>
    </div>
  );
}