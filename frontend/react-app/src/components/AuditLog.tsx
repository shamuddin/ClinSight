import { AuditEntry } from '../types'

export default function AuditLog({ auditLog }: { auditLog: AuditEntry[] }) {
  return (
    <div className="panel">
      <h2>Audit Log ({auditLog.length})</h2>
      {auditLog.length === 0 ? (
        <p className="dim">No audit entries yet.</p>
      ) : (
        <table className="audit-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Agent</th>
              <th>Stage</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            {auditLog.map((entry, i) => (
              <tr key={i}>
                <td className="dim">{new Date(entry.timestamp).toLocaleTimeString()}</td>
                <td>{entry.agent}</td>
                <td>
                  <span className={`badge badge-${entry.stage}`}>{entry.stage}</span>
                </td>
                <td>{entry.details}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
