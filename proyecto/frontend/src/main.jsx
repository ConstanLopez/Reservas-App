import React from 'react';
import ReactDOM from 'react-dom/client';
import { StrictMode } from 'react';
import App from './App.jsx';
import { AuthProvider } from './context/AuthContext';
import 'bootstrap/dist/css/bootstrap.min.css';
import './styles/estilos.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </StrictMode>
);
