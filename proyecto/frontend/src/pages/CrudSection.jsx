import { useEffect, useState } from "react";

/**
 * title: string
 * api: { fetchAll, create, update, remove }  -> funciones que devuelven Promise(axiosResponse)
 * columns: [{ header, field, render? }]
 * formFields: [
 *    { name, label, type, options?, defaultValue?, readOnlyInEdit?, required? }
 * ]
 */
export default function CrudSection({ title, api, columns, formFields }) {
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
    return <p>Cargando {title.toLowerCase()}...</p>;
  }

  return (
    <div className="card mb-4">
      <div className="card-body">
        <h4 className="mb-3">{title}</h4>

        {/* FORM */}
        <form onSubmit={handleSubmit}>
          <div className="row g-3">
            {formFields.map((field) => (
              <div className="col-md-3" key={field.name}>
                <label className="form-label">{field.label}</label>
                {field.type === "select" ? (
                  <select
                    className="form-select"
                    value={formData[field.name]}
                    onChange={(e) => handleChange(field.name, e.target.value)}
                    required={field.required !== false}
                    disabled={editMode && field.readOnlyInEdit}
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
                  />
                )}
              </div>
            ))}
          </div>

          <button type="submit" className="btn btn-primary mt-3">
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

        {/* TABLA */}
        <hr className="my-4" />
        <div className="table-responsive">
          <table className="table table-striped table-hover">
            <thead>
              <tr>
                {columns.map((col) => (
                  <th key={col.field}>{col.header}</th>
                ))}
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, idx) => (
                <tr key={idx}>
                  {columns.map((col) => (
                    <td key={col.field}>
                      {col.render ? col.render(row[col.field], row) : row[col.field]}
                    </td>
                  ))}
                  <td>
                    <button
                      className="btn btn-sm btn-warning me-2"
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
                  <td colSpan={columns.length + 1} className="text-center text-muted">
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
