import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 10000,
})

/** Mensaje legible a partir de un error de Axios (detail de FastAPI si existe). */
export function errorMessage(err) {
  const detail = err.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map((d) => d.msg).join('; ')
  if (err.code === 'ECONNABORTED') return 'La API tardó demasiado en responder'
  if (!err.response) return 'No se pudo conectar con la API'
  return `Error ${err.response.status}`
}

// `signal` permite cancelar la petición si el usuario cambia el filtro antes de que responda.
export const getMakes = (signal) => api.get('/vehicles/makes', { signal }).then((r) => r.data)

export const getModels = (make, signal) =>
  api.get('/vehicles/models', { params: { make }, signal }).then((r) => r.data)

export const getYears = (make, model, signal) =>
  api.get('/vehicles/years', { params: { make, model }, signal }).then((r) => r.data)

export const getCategories = (signal) => api.get('/parts/categories', { signal }).then((r) => r.data)

export const searchParts = (params, signal) =>
  api.get('/search/parts', { params: { limit: 200, ...params }, signal }).then((r) => r.data)

export const getPartBySku = (sku, signal) =>
  api.get(`/parts/sku/${encodeURIComponent(sku)}`, { signal }).then((r) => r.data)

export const searchVehicles = (sku, signal) =>
  api.get('/search/vehicles', { params: { sku, limit: 200 }, signal }).then((r) => r.data)
