import { useState, useEffect } from 'react';
import { Dropdown } from 'react-bootstrap';
import CrearReserva from '../pages/CrearReserva';
import MisReservas from '../pages/MisReservas';
import AdminPanel from '../pages/Auth/AdminPanel';
import Reportes from '../pages/Reportes';
import { useAuth } from '../context/AuthContext';
import '../styles/estilos.css';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const esAdmin = user?.rol === 'admin';
  
  const [vistaActual, setVistaActual] = useState('inicio');

  useEffect(() => {
    if (esAdmin && vistaActual === 'inicio') {
      setVistaActual('admin');
    }
  }, [esAdmin, vistaActual]);

  // Cierra sesión y redirige al login
  const handleLogout = () => {
    logout();
    window.location.href = '/login';
  };

  const renderVista = () => {
    // Si es admin, mostrar según la vista seleccionada
    if (esAdmin) {
      switch (vistaActual) {
        case 'reportes':
          return <Reportes />;
        case 'admin':
        default:
          return <AdminPanel />;
      }
    }

    // Si NO es admin, flujo normal de reservas
    switch (vistaActual) {
      case 'mis-reservas':
        return <MisReservas />;

      case 'crear-reserva':
        return (
          <CrearReserva
            onReservaCreada={() => setVistaActual('mis-reservas')}
          />
        );

      case 'inicio':
      default:
        return (
          <div className="text-center py-5">
            <h2 className="mb-4" style={{color: '#ffffffff'}}>Bienvenido al Sistema de Reservas</h2>
            <p className="mb-4" style={{color: '#ffffffff'}}>
              Selecciona una opción del menú para comenzar
            </p>
            <div className="row justify-content-center g-4">
              <div className="col-md-4">
                <div
                  className="card h-100 shadow-sm cursor-pointer hover-shadow"
                  onClick={() => setVistaActual('crear-reserva')}
                  style={{ cursor: 'pointer', borderColor: '#0056A6' }}
                >
                  <div className="card-body text-center p-4">
                    <h5 className="card-title" style={{color: '#003366'}}>Nueva Reserva</h5>
                    <p className="card-text" style={{color: '#666'}}>
                      Reserva una sala para tus actividades
                    </p>
                  </div>
                </div>
              </div>
              <div className="col-md-4">
                <div
                  className="card h-100 shadow-sm cursor-pointer hover-shadow"
                  onClick={() => setVistaActual('mis-reservas')}
                  style={{ cursor: 'pointer', borderColor: '#0056A6' }}
                >
                  <div className="card-body text-center p-4">
                    <h5 className="card-title" style={{color: '#003366'}}>Mis Reservas</h5>
                    <p className="card-text" style={{color: '#666'}}>
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
    <div className="min-vh-100" style={{background: 'linear-gradient(180deg, #0056A6 0%, #003366 100%)'}}>
      {/* Navbar */}
      <nav className="navbar navbar-expand-lg navbar-dark shadow" style={{backgroundColor: '#003366'}}>
        <div className="container-fluid">
          <span className="navbar-brand mb-0 h1" style={{color: '#E6F0FA'}}>
            Sistema de Reservas UCU
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
              {/* Menú distinto según sea admin o no */}
              {!esAdmin && (
                <>
                  <li className="nav-item">
                    <button
                      className={`nav-link btn btn-link ${
                        vistaActual === 'inicio' ? 'active' : ''
                      }`}
                      onClick={() => setVistaActual('inicio')}
                    >
                      Inicio
                    </button>
                  </li>
                  <li className="nav-item">
                    <button
                      className={`nav-link btn btn-link ${
                        vistaActual === 'crear-reserva' ? 'active' : ''
                      }`}
                      onClick={() => setVistaActual('crear-reserva')}
                    >
                      Nueva Reserva
                    </button>
                  </li>
                  <li className="nav-item">
                    <button
                      className={`nav-link btn btn-link ${
                        vistaActual === 'mis-reservas' ? 'active' : ''
                      }`}
                      onClick={() => setVistaActual('mis-reservas')}
                    >
                      Mis Reservas
                    </button>
                  </li>
                </>
              )}

              {esAdmin && (
                <>
                  <li className="nav-item">
                    <button
                      className={`nav-link btn btn-link ${vistaActual === 'admin' ? 'active' : ''}`}
                      onClick={() => setVistaActual('admin')}
                      style={vistaActual === 'admin' ? {color: '#E6F0FA', fontWeight: 'bold'} : {color: '#E6F0FA'}}
                    >
                      🔧 Panel Admin
                    </button>
                  </li>
                  <li className="nav-item">
                    <button
                      className={`nav-link btn btn-link ${vistaActual === 'reportes' ? 'active' : ''}`}
                      onClick={() => setVistaActual('reportes')}
                      style={vistaActual === 'reportes' ? {color: '#E6F0FA', fontWeight: 'bold'} : {color: '#E6F0FA'}}
                    >
                      📊 Reportes BI
                    </button>
                  </li>
                </>
              )}

              {/* Dropdown usuario */}
              <li className="nav-item">
                <Dropdown align="end">
                  <Dropdown.Toggle variant="link" className="nav-link text-decoration-none" id="userDropdown" style={{color: '#E6F0FA'}}>
                    {user?.nombre || 'Usuario'}
                  </Dropdown.Toggle>

                  <Dropdown.Menu>
                    <Dropdown.ItemText>
                      <small style={{color: '#666'}}>
                        {user?.email || 'usuario@ucu.edu.uy'}
                      </small>
                    </Dropdown.ItemText>
                    <Dropdown.Divider />
                    <Dropdown.Item onClick={handleLogout} className="text-danger">
                      Cerrar Sesión
                    </Dropdown.Item>
                  </Dropdown.Menu>
                </Dropdown>
              </li>
            </ul>
          </div>
        </div>
      </nav>

      {/* Contenido Principal */}
      <div className="container-fluid py-4">
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