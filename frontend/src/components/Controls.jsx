export default function Controls({ meta, params, onChange }) {
  const set = (patch) => onChange({ ...params, ...patch })
  return (
    <div className="controls">
      <label>
        Shock
        <select value={params.hazard} onChange={(e) => set({ hazard: e.target.value })}>
          {Object.entries(meta.hazards).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
      </label>
      <label>
        Epicentre
        <select value={params.region} onChange={(e) => set({ region: e.target.value })}>
          {meta.regions.map((r) => <option key={r}>{r}</option>)}
        </select>
      </label>
      <label>
        Severity: {Math.round(params.severity * 100)}%
        <input type="range" min="0" max="100" value={Math.round(params.severity * 100)}
               onChange={(e) => set({ severity: e.target.value / 100 })} />
      </label>
      <label>
        Digital adoption uplift: +{Math.round(params.boost * 100)} pts
        <input type="range" min="0" max="40" value={Math.round(params.boost * 100)}
               onChange={(e) => set({ boost: e.target.value / 100 })} />
      </label>
    </div>
  )
}
