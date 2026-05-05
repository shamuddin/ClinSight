import { SafetyFlag, QualityGate, PediatricGate } from '../types'

export default function SafetyPanel({
  flags,
  qualityGate,
  pediatricGate,
}: {
  flags: SafetyFlag[]
  qualityGate: QualityGate
  pediatricGate: PediatricGate
}) {
  const sevClass = (s: string) =>
    s === 'HIGH' || s === 'CRITICAL' ? 'badge-critical' : s === 'MEDIUM' ? 'badge-warning' : 'badge-abnormal'

  return (
    <div className="panel">
      <h2>Safety Review ({flags.length})</h2>

      <div className="safety-subsection">
        <strong>Quality Gate:</strong>{' '}
        {qualityGate.pass ? (
          <span className="badge badge-pass">PASS</span>
        ) : (
          <span className="badge badge-critical">FAIL</span>
        )}
        {qualityGate.reasons?.map((r) => (
          <span key={r} className="dim"> {r}</span>
        ))}
      </div>

      <div className="safety-subsection">
        <strong>Pediatric Gate:</strong>{' '}
        <span className={`badge ${pediatricGate.status === 'PASS' ? 'badge-pass' : 'badge-warning'}`}>
          {pediatricGate.status}
        </span>
        {pediatricGate.message && <span className="dim"> {pediatricGate.message}</span>}
      </div>

      {flags.length === 0 ? (
        <p className="dim">No safety flags.</p>
      ) : (
        <ul className="flag-list">
          {flags.map((f, i) => (
            <li key={i} className="flag-item">
              <span className={`badge ${sevClass(f.severity)}`}>{f.severity}</span>
              <strong>{f.rule}</strong>
              <div className="flag-msg">{f.message}</div>
              {f.confidence_penalty && (
                <div className="dim">Confidence penalty: {(f.confidence_penalty * 100).toFixed(0)}%</div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
