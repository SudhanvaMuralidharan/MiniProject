export default function Reskilling({ items }) {
  return (
    <section className="card">
      <h2>Reskilling pathways for affected workers</h2>
      <ul>
        {items.length === 0 && <li className="mute">No residual job risk after mitigation.</li>}
        {items.map((r) => (
          <li key={r.sector}>
            <b>{r.workers} workers</b> in {r.sector} → {r.role} <span className="mute">({r.weeks}-week programme)</span>
          </li>
        ))}
      </ul>
    </section>
  )
}
