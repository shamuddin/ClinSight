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
  return (
    <div className="panel dashboard-panel">
      <h2>Case Dashboard</h2>
      {cases.length === 0 ? (
        <p className="dim">No cases loaded — ensure backend is running on :8000</p>
      ) : (
        <div className="case-grid">
          {cases.map((c) => (
            <button
              key={c.case_id}
              className={`case-card ${activeCaseId === c.case_id ? 'active' : ''}`}
              onClick={() => onSelect(c.case_id)}
            >
              <div className="case-id">{c.case_id}</div>
              <div className="case-meta">{c.patient_age}yo {c.patient_sex} — {c.chief_complaint}</div>
              <div className="case-vitals">
                BP {c.vitals.bp} · HR {c.vitals.hr} · SpO₂ {c.vitals.spo2}%
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
