export default function FirmTable({ firms }) {
  return (
    <section className="card">
      <h2>Firms ranked by jobs at risk</h2>
      <table>
        <thead>
          <tr><th>Firm</th><th>Score</th><th>Output loss</th><th>Jobs at risk</th></tr>
        </thead>
        <tbody>
          {firms.map((f) => (
            <tr key={f.id}>
              <td>
                {f.name}
                <div className="mute sub">{f.sector} · {f.region}</div>
              </td>
              <td>{f.score}</td>
              <td>
                <div className="bar" title={`${f.output_loss_pct}% → ${f.output_loss_mitigated_pct}%`}>
                  <i style={{ width: `${f.output_loss_pct}%` }} />
                  <b style={{ width: `${f.output_loss_mitigated_pct}%` }} />
                </div>
              </td>
              <td><span className="bad">{f.jobs_at_risk}</span> → <span className="good">{f.jobs_at_risk_mitigated}</span></td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}
