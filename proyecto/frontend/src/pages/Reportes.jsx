import { useState, useEffect } from 'react';
import '../styles/estilos.css';
import { reportesService } from '../services/reportesService';

const API_URL = 'http://localhost:5000/api';

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : ''
  };
};

export default function Reportes() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reporteActivo, setReporteActivo] = useState('salas');
  
  // Estados para cada reporte
  const [salasData, setSalasData] = useState([]);
  const [turnosData, setTurnosData] = useState([]);
  const [promedioData, setPromedioData] = useState([]);
  const [carreraData, setCarreraData] = useState([]);
  const [ocupacionData, setOcupacionData] = useState([]);
  const [rolData, setRolData] = useState([]);
  const [sancionesData, setSancionesData] = useState([]);
  const [efectividadData, setEfectividadData] = useState(null);
  const [horariosData, setHorariosData] = useState([]);
  const [tendenciaData, setTendenciaData] = useState([]);
  const [usuariosData, setUsuariosData] = useState([]);

  useEffect(() => {
    cargarReporte(reporteActivo);
  }, [reporteActivo]);

  const cargarReporte = async (tipo) => {
  setLoading(true);
  setError(null);
  try {
    let response;

    switch(tipo) {
      case 'salas':
        response = await reportesService.getSalasMasReservadas();
        setSalasData(response.data.data);
        break;
      case 'turnos':
        response = await reportesService.getTurnosMasDemandados();
        setTurnosData(response.data.data);
        break;
      case 'promedio':
        response = await reportesService.getPromedioParticipantes();
        setPromedioData(response.data.data);
        break;
      case 'carrera':
        response = await reportesService.getReservasPorCarrera();
        setCarreraData(response.data.data);
        break;
      case 'ocupacion':
        response = await reportesService.getOcupacionPorEdificio();
        setOcupacionData(response.data.data);
        break;
      case 'rol':
        response = await reportesService.getReservasPorRol();
        setRolData(response.data.data);
        break;
      case 'sanciones':
        response = await reportesService.getSancionesPorRol();
        setSancionesData(response.data.data);
        break;
      case 'efectividad':
        response = await reportesService.getEfectividadReservas();
        setEfectividadData(response.data.data);
        break;
      case 'horarios':
        response = await reportesService.getHorariosPico();
        setHorariosData(response.data.data);
        break;
      case 'tendencia':
        response = await reportesService.getTendenciaMensual();
        setTendenciaData(response.data.data);
        break;
      case 'usuarios':
        response = await reportesService.getUsuariosActivos();
        setUsuariosData(response.data.data);
        break;
      default:
        return;
    }
  } catch (err) {
    setError(err.response?.data?.message || 'Error de conexión con el servidor');
    console.error(err);
  } finally {
    setLoading(false);
  }
};

  const renderSalasReporte = () => (
    <div className="card" style={{backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid #0056A6'}}>
      <div className="card-header text-white" style={{backgroundColor: '#0056A6'}}>
        <h5 className="mb-0">📊 Salas Más Reservadas</h5>
      </div>
      <div className="card-body">
        <div className="table-responsive">
          <table className="table table-hover">
            <thead>
              <tr style={{backgroundColor: '#003366'}}>
                <th style={{color: '#073766ff'}}>Posición</th>
                <th style={{color: '#073766ff'}}>Sala</th>
                <th style={{color: '#073766ff'}}>Edificio</th>
                <th style={{color: '#073766ff'}}>Tipo</th>
                <th style={{color: '#073766ff'}}>Capacidad</th>
                <th style={{color: '#073766ff'}}>Total Reservas</th>
              </tr>
            </thead>
            <tbody>
              {salasData.map((sala, index) => (
                <tr key={index}>
                  <td style={{color: '#333'}}>
                    <span className="badge" style={{
                      backgroundColor: index === 0 ? '#FFD700' : index === 1 ? '#C0C0C0' : index === 2 ? '#CD7F32' : '#0056A6',
                      color: index < 3 ? '#000' : '#fff'
                    }}>
                      #{index + 1}
                    </span>
                  </td>
                  <td style={{color: '#333', fontWeight: index < 3 ? 'bold' : 'normal'}}>{sala.nombre_sala}</td>
                  <td style={{color: '#333'}}>{sala.edificio}</td>
                  <td><span className={`badge ${sala.tipo_sala === 'libre' ? 'bg-primary' : sala.tipo_sala === 'docente' ? 'bg-danger' : 'bg-warning text-dark'}`}>{sala.tipo_sala}</span></td>
                  <td style={{color: '#333'}}>{sala.capacidad}</td>
                  <td style={{color: '#333', fontWeight: 'bold'}}>{sala.total_reservas}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderTurnosReporte = () => (
    <div className="card" style={{backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid #0056A6'}}>
      <div className="card-header text-white" style={{backgroundColor: '#0056A6'}}>
        <h5 className="mb-0">🕐 Turnos Más Demandados</h5>
      </div>
      <div className="card-body">
        <div className="row g-3">
          {turnosData.map((turno, index) => (
            <div key={turno.id_turno} className="col-md-6 col-lg-4">
              <div className="card h-100" style={{borderColor: '#0056A6'}}>
                <div className="card-body text-center">
                  <h6 style={{color: '#003366'}}>Turno {turno.id_turno}</h6>
                  <div className="my-3">
                    <h3 style={{color: '#0056A6'}}>{turno.hora_inicio} - {turno.hora_fin}</h3>
                  </div>
                  <div className="alert alert-info mb-0">
                    <strong>{turno.total_reservas}</strong> reservas
                  </div>
                  <div className="progress mt-2" style={{height: '10px'}}>
                    <div 
                      className="progress-bar" 
                      style={{
                        width: `${(turno.total_reservas / Math.max(...turnosData.map(t => t.total_reservas))) * 100}%`,
                        backgroundColor: '#0056A6'
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderPromedioReporte = () => (
    <div className="card" style={{backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid #0056A6'}}>
      <div className="card-header text-white" style={{backgroundColor: '#0056A6'}}>
        <h5 className="mb-0">👥 Promedio de Participantes por Sala</h5>
      </div>
      <div className="card-body">
        <div className="table-responsive">
          <table className="table table-hover">
            <thead>
              <tr style={{backgroundColor: '#003366'}}>
                <th style={{color: '#073766ff'}}>Sala</th>
                <th style={{color: '#073766ff'}}>Edificio</th>
                <th style={{color: '#073766ff'}}>Capacidad</th>
                <th style={{color: '#073766ff'}}>Reservas</th>
                <th style={{color: '#073766ff'}}>Participantes</th>
                <th style={{color: '#073766ff'}}>Promedio</th>
              </tr>
            </thead>
            <tbody>
              {promedioData.map((sala, index) => (
                <tr key={index}>
                  <td style={{color: '#333'}}>{sala.nombre_sala}</td>
                  <td style={{color: '#333'}}>{sala.edificio}</td>
                  <td style={{color: '#333'}}>{sala.capacidad}</td>
                  <td style={{color: '#333'}}>{sala.total_reservas}</td>
                  <td style={{color: '#333'}}>{sala.total_participantes}</td>
                  <td style={{color: '#0056A6', fontWeight: 'bold'}}>{sala.promedio_participantes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderCarreraReporte = () => (
    <div className="card" style={{backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid #0056A6'}}>
      <div className="card-header text-white" style={{backgroundColor: '#0056A6'}}>
        <h5 className="mb-0">🎓 Reservas por Carrera y Facultad</h5>
      </div>
      <div className="card-body">
        <div className="table-responsive">
          <table className="table table-hover">
            <thead>
              <tr style={{backgroundColor: '#003366'}}>
                <th style={{color: '#073766ff'}}>Facultad</th>
                <th style={{color: '#073766ff'}}>Programa</th>
                <th style={{color: '#073766ff'}}>Tipo</th>
                <th style={{color: '#073766ff'}}>Total Reservas</th>
              </tr>
            </thead>
            <tbody>
              {carreraData.map((item, index) => (
                <tr key={index}>
                  <td style={{color: '#333', fontWeight: 'bold'}}>{item.facultad}</td>
                  <td style={{color: '#333'}}>{item.nombre_programa}</td>
                  <td><span className={`badge ${item.tipo === 'grado' ? 'bg-primary' : 'bg-warning text-dark'}`}>{item.tipo}</span></td>
                  <td style={{color: '#0056A6', fontWeight: 'bold'}}>{item.total_reservas}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderOcupacionReporte = () => (
    <div className="card" style={{backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid #0056A6'}}>
      <div className="card-header text-white" style={{backgroundColor: '#0056A6'}}>
        <h5 className="mb-0">🏢 Porcentaje de Ocupación por Edificio</h5>
      </div>
      <div className="card-body">
        <div className="row g-4">
          {ocupacionData.map((edificio, index) => (
            <div key={index} className="col-md-6">
              <div className="card h-100" style={{borderColor: '#0056A6'}}>
                <div className="card-body">
                  <h5 style={{color: '#003366'}}>{edificio.nombre_edificio}</h5>
                  <hr />
                  <div className="mb-3">
                    <small style={{color: '#666'}}>Salas totales:</small>
                    <div style={{color: '#333', fontSize: '1.5rem', fontWeight: 'bold'}}>{edificio.total_salas}</div>
                  </div>
                  <div className="mb-3">
                    <small style={{color: '#666'}}>Reservas activas:</small>
                    <div style={{color: '#333', fontSize: '1.2rem'}}>{edificio.reservas_activas}</div>
                  </div>
                  <div className="mb-3">
                    <small style={{color: '#666'}}>Total reservas:</small>
                    <div style={{color: '#333', fontSize: '1.2rem'}}>{edificio.total_reservas}</div>
                  </div>
                  <div className="mt-3">
                    <label style={{color: '#666'}}>Ocupación:</label>
                    <div className="progress" style={{height: '25px'}}>
                      <div 
                        className="progress-bar" 
                        style={{
                          width: `${edificio.porcentaje_ocupacion}%`,
                          backgroundColor: edificio.porcentaje_ocupacion > 75 ? '#dc3545' : edificio.porcentaje_ocupacion > 50 ? '#ffc107' : '#28a745'
                        }}
                      >
                        <strong>{edificio.porcentaje_ocupacion}%</strong>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderRolReporte = () => (
    <div className="card" style={{backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid #0056A6'}}>
      <div className="card-header text-white" style={{backgroundColor: '#0056A6'}}>
        <h5 className="mb-0">📈 Reservas y Asistencias por Rol</h5>
      </div>
      <div className="card-body">
        <div className="table-responsive">
          <table className="table table-hover">
            <thead>
              <tr style={{backgroundColor: '#003366'}}>
                <th style={{color: '#073766ff'}}>Rol</th>
                <th style={{color: '#073766ff'}}>Tipo Programa</th>
                <th style={{color: '#073766ff'}}>Reservas</th>
                <th style={{color: '#073766ff'}}>Asistencias</th>
                <th style={{color: '#073766ff'}}>Inasistencias</th>
                <th style={{color: '#073766ff'}}>% Asistencia</th>
              </tr>
            </thead>
            <tbody>
              {rolData.map((item, index) => (
                <tr key={index}>
                  <td><span className={`badge ${item.rol === 'docente' ? 'bg-danger' : 'bg-primary'}`}>{item.rol}</span></td>
                  <td style={{color: '#333'}}>{item.tipo_programa}</td>
                  <td style={{color: '#333'}}>{item.total_reservas}</td>
                  <td style={{color: '#28a745', fontWeight: 'bold'}}>{item.total_asistencias}</td>
                  <td style={{color: '#dc3545', fontWeight: 'bold'}}>{item.total_inasistencias}</td>
                  <td>
                    <span className={`badge ${item.porcentaje_asistencia > 80 ? 'bg-success' : item.porcentaje_asistencia > 60 ? 'bg-warning text-dark' : 'bg-danger'}`}>
                      {item.porcentaje_asistencia}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderSancionesReporte = () => (
    <div className="card" style={{backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid #0056A6'}}>
      <div className="card-header text-white" style={{backgroundColor: '#0056A6'}}>
        <h5 className="mb-0">⚠️ Sanciones por Rol</h5>
      </div>
      <div className="card-body">
        <div className="row g-4">
          {sancionesData.map((item, index) => (
            <div key={index} className="col-md-6">
              <div className="card h-100" style={{borderColor: '#0056A6'}}>
                <div className="card-header bg-white">
                  <h5 style={{color: '#003366'}}>
                    <span className={`badge ${item.rol === 'docente' ? 'bg-danger' : 'bg-primary'}`}>{item.rol}</span>
                    {' '}{item.tipo_programa}
                  </h5>
                </div>
                <div className="card-body">
                  <div className="row text-center">
                    <div className="col-6">
                      <div className="alert alert-warning">
                        <h3 style={{color: '#333'}}>{item.total_sanciones}</h3>
                        <small>Total</small>
                      </div>
                    </div>
                    <div className="col-6">
                      <div className="alert alert-danger">
                        <h3 style={{color: '#333'}}>{item.sanciones_activas}</h3>
                        <small>Activas</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderEfectividadReporte = () => (
    <div className="card" style={{backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid #0056A6'}}>
      <div className="card-header text-white" style={{backgroundColor: '#0056A6'}}>
        <h5 className="mb-0">✅ Efectividad de Reservas</h5>
      </div>
      <div className="card-body">
        {efectividadData && (
          <>
            <div className="row g-4 mb-4">
              <div className="col-md-3">
                <div className="card text-center" style={{backgroundColor: '#E6F0FA'}}>
                  <div className="card-body">
                    <h2 style={{color: '#0056A6'}}>{efectividadData.total_reservas}</h2>
                    <p style={{color: '#333', margin: 0}}>Total</p>
                  </div>
                </div>
              </div>
              <div className="col-md-3">
                <div className="card text-center" style={{backgroundColor: '#d4edda'}}>
                  <div className="card-body">
                    <h2 style={{color: '#28a745'}}>{efectividadData.finalizadas}</h2>
                    <p style={{color: '#333', margin: 0}}>Finalizadas</p>
                  </div>
                </div>
              </div>
              <div className="col-md-3">
                <div className="card text-center" style={{backgroundColor: '#f8d7da'}}>
                  <div className="card-body">
                    <h2 style={{color: '#dc3545'}}>{efectividadData.canceladas}</h2>
                    <p style={{color: '#333', margin: 0}}>Canceladas</p>
                  </div>
                </div>
              </div>
              <div className="col-md-3">
                <div className="card text-center" style={{backgroundColor: '#fff3cd'}}>
                  <div className="card-body">
                    <h2 style={{color: '#ffc107'}}>{efectividadData.sin_asistencia}</h2>
                    <p style={{color: '#333', margin: 0}}>Sin Asistencia</p>
                  </div>
                </div>
              </div>
            </div>

            <hr />

            <div className="row g-4">
              <div className="col-md-4">
                <h6 style={{color: '#003366'}}>Reservas Utilizadas</h6>
                <div className="progress" style={{height: '40px'}}>
                  <div 
                    className="progress-bar bg-success" 
                    style={{width: `${efectividadData.porcentaje_utilizadas}%`}}
                  >
                    <strong>{efectividadData.porcentaje_utilizadas}%</strong>
                  </div>
                </div>
              </div>
              <div className="col-md-4">
                <h6 style={{color: '#003366'}}>Reservas Canceladas</h6>
                <div className="progress" style={{height: '40px'}}>
                  <div 
                    className="progress-bar bg-danger" 
                    style={{width: `${efectividadData.porcentaje_canceladas}%`}}
                  >
                    <strong>{efectividadData.porcentaje_canceladas}%</strong>
                  </div>
                </div>
              </div>
              <div className="col-md-4">
                <h6 style={{color: '#003366'}}>Sin Asistencia</h6>
                <div className="progress" style={{height: '40px'}}>
                  <div 
                    className="progress-bar bg-warning" 
                    style={{width: `${efectividadData.porcentaje_sin_asistencia}%`}}
                  >
                    <strong>{efectividadData.porcentaje_sin_asistencia}%</strong>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );

  const renderHorariosReporte = () => (
    <div className="card" style={{backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid #0056A6'}}>
      <div className="card-header text-white" style={{backgroundColor: '#0056A6'}}>
        <h5 className="mb-0">⏰ Horarios Pico (Franja Horaria)</h5>
      </div>
      <div className="card-body">
        <div className="row g-4">
          {horariosData.map((horario, index) => (
            <div key={index} className="col-md-4">
              <div className="card h-100 text-center" style={{borderColor: '#0056A6'}}>
                <div className="card-body">
                  <h5 style={{color: '#003366'}}>{horario.franja_horaria}</h5>
                  <h2 style={{color: '#0056A6'}}>{horario.total_reservas}</h2>
                  <p style={{color: '#666'}}>reservas</p>
                  <div className="progress" style={{height: '20px'}}>
                    <div 
                      className="progress-bar" 
                      style={{
                        width: `${horario.porcentaje}%`,
                        backgroundColor: '#0056A6'
                      }}
                    >
                      <strong>{horario.porcentaje}%</strong>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderTendenciaReporte = () => (
    <div className="card" style={{backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid #0056A6'}}>
      <div className="card-header text-white" style={{backgroundColor: '#0056A6'}}>
        <h5 className="mb-0">📅 Tendencia de Uso Mensual (Últimos 6 meses)</h5>
      </div>
      <div className="card-body">
        <div className="table-responsive">
          <table className="table table-hover">
            <thead>
              <tr style={{backgroundColor: '#003366'}}>
                <th style={{color: '#073766ff'}}>Mes</th>
                <th style={{color: '#073766ff'}}>Total Reservas</th>
                <th style={{color: '#073766ff'}}>Salas Utilizadas</th>
                <th style={{color: '#073766ff'}}>Edificios Utilizados</th>
              </tr>
            </thead>
            <tbody>
              {tendenciaData.map((item, index) => (
                <tr key={index}>
                  <td style={{color: '#333', fontWeight: 'bold'}}>{item.mes}</td>
                  <td style={{color: '#0056A6', fontWeight: 'bold'}}>{item.total_reservas}</td>
                  <td style={{color: '#333'}}>{item.salas_utilizadas}</td>
                  <td style={{color: '#333'}}>{item.edificios_utilizados}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderUsuariosReporte = () => (
    <div className="card" style={{backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid #0056A6'}}>
      <div className="card-header text-white" style={{backgroundColor: '#0056A6'}}>
        <h5 className="mb-0">🏆 Top 20 Usuarios Más Activos</h5>
      </div>
      <div className="card-body">
        <div className="table-responsive">
          <table className="table table-hover">
            <thead>
              <tr style={{backgroundColor: '#003366'}}>
                <th style={{color: '#073766ff'}}>Pos.</th>
                <th style={{color: '#073766ff'}}>CI</th>
                <th style={{color: '#073766ff'}}>Nombre</th>
                <th style={{color: '#073766ff'}}>Rol</th>
                <th style={{color: '#073766ff'}}>Programa</th>
                <th style={{color: '#073766ff'}}>Reservas</th>
                <th style={{color: '#073766ff'}}>Asistencias</th>
                <th style={{color: '#073766ff'}}>Sanciones</th>
              </tr>
            </thead>
            <tbody>
              {usuariosData.map((user, index) => (
                <tr key={user.ci}>
                  <td>
                    <span className="badge" style={{
                      backgroundColor: index === 0 ? '#FFD700' : index === 1 ? '#C0C0C0' : index === 2 ? '#CD7F32' : '#0056A6',
                      color: index < 3 ? '#000' : '#fff'
                    }}>
                      #{index + 1}
                    </span>
                  </td>
                  <td style={{color: '#333'}}>{user.ci}</td>
                  <td style={{color: '#333', fontWeight: index < 3 ? 'bold' : 'normal'}}>
                    {user.nombre} {user.apellido}
                  </td>
                  <td><span className={`badge ${user.rol === 'docente' ? 'bg-danger' : 'bg-primary'}`}>{user.rol}</span></td>
                  <td style={{color: '#333'}}><small>{user.tipo_programa}</small></td>
                  <td style={{color: '#0056A6', fontWeight: 'bold'}}>{user.total_reservas}</td>
                  <td style={{color: '#28a745'}}>{user.asistencias}</td>
                  <td style={{color: user.sanciones > 0 ? '#dc3545' : '#666'}}>{user.sanciones}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const menuReportes = [
    { id: 'salas', icon: '📊', label: 'Salas Más Reservadas' },
    { id: 'turnos', icon: '🕐', label: 'Turnos Demandados' },
    { id: 'promedio', icon: '👥', label: 'Promedio Participantes' },
    { id: 'carrera', icon: '🎓', label: 'Por Carrera/Facultad' },
    { id: 'ocupacion', icon: '🏢', label: 'Ocupación Edificios' },
    { id: 'rol', icon: '📈', label: 'Reservas por Rol' },
    { id: 'sanciones', icon: '⚠️', label: 'Sanciones' },
    { id: 'efectividad', icon: '✅', label: 'Efectividad' },
    { id: 'horarios', icon: '⏰', label: 'Horarios Pico' },
    { id: 'tendencia', icon: '📅', label: 'Tendencia Mensual' },
    { id: 'usuarios', icon: '🏆', label: 'Top Usuarios' },
  ];

  return (
    <div>
      <h2 className="mb-4" style={{color: '#E6F0FA'}}>📊 Reportes de Business Intelligence</h2>

      {/* Menú de navegación entre reportes */}
      <div className="card mb-4" style={{backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid #0056A6'}}>
        <div className="card-body">
          <div className="row g-2">
            {menuReportes.map((item) => (
              <div key={item.id} className="col-md-3">
                <button
                  className={`btn w-100 ${reporteActivo === item.id ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => setReporteActivo(item.id)}
                  style={reporteActivo === item.id ? {
                    backgroundColor: '#0056A6',
                    borderColor: '#0056A6'
                  } : {
                    color: '#0056A6',
                    borderColor: '#0056A6'
                  }}
                >
                  {item.icon} {item.label}
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Contenido del reporte activo */}
      {loading ? (
        <div className="text-center py-5">
          <div className="spinner-border" style={{color: '#E6F0FA'}} role="status">
            <span className="visually-hidden">Cargando...</span>
          </div>
        </div>
      ) : error ? (
        <div className="alert alert-danger">{error}</div>
      ) : (
        <>
          {reporteActivo === 'salas' && renderSalasReporte()}
          {reporteActivo === 'turnos' && renderTurnosReporte()}
          {reporteActivo === 'promedio' && renderPromedioReporte()}
          {reporteActivo === 'carrera' && renderCarreraReporte()}
          {reporteActivo === 'ocupacion' && renderOcupacionReporte()}
          {reporteActivo === 'rol' && renderRolReporte()}
          {reporteActivo === 'sanciones' && renderSancionesReporte()}
          {reporteActivo === 'efectividad' && renderEfectividadReporte()}
          {reporteActivo === 'horarios' && renderHorariosReporte()}
          {reporteActivo === 'tendencia' && renderTendenciaReporte()}
          {reporteActivo === 'usuarios' && renderUsuariosReporte()}
        </>
      )}
    </div>
  );
}