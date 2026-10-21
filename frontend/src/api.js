async function getJson(url, signal) {
  const res = await fetch(url, { signal })
  if (!res.ok) throw new Error(`Request failed (${res.status})`)
  return res.json()
}

export const fetchMeta = (signal) => getJson('/api/meta', signal)

export const fetchSimulation = ({ hazard, region, severity, boost }, signal) =>
  getJson('/api/simulate?' + new URLSearchParams({ hazard, region, severity, boost }), signal)
