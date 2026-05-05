import { AuditEntry } from '../types'

export default function AgentActivity({ auditLog }: { auditLog: AuditEntry[] }) {
  return (
    <div className="panel">
      <h2>Agent Activity</h2>
      {auditLog.length === 0 ? (
        <p className="dim">No activity yet.</p>
      ) : (
        <div className="activity-tree">
          {auditLog.map((entry, i) => (
            <div key={i} className="activity-node">
              <span className={`badge badge-${entry.stage}`}>{entry.stage}</span>
              <span className="agent-name">{entry.agent}</span>
              <span className="dim">{entry.details}</span>
              {entry.duration_ms && <span className="duration">{entry.duration_ms}ms</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
