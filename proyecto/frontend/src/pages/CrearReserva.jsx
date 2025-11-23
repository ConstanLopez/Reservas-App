import { useState, useEffect } from 'react';
import { getTurnos, getSalasDisponibles, crearReserva } from '../services/reservasService';

export default function CrearReserva({ onReservaCreada }) {
  const [paso, setPaso] = useState(1); //  Pasos para la reserva : 1: Fecha y turno, 2: Seleccionar sala, 3: Confirmar
  const [turnos, setTurnos] = useState([]);
  const [salasDisponibles, setSalasDisponibles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
const [horaDesde, setHoraDesde] = useState("");
const [horaHasta, setHoraHasta] = useState("");
const [turnosSeleccionados, setTurnosSeleccionados] = useState([])

  // Datos del formulario
  const [fecha, setFecha] = useState('');
  const [turnoSeleccionado, setTurnoSeleccionado] = useState(null);
  const [salaSeleccionada, setSalaSeleccionada] = useState(null);

  const [participantes, setParticipantes] = useState([]);

  useEffect(() => {
    cargarTurnos();
  }, []);

  console.log(turnosSeleccionados)
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

  const tieneRango = turnosSeleccionados.length > 0;

const horaInicioRango = tieneRango
  ? turnosSeleccionados[0].hora_inicio
  : turnoSeleccionado?.hora_inicio || '';

const horaFinRango = tieneRango
  ? turnosSeleccionados[turnosSeleccionados.length - 1].hora_fin
  : turnoSeleccionado?.hora_fin || '';

  const buscarSalasDisponibles = async () => {
    if (!fecha || !turnoSeleccionado) {
      setError('Debes seleccionar una fecha y un turno');
      return;
    }

     const turnoBase = turnosSeleccionados[0];
    // Validar que la fecha no sea pasada
    const hoy = new Date().toISOString().split('T')[0];
    if (fecha < hoy) {
      setError('No puedes reservar para fechas pasadas');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await getSalasDisponibles(fecha, turnoBase.id_turno);

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
  
  const agregarParticipante = () => {
    setParticipantes((prev) => [
      ...prev,
      { nombre: '', ci: '' }
    ]);
  };

  const actualizarParticipante = (index, campo, valor) => {
    setParticipantes((prev) =>
      prev.map((p, i) =>
        i === index ? { ...p, [campo]: valor } : p
      )
    );
  };

  const eliminarParticipante = (index) => {
    setParticipantes((prev) => prev.filter((_, i) => i !== index));
  };

  const participantesLimpios = participantes.filter(
        (p) => p.ci.trim() !== '' || p.nombre.trim() !== ''
      );
  
  if (participantesLimpios.some(p => isNaN(Number(p.ci)))) {
  setError('Las cédulas deben ser numéricas');
  setLoading(false);
  return;
}

  const confirmarReserva = async () => {
    try {
      setLoading(true);
      setError(null);
  
  const participantesList = participantes
  .filter(p => p.ci.trim() !== '' || p.nombre.trim() !== '')
  .map(p => ({
    ci: p.ci.trim(),
    nombre: p.nombre.trim()
  }));

  console.log(participantesList)
  
  const horaInicioRango = turnosSeleccionados[0].hora_inicio;
  const horaFinRango = turnosSeleccionados[turnosSeleccionados.length - 1].hora_fin;

  const reservaData = {
        nombre_sala: salaSeleccionada.nombre_sala,
        edificio: salaSeleccionada.edificio,
        fecha: fecha,
        id_turno: turnoSeleccionado.id_turno,
        participantes: participantesList,
        hora_inicio_rango: horaInicioRango || null,
        hora_fin_rango: horaFinRango || null,
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
        setParticipantes([]); 

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


  const seleccionarBloquesPorRango = () => {
  if (!horaDesde || !horaHasta) {
    setError("Debes ingresar hora desde y hasta");
    return;
  }

  let minDesde = toMinutes(horaDesde);
  let minHasta = toMinutes(horaHasta);

  if (minHasta <= minDesde) {
    setError("El rango de horas es inválido");
    return;
  }

  // Redondeo a horas exactas según bloques de 1h
  const bloqueDesde = Math.floor(minDesde / 60) * 60;
  const bloqueHasta = Math.ceil(minHasta / 60) * 60;

  const seleccionados = turnos.filter((t) => {
    const ini = toMinutes(t.hora_inicio.slice(0, 5));
    const fin = toMinutes(t.hora_fin.slice(0, 5));
    return ini >= bloqueDesde && fin <= bloqueHasta;
  });

  if (seleccionados.length === 0) {
    setError("No hay bloques que coincidan con ese rango");
    return;
  }

  // Selecciona solo el primer turno por ahora, como funciona tu backend
  setTurnoSeleccionado(seleccionados[0]);

  // Guarda todos los turnos por si luego deseas crear varias reservas
  setTurnosSeleccionados(seleccionados);
};

  
  const toMinutes = (horaStr) => {
  const [h, m] = horaStr.split(":").map(Number);
  return h * 60 + m;
};
  const renderPaso1 = () => (
    <div className="card" style={{backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid #0056A6'}}>
      <div className="card-header text-white" style={{backgroundColor: '#0056A6'}}>
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
          <label htmlFor="fecha" className="form-label fw-bold" style={{color: '#003366'}}>
            📅 Fecha de la reserva
          </label>
          <input
            type="date"
            className="form-control"
            id="fecha"
            value={fecha}
            onChange={(e) => setFecha(e.target.value)}
            min={new Date().toISOString().split('T')[0]}
            style={{borderColor: '#0056A6'}}
          />
        </div>

        <div className="mb-4">
  <label className="form-label fw-bold" style={{color: '#003366'}}> Rango de horario </label>

  <div className="row g-2">
    <div className="col-md-6">
      <input
        type="time"
        className="form-control"
        value={horaDesde}
        onChange={(e) => setHoraDesde(e.target.value)}
      />
    </div>
    <div className="col-md-6">
      <input
        type="time"
        className="form-control"
        value={horaHasta}
        onChange={(e) => setHoraHasta(e.target.value)}
      />
    </div>
  </div>

  <button
    className="btn btn-outline-primary mt-2"
    onClick={seleccionarBloquesPorRango}
  >
    Seleccionar bloques automáticamente
  </button>
</div>

        <div className="mb-4">
          <label className="form-label fw-bold" style={{color: '#003366'}}>🕐 Turno</label>
          <div className="row g-3">
            {turnos.map((turno) => (
              <div key={turno.id_turno} className="col-md-6">
                <div
                  className={`card cursor-pointer ${turnoSeleccionado?.id_turno === turno.id_turno ? 'border-2 bg-light' : ''}`}
                  onClick={() => {setTurnoSeleccionado(turno);setTurnosSeleccionados([turno]);}}
                  style={{
                    cursor: 'pointer',
                    borderColor: turnoSeleccionado?.id_turno === turno.id_turno ? '#0056A6' : '#dee2e6'
                  }}
                >
                  <div className="card-body text-center">
                    <h6 className="mb-1" style={{color: '#003366'}}>{turno.hora_inicio} - {turno.hora_fin}</h6>
                    {turnosSeleccionados.some(t => t.id_turno === turno.id_turno) && (
                      <small style={{color: '#0056A6'}}>✓ Seleccionado</small>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <button
          className="btn btn-lg w-100"
          style={{backgroundColor: '#0056A6', color: 'white', borderColor: '#003366'}}
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
    <div className="card" style={{backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid #0056A6'}}>
      <div className="card-header text-white" style={{backgroundColor: '#0056A6'}}>
        <h5 className="mb-0">Paso 2: Selecciona una sala</h5>
        <small>
            Fecha: {new Date(fecha + 'T00:00:00').toLocaleDateString('es-ES')} |{' '}
            Turno: {horaInicioRango || '-'}{horaInicioRango && ' - '}{horaFinRango}
        </small>
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
                className={`card h-100 cursor-pointer ${salaSeleccionada?.nombre_sala === sala.nombre_sala && salaSeleccionada?.edificio === sala.edificio ? 'border-2' : ''}`}
                onClick={() => setSalaSeleccionada(sala)}
                style={{
                  cursor: 'pointer',
                  borderColor: salaSeleccionada?.nombre_sala === sala.nombre_sala && salaSeleccionada?.edificio === sala.edificio ? '#0056A6' : '#dee2e6'
                }}
              >
                <div className="card-header bg-white">
                  <h5 className="card-title mb-0" style={{color: '#003366'}}>{sala.nombre_sala}</h5>
                  <small style={{color: '#666'}}>{sala.edificio}</small>
                </div>
                <div className="card-body">
                  <div className="mb-2">
                    <strong style={{color: '#333'}}>👥 Capacidad:</strong> <span style={{color: '#333'}}>{sala.capacidad} personas</span>
                  </div>
                  <div className="mb-2">
                    <strong style={{color: '#333'}}>🏢 Tipo:</strong>{' '}
                    <span className={getTipoSalaBadge(sala.tipo_sala)}>
                      {sala.tipo_sala}
                    </span>
                  </div>
                  <div>
                    <strong style={{color: '#333'}}>📍 Ubicación:</strong>
                    <div className="small" style={{color: '#666'}}>
                      {sala.direccion}, {sala.departamento}
                    </div>
                  </div>
                </div>
                {salaSeleccionada?.nombre_sala === sala.nombre_sala && salaSeleccionada?.edificio === sala.edificio && (
                  <div className="card-footer text-white text-center" style={{backgroundColor: '#0056A6'}}>
                    ✓ Sala seleccionada
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="d-flex gap-2">
          <button
            className="btn btn-secondary"
            onClick={() => {
              setPaso(1);
              setSalaSeleccionada(null);
              setError(null);
            }}
          >
            ← Volver
          </button>
          <button
            className="btn flex-grow-1"
            style={{backgroundColor: '#0056A6', color: 'white', borderColor: '#003366'}}
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
    <div className="card" style={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid #0056A6' }}>
      <div className="card-header text-white" style={{ backgroundColor: '#28a745' }}>
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
            <h5 className="card-title" style={{ color: '#003366' }}>
              {salaSeleccionada.nombre_sala}
            </h5>
            <hr />
            <div className="row">
              <div className="col-md-6 mb-3">
                <strong style={{ color: '#333' }}>📅 Fecha:</strong>
                <div style={{ color: '#333' }}>
                  {new Date(fecha + 'T00:00:00').toLocaleDateString('es-ES')}
                </div>
              </div>
              <div className="col-md-6 mb-3">
                <strong style={{ color: '#333' }}>🕐 Horario:</strong>
                <div style={{ color: '#333' }}>
                  {horaInicioRango || '-'}{horaInicioRango && ' - '}{horaFinRango}
                </div>
              </div>
              <div className="col-md-6 mb-3">
                <strong style={{ color: '#333' }}>🏢 Edificio:</strong>
                <div style={{ color: '#333' }}>{salaSeleccionada.edificio}</div>
              </div>
              <div className="col-md-6 mb-3">
                <strong style={{ color: '#333' }}>👥 Capacidad:</strong>
                <div style={{ color: '#333' }}>{salaSeleccionada.capacidad} personas</div>
              </div>
              <div className="col-md-6 mb-3">
                <strong style={{ color: '#333' }}>🏷️ Tipo:</strong>
                <div>
                  <span className={getTipoSalaBadge(salaSeleccionada.tipo_sala)}>
                    {salaSeleccionada.tipo_sala}
                  </span>
                </div>
              </div>
              <div className="col-md-6 mb-3">
                <strong style={{ color: '#333' }}>📍 Ubicación:</strong>
                <div style={{ color: '#666' }}>
                  {salaSeleccionada.direccion}, {salaSeleccionada.departamento}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mb-4">
          <div className="d-flex justify-content-between align-items-center mb-2">
            <label className="form-label fw-bold mb-0" style={{ color: '#003366' }}>
              👥 Participantes adicionales
            </label>
            <button
              type="button"
              className="btn btn-sm btn-outline-primary"
              onClick={agregarParticipante}
            >
              + Agregar participante
            </button>
          </div>
          <small className="text-muted d-block mb-2">
            No es necesario que te incluyas a vos: el sistema te agrega automáticamente como
            responsable de la reserva.
          </small>

          {participantes.length === 0 && (
            <div className="text-muted small">
              No hay participantes adicionales. Podés agregar compañeros con el botón de arriba.
            </div>
          )}

          {participantes.map((p, index) => (
            <div key={index} className="row g-2 align-items-center mb-2">
              <div className="col-md-5">
                <input
                  type="text"
                  className="form-control"
                  placeholder="Nombre y apellido"
                  value={p.nombre}
                  onChange={(e) => actualizarParticipante(index, 'nombre', e.target.value)}
                />
              </div>
              <div className="col-md-4">
                <input
                  type="text"
                  className="form-control"
                  placeholder="Cédula (sin puntos ni guión)"
                  value={p.ci}
                  onChange={(e) => actualizarParticipante(index, 'ci', e.target.value)}
                />
              </div>
              <div className="col-md-3 text-end">
                <button
                  type="button"
                  className="btn btn-outline-danger btn-sm"
                  onClick={() => eliminarParticipante(index)}
                >
                  Eliminar
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="d-flex gap-2">
          <button
            className="btn btn-secondary"
            onClick={() => {
              setPaso(2);
              setError(null);
            }}
            disabled={loading}
          >
            ← Volver
          </button>
          <button
            className="btn btn-lg flex-grow-1"
            style={{ backgroundColor: '#28a745', color: 'white', borderColor: '#1e7e34' }}
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
      <h2 className="mb-4" style={{ color: '#E6F0FA' }}>
        Nueva Reserva
      </h2>

      {/* Indicador de progreso */}
      <div className="mb-4">
        <div className="d-flex justify-content-between mb-2">
          <small className={paso >= 1 ? 'fw-bold' : ''} style={{ color: paso >= 1 ? '#E6F0FA' : '#ffffffcc' }}>
            1. Fecha y turno
          </small>
          <small className={paso >= 2 ? 'fw-bold' : ''} style={{ color: paso >= 2 ? '#E6F0FA' : '#ffffffcc' }}>
            2. Seleccionar sala
          </small>
          <small className={paso >= 3 ? 'fw-bold' : ''} style={{ color: paso >= 3 ? '#28a745' : '#ffffffcc' }}>
            3. Confirmar
          </small>
        </div>
        <div className="progress" style={{ height: '6px' }}>
          <div
            className="progress-bar"
            style={{ width: `${(paso / 3) * 100}%`, backgroundColor: '#0056A6' }}
          ></div>
        </div>
      </div>

      {paso === 1 && /* renderPaso1 original */ renderPaso1()}
      {paso === 2 && /* renderPaso2 original */ renderPaso2()}
      {paso === 3 && renderPaso3()}
    </div>
  );
}
