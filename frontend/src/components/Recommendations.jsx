export default function Recommendations({ items }) {
  return (
    <section className="card">
      <h2>Recommended supplier rebalancing</h2>
      <ul>
        {items.length === 0 && <li className="mute">No supplier is materially affected. Try a higher severity.</li>}
        {items.map((m, i) => (
          <li key={i}>
            <b>{m.firm}</b>: shift {m.shift_pct}% of <i>{m.input}</i> from {m.from_region} ({m.from_supplier})
            {' '}to {m.to_region} ({m.to_supplier}, {m.lead_days}-day lead)
          </li>
        ))}
      </ul>
    </section>
  )
}
