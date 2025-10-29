import { useState, useEffect } from 'react';
import { getTurnos, getSalasDisponibles, crearReserva } from '../services/reservasService';

export default function CrearReserva({ onReservaCreada }) {
  const [paso, setPaso] = useState(1); // 1: Fecha y turno, 2: Seleccionar sala, 3: Confirmar
  const [turnos, setTurnos] = useState([]);
  const [salasDisponibles, setSalasDisponibles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Datos del formulario
  const [fecha, setFecha] = useState('');
  const [turnoSeleccionado, setTurnoSeleccionado] = useState(null);
  const [salaSeleccionada, setSalaSeleccionada] = useState(null);

  useEffect(() => {
    cargarTurnos();
  }, []);

  const cargarTurnos = async () => {
    try {
      const response = await getTurnos();
      if (response.success) {
        setTurnos(response.data);
      }
    } catch (err) {
      console.error('Error cargando turnos:', err);
    }
  };

  const buscarSalasDisponibles = async () => {
    if (!fecha || !turnoSeleccionado) {
      setError('Debes seleccionar una fecha y un turno');
      return;
    }

    // Validar que la fecha no sea pasada
    const hoy = new Date().toISOString().split('T')[0];
    if (fecha < hoy) {
      setError('No puedes reservar para fechas pasadas');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await getSalasDisponibles(fecha, turnoSeleccionado.id_turno);
      
      if (response.success) {
        setSalasDisponibles(response.data);
        if (response.data.length === 0) {
          setError('No hay salas disponibles para esta fecha y turno');
        } else {
          setPaso(2);
        }
      } else {
        setError(response.message || 'Error al buscar salas disponibles');
      }
    } catch (err) {
      setError('Error de conexión con el servidor');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const confirmarReserva = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const reservaData = {
        nombre_sala: salaSeleccionada.nombre_sala,
        edificio: salaSeleccionada.edificio,
        fecha: fecha,
        id_turno: turnoSeleccionado.id_turno
      };

      const response = await crearReserva(reservaData);
      
      if (response.success) {
        alert('¡Reserva creada exitosamente!');
        // Reiniciar formulario
        setPaso(1);
        setFecha('');
        setTurnoSeleccionado(null);
        setSalaSeleccionada(null);
        setSalasDisponibles([]);
        
        if (onReservaCreada) {
          onReservaCreada();
        }
      } else {
        setError(response.message || 'Error al crear la reserva');
      }
    } catch (err) {
      setError('Error de conexión con el servidor');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getTipoSalaBadge = (tipo) => {
    const badges = {
      'libre': 'badge bg-primary',
      'docente': 'badge bg-danger',
      'posgrado': 'badge bg-warning text-dark'
    };
    return badges[tipo] || 'badge bg-secondary';
  };

  const renderPaso1 = () => (
    <div className="card">
      <div className="card-header bg-primary text-white">
        <h5 className="mb-0">Paso 1: Selecciona fecha y turno</h5>
      </div>
      <div className="card-body">
        {error && (
          <div className="alert alert-danger alert-dismissible fade show" role="alert">
            {error}
            <button type="button" className="btn-close" onClick={() => setError(null)}></button>
          </div>
        )}

        <div className="mb-4">
          <label htmlFor="fecha" className="form-label fw-bold">
            📅 Fecha de la reserva
          </label>
          <input
            type="date"
            className="form-control"
            id="fecha"
            value={fecha}
            onChange={(e) => setFecha(e.target.value)}
            min={new Date().toISOString().split('T')[0]}
          />
        </div>

        <div className="mb-4">
          <label className="form-label fw-bold">🕐 Turno</label>
          <div className="row g-3">
            {turnos.map((turno) => (
              <div key={turno.id_turno} className="col-md-6">
                <div
                  className={`card cursor-pointer ${turnoSeleccionado?.id_turno === turno.id_turno ? 'border-primary border-2 bg-light' : ''}`}
                  onClick={() => setTurnoSeleccionado(turno)}
                  style={{ cursor: 'pointer' }}
                >
                  <div className="card-body text-center">
                    <h6 className="mb-1">{turno.hora_inicio} - {turno.hora_fin}</h6>
                    {turnoSeleccionado?.id_turno === turno.id_turno && (
                      <small className="text-primary">✓ Seleccionado</small>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <button
          className="btn btn-primary btn-lg w-100"
          onClick={buscarSalasDisponibles}
          disabled={!fecha || !turnoSeleccionado || loading}
        >
          {loading ? (
            <>
              <span className="spinner-border spinner-border-sm me-2" role="status"></span>
              Buscando...
            </>
          ) : (
            'Buscar salas disponibles →'
          )}
        </button>
      </div>
    </div>
  );

  const renderPaso2 = () => (
    <div className="card">
      <div className="card-header bg-primary text-white">
        <h5 className="mb-0">Paso 2: Selecciona una sala</h5>
        <small>Fecha: {new Date(fecha + 'T00:00:00').toLocaleDateString('es-ES')} | Turno: {turnoSeleccionado.hora_inicio} - {turnoSeleccionado.hora_fin}</small>
      </div>
      <div className="card-body">
        {error && (
          <div className="alert alert-danger alert-dismissible fade show" role="alert">
            {error}
            <button type="button" className="btn-close" onClick={() => setError(null)}></button>
          </div>
        )}

        <div className="row g-4 mb-4">
          {salasDisponibles.map((sala) => (
            <div key={`${sala.nombre_sala}-${sala.edificio}`} className="col-md-6 col-lg-4">
              <div
                className={`card h-100 cursor-pointer ${salaSeleccionada?.nombre_sala === sala.nombre_sala && salaSeleccionada?.edificio === sala.edificio ? 'border-primary border-2' : ''}`}
                onClick={() => setSalaSeleccionada(sala)}
                style={{ cursor: 'pointer' }}
              >
                <div className="card-header bg-white">
                  <h5 className="card-title mb-0">{sala.nombre_sala}</h5>
                  <small className="text-muted">{sala.edificio}</small>
                </div>
                <div className="card-body">
                  <div className="mb-2">
                    <strong>👥 Capacidad:</strong> {sala.capacidad} personas
                  </div>
                  <div className="mb-2">
                    <strong>🏢 Tipo:</strong>{' '}
                    <span className={getTipoSalaBadge(sala.tipo_sala)}>
                      {sala.tipo_sala}
                    </span>
                  </div>
                  <div>
                    <strong>📍 Ubicación:</strong>
                    <div className="text-muted small">
                      {sala.direccion}, {sala.departamento}
                    </div>
                  </div>
                </div>
                {salaSeleccionada?.nombre_sala === sala.nombre_sala && salaSeleccionada?.edificio === sala.edificio && (
                  <div className="card-footer bg-primary text-white text-center">
                    ✓ Sala seleccionada
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="d-flex gap-2">
          <button
            className="btn btn-outline-secondary"
            onClick={() => {
              setPaso(1);
              setSalaSeleccionada(null);
              setError(null);
            }}
          >
            ← Volver
          </button>
          <button
            className="btn btn-primary flex-grow-1"
            onClick={() => setPaso(3)}
            disabled={!salaSeleccionada}
          >
            Continuar →
          </button>
        </div>
      </div>
    </div>
  );

  const renderPaso3 = () => (
    <div className="card">
      <div className="card-header bg-success text-white">
        <h5 className="mb-0">Paso 3: Confirma tu reserva</h5>
      </div>
      <div className="card-body">
        {error && (
          <div className="alert alert-danger alert-dismissible fade show" role="alert">
            {error}
            <button type="button" className="btn-close" onClick={() => setError(null)}></button>
          </div>
        )}

        <div className="alert alert-info">
          <h6 className="alert-heading">Revisa los detalles de tu reserva:</h6>
        </div>

        <div className="card mb-4">
          <div className="card-body">
            <h5 className="card-title">{salaSeleccionada.nombre_sala}</h5>
            <hr />
            <div className="row">
              <div className="col-md-6 mb-3">
                <strong>📅 Fecha:</strong>
                <div>{new Date(fecha + 'T00:00:00').toLocaleDateString('es-ES')}</div>
              </div>
              <div className="col-md-6 mb-3">
                <strong>🕐 Horario:</strong>
                <div>{turnoSeleccionado.hora_inicio} - {turnoSeleccionado.hora_fin}</div>
              </div>
              <div className="col-md-6 mb-3">
                <strong>🏢 Edificio:</strong>
                <div>{salaSeleccionada.edificio}</div>
              </div>
              <div className="col-md-6 mb-3">
                <strong>👥 Capacidad:</strong>
                <div>{salaSeleccionada.capacidad} personas</div>
              </div>
              <div className="col-md-6 mb-3">
                <strong>🏷️ Tipo:</strong>
                <div>
                  <span className={getTipoSalaBadge(salaSeleccionada.tipo_sala)}>
                    {salaSeleccionada.tipo_sala}
                  </span>
                </div>
              </div>
              <div className="col-md-6 mb-3">
                <strong>📍 Ubicación:</strong>
                <div className="text-muted">{salaSeleccionada.direccion}, {salaSeleccionada.departamento}</div>
              </div>
            </div>
          </div>
        </div>

        <div className="d-flex gap-2">
          <button
            className="btn btn-outline-secondary"
            onClick={() => {
              setPaso(2);
              setError(null);
            }}
            disabled={loading}
          >
            ← Volver
          </button>
          <button
            className="btn btn-success flex-grow-1 btn-lg"
            onClick={confirmarReserva}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                Confirmando...
              </>
            ) : (
              '✓ Confirmar reserva'
            )}
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div>
      <h2 className="mb-4">Nueva Reserva</h2>

      {/* Indicador de progreso */}
      <div className="mb-4">
        <div className="d-flex justify-content-between mb-2">
          <small className={paso >= 1 ? 'text-primary fw-bold' : 'text-muted'}>
            1. Fecha y turno
          </small>
          <small className={paso >= 2 ? 'text-primary fw-bold' : 'text-muted'}>
            2. Seleccionar sala
          </small>
          <small className={paso >= 3 ? 'text-success fw-bold' : 'text-muted'}>
            3. Confirmar
          </small>
        </div>
        <div className="progress" style={{ height: '6px' }}>
          <div
            className="progress-bar bg-primary"
            style={{ width: `${(paso / 3) * 100}%` }}
          ></div>
        </div>
      </div>

      {paso === 1 && renderPaso1()}
      {paso === 2 && renderPaso2()}
      {paso === 3 && renderPaso3()}
    </div>
  );
}