import { useEffect, useState } from 'react'
import axios from 'axios'
import {
  errorMessage,
  getCategories,
  getMakes,
  getModels,
  getYears,
  searchParts,
} from '../api/client'

/**
 * Carga datos cuando cambian las dependencias y cancela la petición anterior,
 * para que una respuesta lenta no pise a una más reciente.
 * `load` devuelve una promesa, o null si aún faltan datos para consultar.
 */
function useApi(load, deps, initial) {
  const [state, setState] = useState({ data: initial, loading: false, error: null })

  useEffect(() => {
    const controller = new AbortController()
    const promise = load(controller.signal)
    if (!promise) {
      setState({ data: initial, loading: false, error: null })
      return
    }
    setState((s) => ({ ...s, loading: true, error: null }))
    promise
      .then((data) => setState({ data, loading: false, error: null }))
      .catch((err) => {
        if (axios.isCancel(err)) return
        setState({ data: initial, loading: false, error: errorMessage(err) })
      })
    return () => controller.abort()
  }, deps)

  return state
}

export default function VehiclePartsFinder() {
  const [make, setMake] = useState('')
  const [model, setModel] = useState('')
  const [year, setYear] = useState('')
  const [category, setCategory] = useState('')

  const makes = useApi((s) => getMakes(s), [], [])
  const models = useApi((s) => (make ? getModels(make, s) : null), [make], [])
  const years = useApi((s) => (make && model ? getYears(make, model, s) : null), [make, model], [])
  const categories = useApi((s) => getCategories(s), [], [])
  const parts = useApi(
    (s) =>
      make && model && year
        ? searchParts({ make, model, year, ...(category && { category }) }, s)
        : null,
    [make, model, year, category],
    null,
  )

  // Al cambiar un nivel, se limpian los que dependen de él.
  const onMake = (e) => { setMake(e.target.value); setModel(''); setYear('') }
  const onModel = (e) => { setModel(e.target.value); setYear('') }

  const error = makes.error || models.error || years.error || categories.error || parts.error

  return (
    <section className="card">
      <h2>Partes por vehículo</h2>

      <div className="filters">
        <label>
          Marca
          <select value={make} onChange={onMake} disabled={makes.loading}>
            <option value="">Selecciona…</option>
            {makes.data.map((m) => <option key={m}>{m}</option>)}
          </select>
        </label>

        <label>
          Modelo
          <select value={model} onChange={onModel} disabled={!make || models.loading}>
            <option value="">Selecciona…</option>
            {models.data.map((m) => <option key={m}>{m}</option>)}
          </select>
        </label>

        <label>
          Año
          <select value={year} onChange={(e) => setYear(e.target.value)} disabled={!model || years.loading}>
            <option value="">Selecciona…</option>
            {years.data.map((y) => <option key={y}>{y}</option>)}
          </select>
        </label>

        <label>
          Categoría
          <select value={category} onChange={(e) => setCategory(e.target.value)}>
            <option value="">Todas</option>
            {categories.data.map((c) => <option key={c}>{c}</option>)}
          </select>
        </label>
      </div>

      {error && <p className="error">{error}</p>}
      {!year && !error && <p className="hint">Elige marca, modelo y año para ver las partes compatibles.</p>}
      {parts.loading && <p className="hint">Buscando…</p>}

      {parts.data && !parts.loading && (
        parts.data.total === 0 ? (
          <p className="hint">No hay partes registradas para {make} {model} {year}.</p>
        ) : (
          <>
            <p className="hint">
              {parts.data.total} parte{parts.data.total === 1 ? '' : 's'} compatible
              {parts.data.total === 1 ? '' : 's'} con {make} {model} {year}
            </p>
            <table>
              <thead>
                <tr><th>SKU</th><th>Nombre</th><th>Categoría</th><th>Fabricante</th><th>Notas</th></tr>
              </thead>
              <tbody>
                {parts.data.items.map((p) => (
                  <tr key={p.id}>
                    <td className="mono">{p.sku}</td>
                    <td>{p.name}</td>
                    <td>{p.category}</td>
                    <td>{p.manufacturer}</td>
                    <td>{p.notes ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )
      )}
    </section>
  )
}
