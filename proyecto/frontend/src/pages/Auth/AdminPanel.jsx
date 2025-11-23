import { useState,useEffect } from "react";
import CrudSection from '../CrudSection';
import {
  participantesApi,
  salasApi,
  reservasApi,
  sancionesApi,
  turnosApi,
} from "../../services/adminService";
import '../../styles/estilos.css';

export default function AdminPanel() {
  const [tab, setTab] = useState("participantes");
  const [programas, setProgramas] = useState([]);
  const [edificios, setEdificios] = useState([]);

  useEffect(() => {
    const fetchProgramas = async () => {
      try {
        const res = await fetch('http://localhost:5000/api/auth/programas');
        const data = await res.json();
        setProgramas(data);
      } catch (err) {
        console.error('No se pudieron cargar los programas académicos', err);
      }
    };

    const fetchEdificios = async () => {            
      try {
        const res = await fetch('http://localhost:5000/api/admin/salas/edificios');
        const json = await res.json();
        if (json.success) {
          setEdificios(json.data);
        } else {
          console.error('Error al traer edificios:', json.message);
        }
      } catch (err) {
        console.error('No se pudieron cargar los edificios', err);
      }
    };

    fetchProgramas();
    fetchEdificios();                               
  }, []);

  // Transformar a formato options para CrudSection
  const programaOptions = programas.map((p) => ({
    value: p.nombre_programa,
    label: `${p.nombre_programa}${p.tipo ? ` (${p.tipo})` : ''}`,
  }));

  const edificioOptions = edificios.map((e) => ({
    value: e.nombre_edificio,
    label: e.nombre_edificio,
  }))

  return (
    <div className="container py-4">
      <h2 className="mb-4" style={{color: '#E6F0FA'}}>Panel de Administración</h2>

      <ul className="nav nav-tabs mb-4" style={{borderBottom: '2px solid #E6F0FA'}}>
        <li className="nav-item">
          <button
            className={`nav-link ${tab === "participantes" ? "active" : ""}`}
            onClick={() => setTab("participantes")}
            style={tab === "participantes" ? {backgroundColor: '#0056A6', color: '#E6F0FA'} : {color: '#E6F0FA'}}
          >
            Participantes
          </button>
        </li>

        <li className="nav-item">
          <button
            className={`nav-link ${tab === "salas" ? "active" : ""}`}
            onClick={() => setTab("salas")}
            style={tab === "salas" ? {backgroundColor: '#0056A6', color: '#E6F0FA'} : {color: '#E6F0FA'}}
          >
            Salas
          </button>
        </li>

        <li className="nav-item">
          <button
            className={`nav-link ${tab === "reservas" ? "active" : ""}`}
            onClick={() => setTab("reservas")}
            style={tab === "reservas" ? {backgroundColor: '#0056A6', color: '#E6F0FA'} : {color: '#E6F0FA'}}
          >
            Reservas
          </button>
        </li>

        <li className="nav-item">
          <button
            className={`nav-link ${tab === "sanciones" ? "active" : ""}`}
            onClick={() => setTab("sanciones")}
            style={tab === "sanciones" ? {backgroundColor: '#0056A6', color: '#E6F0FA'} : {color: '#E6F0FA'}}
          >
            Sanciones
          </button>
        </li>

        <li className="nav-item">
          <button
            className={`nav-link ${tab === "turnos" ? "active" : ""}`}
            onClick={() => setTab("turnos")}
            style={tab === "turnos" ? {backgroundColor: '#0056A6', color: '#E6F0FA'} : {color: '#E6F0FA'}}
          >
            Turnos
          </button>
        </li>
      </ul>

      {/* PARTICIPANTES */}
      {tab === "participantes" && (
        <CrudSection
          title="ABM de participantes"
          api={participantesApi}
          columns={[
            { header: "CI", field: "ci" },
            { header: "Nombre", field: "nombre" },
            { header: "Apellido", field: "apellido" },
            { header: "Email", field: "email" },
            {
              header: "Rol Sistema",
              field: "rol_sistema",
              render: (val) => (
                <span className={`badge ${val === "admin" ? "bg-danger" : "bg-secondary"}`}>
                  {val}
                </span>
              )
            },
            {
              header: "Rol Académico",
              field: "rol_academico",
              render: (val) => (
                <span className={`badge ${val === "docente" ? "bg-primary" : "bg-info"}`}>
                  {val || 'Sin asignar'}
                </span>
              )
            },
            { header: "Programa", field: "nombre_programa" }
          ]}
          formFields={[
            { name: "ci", label: "CI", type: "text", readOnlyInEdit: true },
            { name: "nombre", label: "Nombre", type: "text" },
            { name: "apellido", label: "Apellido", type: "text" },
            { name: "email", label: "Email", type: "email" },

            {
              name: "rol_sistema",
              label: "Rol del Sistema (Acceso Panel)",
              type: "select",
              options: [
                { value: "usuario", label: "Usuario" },
                { value: "admin", label: "Administrador" }
              ]
            },

            {
              name: "rol_academico",
              label: "Rol Académico (Alumno/Docente)",
              type: "select",
              options: [
                { value: "alumno", label: "Alumno" },
                { value: "docente", label: "Docente" }
              ]
            },

            {
              name: "nombre_programa",
              label: "Programa Académico",
              type: "select",
              options: programaOptions,
              required: true
            },

            {
              name: "password",
              label: "Password (solo alta / cambio)",
              type: "password",
              required: true,
            },
          ]}
        />
      )}

      {/* SALAS */}
      {tab === "salas" && (
        <CrudSection
          title="ABM de salas"
          api={salasApi}
          columns={[
            { header: "Sala", field: "nombre_sala" },
            { header: "Edificio", field: "edificio" },
            { header: "Capacidad", field: "capacidad" },
            { header: "Tipo", field: "tipo_sala" },
          ]}
          formFields={[
            { name: "nombre_sala", label: "Nombre sala", type: "text", readOnlyInEdit: true },
            { name: "edificio", label: "Edificio", type: "select", readOnlyInEdit: false, options: edificioOptions },
            { name: "capacidad", label: "Capacidad", type: "number" },
            {
              name: "tipo_sala",
              label: "Tipo de sala",
              type: "select",
              options: [
                { value: "libre", label: "Libre" },
                { value: "docente", label: "Docente" },
                { value: "posgrado", label: "Posgrado" }
              ]
            },
          ]}
        />
      )}

      {/* RESERVAS */}
      {tab === "reservas" && (
        <CrudSection
          title="ABM de reservas"
          api={reservasApi}
          columns={[
            { header: "ID", field: "id_reserva" },
            { header: "Sala", field: "nombre_sala" },
            { header: "Edificio", field: "edificio" },
            { header: "Fecha", field: "fecha" },
            { header: "Turno", field: "id_turno" },
            { header: "Inicio", field: "hora_inicio" },
            { header: "Fin", field: "hora_fin" },
            { header: "Estado", field: "estado" },
            { header: "CI", field: "ci_participante" },
          ]}
          formFields={[
            { name: "id_reserva", label: "ID", type: "text", readOnlyInEdit: true },
            {
              name: "estado",
              label: "Estado",
              type: "select",
              options: [
                { value: "activa", label: "Activa" },
                { value: "cancelada", label: "Cancelada" },
                { value: "sin asistencia", label: "Sin asistencia" },
                { value: "finalizada", label: "Finalizada" },
              ]
            }
          ]}
          hideCreate={true}
        />
      )}

      {/* SANCIONES */}
      {tab === "sanciones" && (
        <CrudSection
          title="ABM de sanciones"
          api={sancionesApi}
          columns={[
            { header: "CI", field: "ci_participante" },
            { header: "Nombre", field: "nombre" },
            { header: "Apellido", field: "apellido" },
            { header: "Inicio", field: "fecha_inicio" },
            { header: "Fin", field: "fecha_fin" },
          ]}
          formFields={[
            { name: "ci_participante", label: "CI participante", type: "number", readOnlyInEdit: true },
            { name: "fecha_inicio", label: "Inicio", type: "date" },
            { name: "fecha_fin", label: "Fin", type: "date" },
          ]}
        />
      )}

      {/* TURNOS */}
      {tab === "turnos" && (
        <CrudSection
          title="ABM de turnos"
          api={turnosApi}
          columns={[
            { header: "ID", field: "id_turno" },
            { header: "Inicio", field: "hora_inicio" },
            { header: "Fin", field: "hora_fin" },
          ]}
          formFields={[
            { name: "id_turno", label: "ID", type: "number", readOnlyInEdit: true },
            { name: "hora_inicio", label: "Inicio", type: "time" },
            { name: "hora_fin", label: "Fin", type: "time" },
          ]}
        />
      )}

    </div>
  );
}