import { useState } from "react";
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

  return (
    <div className="container py-4">
      <h2 className="mb-4" style={{color: '#E6F0FA'}}>Panel de Administración</h2>

      <ul className="nav nav-tabs mb-4" style={{borderBottom: '2px solid #E6F0FA'}}>
        <li className="nav-item">
          <button
            className={`nav-link ${tab === "participantes" ? "active" : ""}`}
            onClick={() => setTab("participantes")}
            style={tab === "participantes" ? {backgroundColor: '#0056A6', color: '#E6F0FA', borderColor: '#E6F0FA'} : {color: '#E6F0FA', backgroundColor: 'transparent', border: 'none'}}
          >
            Participantes
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link ${tab === "salas" ? "active" : ""}`}
            onClick={() => setTab("salas")}
            style={tab === "salas" ? {backgroundColor: '#0056A6', color: '#E6F0FA', borderColor: '#E6F0FA'} : {color: '#E6F0FA', backgroundColor: 'transparent', border: 'none'}}
          >
            Salas
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link ${tab === "reservas" ? "active" : ""}`}
            onClick={() => setTab("reservas")}
            style={tab === "reservas" ? {backgroundColor: '#0056A6', color: '#E6F0FA', borderColor: '#E6F0FA'} : {color: '#E6F0FA', backgroundColor: 'transparent', border: 'none'}}
          >
            Reservas
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link ${tab === "sanciones" ? "active" : ""}`}
            onClick={() => setTab("sanciones")}
            style={tab === "sanciones" ? {backgroundColor: '#0056A6', color: '#E6F0FA', borderColor: '#E6F0FA'} : {color: '#E6F0FA', backgroundColor: 'transparent', border: 'none'}}
          >
            Sanciones
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link ${tab === "turnos" ? "active" : ""}`}
            onClick={() => setTab("turnos")}
            style={tab === "turnos" ? {backgroundColor: '#0056A6', color: '#E6F0FA', borderColor: '#E6F0FA'} : {color: '#E6F0FA', backgroundColor: 'transparent', border: 'none'}}
          >
            Turnos
          </button>
        </li>
      </ul>

      {tab === "participantes" && (
        <CrudSection
          title="ABM de participantes"
          api={participantesApi}
          columns={[
            { header: "CI", field: "ci" },
            { header: "Nombre", field: "nombre" },
            { header: "Apellido", field: "apellido" },
            { header: "Email", field: "email" },
            { header: "Rol", field: "rol" },
          ]}
          formFields={[
            { name: "ci", label: "CI", type: "text", readOnlyInEdit: true },
            { name: "nombre", label: "Nombre", type: "text" },
            { name: "apellido", label: "Apellido", type: "text" },
            { name: "email", label: "Email", type: "email" },
            {
              name: "rol",
              label: "Rol",
              type: "select",
              options: [
                { value: "alumno", label: "Alumno" },
                { value: "docente", label: "Docente" },
                { value: "admin", label: "Admin" },
              ],
            },
            {
              name: "password",
              label: "Password (solo alta / cambio)",
              type: "password",
              required: false,
            },
          ]}
        />
      )}

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
            {
              name: "nombre_sala",
              label: "Nombre de sala",
              type: "text",
              readOnlyInEdit: true,
            },
            {
              name: "edificio",
              label: "Edificio",
              type: "text",
              readOnlyInEdit: true,
            },
            { name: "capacidad", label: "Capacidad", type: "number" },
            {
              name: "tipo_sala",
              label: "Tipo de sala",
              type: "select",
              options: [
                { value: "libre", label: "Libre" },
                { value: "posgrado", label: "Posgrado" },
                { value: "docente", label: "Docente" },
              ],
            },
          ]}
        />
      )}

      {tab === "reservas" && (
        <div className="card mb-4 shadow" style={{backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid #0056A6'}}>
          <div className="card-body">
            <h4 className="mb-3" style={{color: '#003366'}}>ABM de reservas</h4>
            <p style={{color: '#666'}}>
              Nota: Para crear reservas, los usuarios deben hacerlo desde su panel.
              Aquí solo puedes modificar el estado o eliminar reservas existentes.
            </p>
            <CrudSection
              title=""
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
                { header: "Participante", field: "nombre", render: (_, row) => `${row.nombre} ${row.apellido}` },
              ]}
              formFields={[
                {
                  name: "id_reserva",
                  label: "ID reserva (solo lectura)",
                  type: "number",
                  readOnlyInEdit: true,
                  required: false,
                },
                {
                  name: "estado",
                  label: "Estado",
                  type: "select",
                  options: [
                    { value: "activa", label: "Activa" },
                    { value: "cancelada", label: "Cancelada" },
                    { value: "cancelada_admin", label: "Cancelada por Admin" },
                  ],
                },
              ]}
              hideCreate={true}
            />
          </div>
        </div>
      )}

      {tab === "sanciones" && (
        <CrudSection
          title="ABM de sanciones"
          api={sancionesApi}
          columns={[
            { header: "CI participante", field: "ci_participante" },
            { header: "Nombre", field: "nombre" },
            { header: "Apellido", field: "apellido" },
            { header: "Fecha inicio", field: "fecha_inicio" },
            { header: "Fecha fin", field: "fecha_fin" },
          ]}
          formFields={[
            { name: "ci_participante", label: "CI participante", type: "number", readOnlyInEdit: true },
            { name: "fecha_inicio", label: "Fecha inicio", type: "date" },
            { name: "fecha_fin", label: "Fecha fin", type: "date" },
          ]}
          onEdit={(row) => sancionesApi.setOriginal(row)}
        />
      )}

      {tab === "turnos" && (
        <CrudSection
          title="ABM de turnos"
          api={turnosApi}
          columns={[
            { header: "ID", field: "id_turno" },
            { header: "Hora inicio", field: "hora_inicio" },
            { header: "Hora fin", field: "hora_fin" },
          ]}
          formFields={[
            {
              name: "id_turno",
              label: "ID turno (solo editar)",
              type: "number",
              readOnlyInEdit: true,
              required: false,
            },
            { name: "hora_inicio", label: "Hora inicio (HH:MM)", type: "time" },
            { name: "hora_fin", label: "Hora fin (HH:MM)", type: "time" },
          ]}
        />
      )}
    </div>
  );
}
