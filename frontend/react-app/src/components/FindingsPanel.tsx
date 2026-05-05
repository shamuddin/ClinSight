import { Finding, AttentionRegion } from '../types'

export default function FindingsPanel({
  findings,
  regions,
}: {
  findings: Finding[]
  regions: AttentionRegion[]
}) {
  const regionMap = new Map(regions.map((r) => [r.finding_id, r]))

  return (
    <div className="panel">
      <h2>Findings ({findings.length})</h2>
      {findings.length === 0 ? (
        <p className="dim">No findings reported.</p>
      ) : (
        <ul className="finding-list">
          {findings.map((f) => {
            const region = regionMap.get(f.id)
            const hasFlag = f.confidence < 0.5
            return (
              <li key={f.id} className={`finding-item ${hasFlag ? 'flagged' : ''}`}>
                <div className="finding-header">
                  <span className={`badge badge-${f.severity}`}>{f.severity}</span>
                  <strong>{f.finding}</strong>
                  <span className="confidence">{(f.confidence * 100).toFixed(0)}%</span>
                </div>
                <div className="finding-desc">{f.description}</div>
                <div className="finding-meta">
                  <span className="dim">Location: {f.location}</span>
                  {region && (
                    <span className="dim">
                      Attention: ({region.x},{region.y}) {region.w}×{region.h}
                    </span>
                  )}
                </div>
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}
