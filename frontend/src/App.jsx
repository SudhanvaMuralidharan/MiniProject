import { useEffect, useState } from 'react'
import { fetchMeta } from './api.js'
import { useSimulation } from './useSimulation.js'
import Controls from './components/Controls.jsx'
import KpiCards from './components/KpiCards.jsx'
import RegionMap from './components/RegionMap.jsx'
import FirmTable from './components/FirmTable.jsx'
import Recommendations from './components/Recommendations.jsx'
import Reskilling from './components/Reskilling.jsx'

export default function App() {
  const [meta, setMeta] = useState(null)
  const [params, setParams] = useState({ hazard: 'flood', region: 'Kochi', severity: 0.7, boost: 0 })
  const { data, error, loading } = useSimulation(params)

  useEffect(() => {
    fetchMeta().then(setMeta).catch(() => {})
  }, [])

  return (
    <>
      <header>
        <h1>Resilient<span>Chain</span></h1>
        <p>
          Stress-test a regional MSME manufacturing network against climate and logistics shocks.
          See jobs at risk, what supplier rebalancing and digital adoption save, and the reskilling
          pathways that make jobs future-ready.
        </p>
      </header>

      {meta && <Controls meta={meta} params={params} onChange={setParams} />}
      {error && <div className="error">Could not reach the API: {error}. Is the backend running on port 8000?</div>}

      {data && (
        <main className={loading ? 'loading' : ''}>
          <KpiCards totals={data.totals} scenario={data.scenario} />
          <div className="panels">
            <RegionMap regions={data.regions} />
            <FirmTable firms={data.firms} />
            <Recommendations items={data.recommendations} />
            <Reskilling items={data.reskilling} />
          </div>
        </main>
      )}
      {!data && !error && <p className="mute pad">Loading simulation…</p>}
    </>
  )
}
