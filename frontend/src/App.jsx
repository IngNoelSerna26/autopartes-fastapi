import { useState } from 'react'
import VehiclePartsFinder from './components/VehiclePartsFinder.jsx'
import PartVehiclesFinder from './components/PartVehiclesFinder.jsx'

const TABS = [
  { id: 'vehicle', label: 'Buscar por vehículo', Component: VehiclePartsFinder },
  { id: 'part', label: 'Buscar por autoparte', Component: PartVehiclesFinder },
]

export default function App() {
  const [tab, setTab] = useState('vehicle')

  return (
    <main>
      <header>
        <h1>Compatibilidad de autopartes</h1>
        <nav className="tabs">
          {TABS.map((t) => (
            <button
              key={t.id}
              className={tab === t.id ? 'active' : ''}
              onClick={() => setTab(t.id)}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </header>

      {/* Ambas vistas quedan montadas para conservar sus filtros al cambiar de pestaña. */}
      {TABS.map(({ id, Component }) => (
        <div key={id} hidden={tab !== id}>
          <Component />
        </div>
      ))}
    </main>
  )
}
