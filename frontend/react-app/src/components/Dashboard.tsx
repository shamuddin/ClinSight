import { DemoCase } from '../types'

export default function Dashboard({
  cases,
  onSelect,
  activeCaseId,
}: {
  cases: DemoCase[]
  onSelect: (id: string) => void
  activeCaseId?: string
}) {
  if (cases.length === 0) {
    return <p className="sidebar-empty dim">Waiting for backend on :8000…</p>
  }

  return (
    <div className="case-list">
      {cases.map((c, i) => (
        <button
          key={c.case_id}
          className={`case-card${activeCaseId === c.case_id ? ' case-card--active' : ''}`}
          onClick={() => onSelect(c.case_id)}
          title={`Press ${i + 1} to load`}
        >
          <div className="case-id">{c.case_id}</div>
          <div className="case-meta">
            {c.patient_age}yo {c.patient_sex} — {c.chief_complaint}
          </div>
          <div className="case-vitals mono">
            BP {String(c.vitals.bp ?? '—')} · HR {String(c.vitals.hr ?? '—')} · SpO₂ {String(c.vitals.spo2 ?? '—')}%
          </div>
        </button>
      ))}
    </div>
  )
}
