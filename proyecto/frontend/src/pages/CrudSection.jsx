import { useEffect, useState } from "react";
import '../styles/estilos.css';

export default function CrudSection({ title, api, columns, formFields, onEdit, hideCreate }) {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editMode, setEditMode] = useState(false);
  const [error, setError] = useState(null);

  const initialForm = () =>
    formFields.reduce(
      (acc, f) => ({ ...acc, [f.name]: f.defaultValue ?? "" }),
      {}
    );

  const [formData, setFormData] = useState(initialForm);

  const resetForm = () => {
    setFormData(initialForm());
    setEditMode(false);
    setError(null);
  };

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.fetchAll();
      // asumo respuesta { success, data }
      setRows(res.data.data || []);
    } catch (e) {
      console.error(e);
      setError("Error al cargar datos");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleChange = (name, value) => {
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      if (editMode) {
        await api.update(formData);
      } else {
        await api.create(formData);
      }
      resetForm();
      loadData();
    } catch (e) {
      console.error(e);
      const msg = e.response?.data?.message || "Error al guardar";
      setError(msg);
    }
  };

  const handleEdit = (row) => {
    // Llamar callback opcional antes de editar (para PK compuestas)
    if (onEdit) {
      onEdit(row);
    }
    const data = {};
    formFields.forEach((f) => {
      data[f.name] = row[f.name] ?? "";
    });
    setFormData(data);
    setEditMode(true);
  };

  const handleDelete = async (row) => {
    if (!window.confirm("¿Seguro que querés eliminar este registro?")) return;
    setError(null);
    try {
      await api.remove(row);
      loadData();
    } catch (e) {
      console.error(e);
      const msg = e.response?.data?.message || "Error al eliminar";
      setError(msg);
    }
  };

  if (loading) {
    return <p style={{color: '#E6F0FA'}}>Cargando {title.toLowerCase()}...</p>;
  }

  return (
    <div className="card mb-4 shadow" style={{backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid #0056A6'}}>
      <div className="card-body">
        {title && <h4 className="mb-3" style={{color: '#003366'}}>{title}</h4>}

        {/* FORM - solo mostrar si no está hideCreate O si está en editMode */}
        {(!hideCreate || editMode) && (
          <form onSubmit={handleSubmit}>
            <div className="row g-3">
              {formFields.map((field) => (
                <div className="col-md-3" key={field.name}>
                  <label className="form-label fw-bold" style={{color: '#003366'}}>{field.label}</label>
                  {field.type === "select" ? (
                    <select
                      className="form-select"
                      value={formData[field.name]}
                      onChange={(e) => handleChange(field.name, e.target.value)}
                      required={field.required !== false}
                      disabled={editMode && field.readOnlyInEdit}
                      style={{borderColor: '#0056A6'}}
                    >
                      <option value="">Seleccionar...</option>
                      {field.options?.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <input
                      type={field.type || "text"}
                      className="form-control"
                      value={formData[field.name]}
                      onChange={(e) => handleChange(field.name, e.target.value)}
                      required={field.required !== false}
                      disabled={editMode && field.readOnlyInEdit}
                      style={{borderColor: '#0056A6'}}
                    />
                  )}
                </div>
              ))}
            </div>

            <button type="submit" className="btn mt-3" style={{backgroundColor: '#0056A6', color: 'white', borderColor: '#003366'}}>
              {editMode ? "Guardar cambios" : "Crear"}
            </button>
            {editMode && (
              <button
                type="button"
                className="btn btn-secondary mt-3 ms-2"
                onClick={resetForm}
              >
                Cancelar
              </button>
            )}

            {error && <div className="alert alert-danger mt-3">{error}</div>}
          </form>
        )}

        {/* TABLA */}
        <hr className="my-4" style={{borderColor: '#0056A6'}} />
        <div className="table-responsive">
          <table className="table table-striped table-hover">
            <thead>
              <tr style={{backgroundColor: '#003366'}}>
                {columns.map((col) => (
                  <th key={col.field} className="fw-bold" style={{color: '#E6F0FA', backgroundColor: '#003366'}}>{col.header}</th>
                ))}
                <th className="fw-bold" style={{color: '#E6F0FA', backgroundColor: '#003366'}}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, idx) => (
                <tr key={idx}>
                  {columns.map((col) => (
                    <td key={col.field} style={{color: '#333'}}>
                      {col.render ? col.render(row[col.field], row) : row[col.field]}
                    </td>
                  ))}
                  <td>
                    <button
                      className="btn btn-sm me-2"
                      style={{backgroundColor: '#0056A6', color: 'white'}}
                      onClick={() => handleEdit(row)}
                    >
                      Editar
                    </button>
                    <button
                      className="btn btn-sm btn-danger"
                      onClick={() => handleDelete(row)}
                    >
                      Eliminar
                    </button>
                  </td>
                </tr>
              ))}
              {rows.length === 0 && (
                <tr>
                  <td colSpan={columns.length + 1} className="text-center" style={{color: '#666'}}>
                    No hay registros.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
