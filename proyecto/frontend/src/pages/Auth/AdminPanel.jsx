import { useState } from "react";
import CrudSection from '../CrudSection';
import {
  participantesApi,
  salasApi,
  reservasApi,
  sancionesApi,
} from "../../services/adminService";

export default function AdminPanel() {
  const [tab, setTab] = useState("participantes");

  return (
    <div className="container py-4">
      <h2 className="mb-4">Panel de Administración</h2>

      <ul className="nav nav-tabs mb-4">
        <li className="nav-item">
          <button
            className={`nav-link ${tab === "participantes" ? "active" : ""}`}
            onClick={() => setTab("participantes")}
          >
            Participantes
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link ${tab === "salas" ? "active" : ""}`}
            onClick={() => setTab("salas")}
          >
            Salas
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link ${tab === "reservas" ? "active" : ""}`}
            onClick={() => setTab("reservas")}
          >
            Reservas
          </button>
        </li>
        <li className="nav-item">
          <button
            className={`nav-link ${tab === "sanciones" ? "active" : ""}`}
            onClick={() => setTab("sanciones")}
          >
            Sanciones
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
        <CrudSection
          title="ABM de reservas"
          api={reservasApi}
          columns={[
            { header: "ID", field: "id_reserva" },
            { header: "Sala", field: "nombre_sala" },
            { header: "Edificio", field: "edificio" },
            { header: "Fecha", field: "fecha" },
            { header: "Inicio", field: "hora_inicio" },
            { header: "Fin", field: "hora_fin" },
            { header: "Estado", field: "estado" },
            { header: "CI", field: "ci" },
          ]}
          formFields={[
            {
              name: "id_reserva",
              label: "ID reserva",
              type: "number",
              readOnlyInEdit: true,
              required: false,
            },
            { name: "estado", label: "Estado", type: "text" },
          ]}
        />
      )}

      {tab === "sanciones" && (
        <CrudSection
          title="ABM de sanciones"
          api={sancionesApi}
          columns={[
            { header: "ID", field: "id_sancion" },
            { header: "CI participante", field: "ci_participante" },
            { header: "Inicio", field: "fecha_inicio" },
            { header: "Fin", field: "fecha_fin" },
          ]}
          formFields={[
            {
              name: "id_sancion",
              label: "ID sanción (solo editar)",
              type: "number",
              readOnlyInEdit: true,
              required: false,
            },
            { name: "ci_participante", label: "CI participante", type: "text" },
            { name: "fecha_inicio", label: "Fecha inicio", type: "date" },
            { name: "fecha_fin", label: "Fecha fin", type: "date" },
          ]}
        />
      )}
    </div>
  );
}
