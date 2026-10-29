import { useState } from 'react'
import { errorMessage, getPartBySku, searchVehicles } from '../api/client'

export default function PartVehiclesFinder() {
  const [sku, setSku] = useState('')
  const [result, setResult] = useState(null) // { part, vehicles }
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function onSubmit(e) {
    e.preventDefault()
    const code = sku.trim()
    if (!code) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      // La parte primero: si el SKU no existe, la API responde 404 con un mensaje claro.
      const part = await getPartBySku(code)
      const vehicles = await searchVehicles(code)
      setResult({ part, vehicles })
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="card">
      <h2>Vehículos por autoparte</h2>

      <form className="filters" onSubmit={onSubmit}>
        <label className="grow">
          Código SKU
          <input value={sku} onChange={(e) => setSku(e.target.value)} placeholder="GAT-26600" />
        </label>
        <button type="submit" disabled={loading || !sku.trim()}>
          {loading ? 'Buscando…' : 'Buscar'}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <>
          <p className="hint">
            <strong>{result.part.name}</strong> · {result.part.manufacturer} · {result.part.category} —{' '}
            {result.vehicles.total === 0
              ? 'sin vehículos compatibles registrados'
              : `${result.vehicles.total} vehículo${result.vehicles.total === 1 ? '' : 's'} compatible${result.vehicles.total === 1 ? '' : 's'}`}
          </p>
          {result.vehicles.total > 0 && (
            <table>
              <thead>
                <tr><th>Marca</th><th>Modelo</th><th>Año</th><th>Motor</th><th>Versión</th><th>Notas</th></tr>
              </thead>
              <tbody>
                {result.vehicles.items.map((v) => (
                  <tr key={v.id}>
                    <td>{v.make}</td>
                    <td>{v.model}</td>
                    <td>{v.year}</td>
                    <td>{v.engine || '—'}</td>
                    <td>{v.trim || '—'}</td>
                    <td>{v.notes ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      )}
    </section>
  )
}
