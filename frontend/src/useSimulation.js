import { useEffect, useState } from 'react'
import { fetchSimulation } from './api.js'

/** Debounced, cancellable simulation fetch. Re-runs whenever params change. */
export function useSimulation(params) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const { hazard, region, severity, boost } = params

  useEffect(() => {
    const controller = new AbortController()
    setLoading(true)
    const timer = setTimeout(() => {
      fetchSimulation({ hazard, region, severity, boost }, controller.signal)
        .then((d) => { setData(d); setError(null) })
        .catch((e) => { if (e.name !== 'AbortError') setError(e.message) })
        .finally(() => { if (!controller.signal.aborted) setLoading(false) })
    }, 150)
    return () => { clearTimeout(timer); controller.abort() }
  }, [hazard, region, severity, boost])

  return { data, error, loading }
}
