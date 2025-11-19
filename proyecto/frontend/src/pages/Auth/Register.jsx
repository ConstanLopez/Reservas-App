import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Alert } from 'react-bootstrap';
import '../../styles/estilos.css'; 
import { useAuth } from '../../context/AuthContext';

export function Register() {
    const [formData, setFormData] = useState({
        ci: '',
        nombre: '',
        apellido: '',
        email: '',
        password: '',
        confirmPassword: '',
        nombre_programa: '',
        rol: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        // Validaciones frontend
        if (formData.password !== formData.confirmPassword) {
            setError('Las contraseñas no coinciden');
            return;
        }

        if (formData.password.length < 6) {
            setError('La contraseña debe tener al menos 6 caracteres');
            return;
        }

        setLoading(true);

        setLoading(true);

  // 👇 ESTE ES EL PAYLOAD (lo que se manda al backend)
  const payload = {
    ci: formData.ci.trim(),
    nombre: formData.nombre.trim(),
    apellido: formData.apellido.trim(),
    email: formData.email.trim(),
    password: formData.password,
    nombre_programa: formData.nombre_programa,
    rol: formData.rol
  };

  console.log('payload register →', payload); // 👈 LOG CLAVE

  const result = await register(payload); // <-- usa useAuth()
  if (result.success) navigate('/dashboard');
  else setError(result.error);

  setLoading(false);
};

    return (
        <div className="position-fixed top-0 start-0 w-100 vh-100 bg-primary-subtle d-flex justify-content-center align-items-center overflow-auto">
            <div className="text-center my-3 py-3" style={{width: '400px'}}>
                <h1 className="h2 mb-3" >Crear Cuenta</h1>

                {error && <Alert variant="danger">{error}</Alert>}

                <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                        <label htmlFor="ci" className="form-label fw-bold">CI:</label>
                        <input 
                            name="ci"
                            value={formData.ci} 
                            onChange={handleChange} 
                            type="text" 
                            className="form-control" 
                            placeholder="12345678" 
                            id="ci"
                            required
                        />
                    </div>

                    <div className="row mb-3">
                        <div className="col">
                            <label htmlFor="nombre" className="form-label fw-bold">Nombre:</label>
                            <input 
                                name="nombre"
                                value={formData.nombre} 
                                onChange={handleChange} 
                                type="text" 
                                className="form-control" 
                                placeholder="Juan" 
                                id="nombre"
                                required
                            />
                        </div>
                        <div className="col">
                            <label htmlFor="apellido" className="form-label fw-bold">Apellido:</label>
                            <input 
                                name="apellido"
                                value={formData.apellido} 
                                onChange={handleChange} 
                                type="text" 
                                className="form-control" 
                                placeholder="Pérez" 
                                id="apellido"
                                required
                            />
                        </div>
                    </div>
                    

                    <div className="mb-3">
                        <label htmlFor="nombre_programa" className="form-label fw-bold">Programa Academico:</label>
                        <input 
                            name="nombre_programa"
                            value={formData.nombre_programa} 
                            onChange={handleChange} 
                            type="text" 
                            className="form-control" 
                            placeholder="Ingenieria Infórmatica" 
                            id="nombre_programa"
                            required
                        />
                    </div>


                    <div className="mb-3">
                        <label htmlFor="rol" className="form-label fw-bold">Rol:</label>
                        <select 
                            name="rol"
                            value={formData.rol} 
                            onChange={handleChange}  
                            className="form-control" 
                            placeholder="Alumno, Docente" 
                            id="rol"
                            required
                        > 
                        <option value=""> Selecciona un Rol</option>
                        <option value="alumno"> Alumno </option>
                        <option value="docente" >Docente</option>
                        </select>
                    </div>


                    <div className="mb-3">
                        <label htmlFor="email" className="form-label fw-bold">Email:</label>
                        <input 
                            name="email"
                            value={formData.email} 
                            onChange={handleChange} 
                            type="email" 
                            className="form-control" 
                            placeholder="juan@ucu.edu.uy" 
                            id="email"
                            required
                        />
                    </div>
                
                    <div className="mb-3">
                        <label htmlFor="password" className="form-label fw-bold">Contraseña:</label>
                        <input 
                            name="password"
                            value={formData.password} 
                            onChange={handleChange} 
                            type="password" 
                            className="form-control" 
                            placeholder="Mínimo 6 caracteres" 
                            id="password"
                            required
                        />
                    </div>

                    <div className="mb-3">
                        <label htmlFor="confirmPassword" className="form-label fw-bold">Confirmar Contraseña:</label>
                        <input 
                            name="confirmPassword"
                            value={formData.confirmPassword} 
                            onChange={handleChange} 
                            type="password" 
                            className="form-control" 
                            placeholder="Repita su contraseña" 
                            id="confirmPassword"
                            required
                        />
                    </div>

                    <button 
                        type="submit" 
                        className="btn btn-dark w-100" 
                        disabled={loading}
                    >
                        {loading ? 'Registrando...' : 'Crear Cuenta'}
                    </button>
                </form>

                <div className="mt-3">
                    <p className="p">
                        ¿Ya tienes cuenta? <a href="/login">Inicia sesión</a>
                    </p>
                </div>
            </div>
        </div>
    );
}