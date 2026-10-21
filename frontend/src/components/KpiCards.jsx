export default function KpiCards({ totals: t, scenario }) {
  const saved = t.jobs_unmitigated - t.jobs_mitigated
  return (
    <div className="grid">
      <div className="card kpi">
        <div className="s">Jobs at risk (no action)</div>
        <div className="v bad">{t.jobs_unmitigated.toLocaleString()}</div>
        <div className="s">of {t.total_jobs.toLocaleString()} workers · {scenario.duration_days}-day disruption</div>
      </div>
      <div className="card kpi">
        <div className="s">Jobs at risk (after rebalancing)</div>
        <div className="v good">{t.jobs_mitigated.toLocaleString()}</div>
        <div className="s">{saved.toLocaleString()} jobs protected</div>
      </div>
      <div className="card kpi">
        <div className="s">Revenue at risk</div>
        <div className="v">₹{t.rev_unmitigated_cr} cr</div>
        <div className="s">₹{t.rev_mitigated_cr} cr after mitigation</div>
      </div>
      <div className="card kpi">
        <div className="s">Network resilience score</div>
        <div className="v">{t.avg_resilience}<span className="s"> / 100</span></div>
        <div className="s">structural, before the shock</div>
      </div>
    </div>
  )
}
