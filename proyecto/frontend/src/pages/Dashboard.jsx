import { useState } from 'react';
import CrearReserva from './CrearReserva';
import MisReservas from './MisReservas';
export default function Dashboard() {
  const [vistaActual, setVistaActual] = useState('inicio');

  // Simulación de usuario - en tu caso real viene del AuthContext
  const user = {
    nombre: 'Usuario',
    email: 'usuario@ucu.edu.uy'
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/login';
  };

  const renderVista = () => {
    switch (vistaActual) {
      case 'mis-reservas':
        return <MisReservas />;
      case 'crear-reserva':
        return <CrearReserva onReservaCreada={() => setVistaActual('mis-reservas')} />;
      case 'inicio':
      default:
        return (
          <div className="text-center py-5">
            <h2 className="mb-4">Bienvenido al Sistema de Reservas</h2>
            <p className="text-muted mb-4">
              Selecciona una opción del menú para comenzar
            </p>
            <div className="row justify-content-center g-4">
              <div className="col-md-4">
                <div 
                  className="card h-100 shadow-sm cursor-pointer hover-shadow"
                  onClick={() => setVistaActual('crear-reserva')}
                  style={{ cursor: 'pointer' }}
                >
                  <div className="card-body text-center p-4">
                    <div className="display-4 mb-3">📅</div>
                    <h5 className="card-title">Nueva Reserva</h5>
                    <p className="card-text text-muted">
                      Reserva una sala para tus actividades
                    </p>
                  </div>
                </div>
              </div>
              <div className="col-md-4">
                <div 
                  className="card h-100 shadow-sm cursor-pointer hover-shadow"
                  onClick={() => setVistaActual('mis-reservas')}
                  style={{ cursor: 'pointer' }}
                >
                  <div className="card-body text-center p-4">
                    <div className="display-4 mb-3">📋</div>
                    <h5 className="card-title">Mis Reservas</h5>
                    <p className="card-text text-muted">
                      Ver y gestionar tus reservas
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="min-vh-100 bg-light">
      {/* Navbar */}
      <nav className="navbar navbar-expand-lg navbar-dark bg-primary shadow">
        <div className="container-fluid">
          <span className="navbar-brand mb-0 h1">
            🏫 Sistema de Reservas UCU
          </span>
          <button 
            className="navbar-toggler" 
            type="button" 
            data-bs-toggle="collapse" 
            data-bs-target="#navbarNav"
          >
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="navbar-nav ms-auto">
              <li className="nav-item">
                <button 
                  className={`nav-link btn btn-link ${vistaActual === 'inicio' ? 'active' : ''}`}
                  onClick={() => setVistaActual('inicio')}
                >
                  Inicio
                </button>
              </li>
              <li className="nav-item">
                <button 
                  className={`nav-link btn btn-link ${vistaActual === 'crear-reserva' ? 'active' : ''}`}
                  onClick={() => setVistaActual('crear-reserva')}
                >
                  Nueva Reserva
                </button>
              </li>
              <li className="nav-item">
                <button 
                  className={`nav-link btn btn-link ${vistaActual === 'mis-reservas' ? 'active' : ''}`}
                  onClick={() => setVistaActual('mis-reservas')}
                >
                  Mis Reservas
                </button>
              </li>
              <li className="nav-item dropdown">
                <a 
                  className="nav-link dropdown-toggle" 
                  href="#" 
                  id="userDropdown" 
                  role="button" 
                  data-bs-toggle="dropdown"
                >
                  👤 {user?.nombre || 'Usuario'}
                </a>
                <ul className="dropdown-menu dropdown-menu-end">
                  <li>
                    <span className="dropdown-item-text">
                      <small className="text-muted">{user?.email}</small>
                    </span>
                  </li>
                  <li><hr className="dropdown-divider" /></li>
                  <li>
                    <button className="dropdown-item text-danger" onClick={handleLogout}>
                      Cerrar Sesión
                    </button>
                  </li>
                </ul>
              </li>
            </ul>
          </div>
        </div>
      </nav>

      {/* Contenido Principal */}
      <div className="container py-4">
        {renderVista()}
      </div>

      <style>{`
        .hover-shadow:hover {
          box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
          transform: translateY(-2px);
          transition: all 0.3s ease;
        }
        
        .nav-link.active {
          font-weight: bold;
        }
      `}</style>
    </div>
  );
}