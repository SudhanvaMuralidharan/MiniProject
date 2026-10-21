import { useMemo } from 'react'

const ringColour = (d) => (d >= 0.7 ? '#3ddc97' : d >= 0.6 ? '#8fd16a' : '#ffb454')

export default function RegionMap({ regions }) {
  const project = useMemo(() => {
    const lats = regions.map((r) => r.lat), lons = regions.map((r) => r.lon)
    const [minLat, maxLat, minLon, maxLon] = [Math.min(...lats), Math.max(...lats), Math.min(...lons), Math.max(...lons)]
    return {
      x: (lon) => 30 + ((lon - minLon) / (maxLon - minLon)) * 340,
      y: (lat) => 390 - ((lat - minLat) / (maxLat - minLat)) * 360,
    }
  }, [regions])

  return (
    <section className="card">
      <h2>Regional impact map</h2>
      <svg viewBox="0 0 400 420" role="img" aria-label="Impact by region">
        {regions.map((r) => {
          const rad = 8 + r.impact * 34
          const cx = project.x(r.lon), cy = project.y(r.lat)
          return (
            <g key={r.name}>
              <circle cx={cx} cy={cy} r={rad} fill={`rgba(255,93,108,${0.15 + r.impact * 0.6})`}
                      stroke={ringColour(r.digital)} strokeWidth="3" />
              <text x={cx} y={cy + rad + 12} fill="#cfd9e2" fontSize="11" textAnchor="middle">
                {r.name} {Math.round(r.impact * 100)}%
              </text>
            </g>
          )
        })}
      </svg>
      <div className="mute note">Circle size = shock impact. Ring colour = digital readiness (green high, amber low).</div>
    </section>
  )
}
