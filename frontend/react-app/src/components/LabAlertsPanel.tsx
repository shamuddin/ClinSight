import { LabAlert } from '../types'

export default function LabAlertsPanel({
  alerts,
  patterns,
  labs,
  units,
}: {
  alerts: LabAlert[]
  patterns: string[]
  labs: Record<string, number>
  units: Record<string, string>
}) {
  const severityClass = (s: string) =>
    s === 'CRITICAL' ? 'badge-critical' : 'badge-abnormal'

  return (
    <div className="panel">
      <h2>Lab Alerts ({alerts.length})</h2>
      {alerts.length === 0 ? (
        <p className="dim">No critical or abnormal lab values.</p>
      ) : (
        <ul className="lab-list">
          {alerts.map((a, i) => (
            <li key={i} className="lab-item">
              <span className={`badge ${severityClass(a.severity)}`}>{a.severity}</span>
              <strong>{a.code}</strong>
              <span>
                {a.lab}: {a.value} {a.unit} (threshold: {a.threshold})
              </span>
              <span className="dim">{a.description}</span>
            </li>
          ))}
        </ul>
      )}
      {patterns.length > 0 && (
        <div className="pattern-box">
          <strong>Patterns detected:</strong>{' '}
          {patterns.map((p) => (
            <span key={p} className="badge badge-warning">
              {p}
            </span>
          ))}
        </div>
      )}
      <details className="lab-raw">
        <summary>Raw lab values</summary>
        <table className="lab-table">
          <tbody>
            {Object.entries(labs).map(([k, v]) => (
              <tr key={k}>
                <td>{k}</td>
                <td>{v}</td>
                <td className="dim">{units[k] || ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </div>
  )
}
