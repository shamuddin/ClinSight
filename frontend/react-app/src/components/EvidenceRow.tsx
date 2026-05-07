import { useMemo, useState, useRef, useEffect, useCallback } from 'react'
import { ChevronDown, ChevronUp, Eye, FlaskConical, ScanLine } from 'lucide-react'
import { AttentionRegion, CaseResult, Finding, LabAlert } from '../types'

function severityTone(severity: string): string {
  const s = severity.toLowerCase()
  if (s === 'critical') return 'critical'
  if (s === 'high') return 'high'
  if (s === 'moderate' || s === 'abnormal') return 'moderate'
  return 'low'
}

function confidenceTone(confidence: number): string {
  if (confidence >= 0.8) return 'high'
  if (confidence >= 0.6) return 'medium'
  return 'low'
}

function findingLabel(finding?: Finding): string {
  if (!finding) return 'Unlinked region'
  return finding.finding.replace(/_/g, ' ')
}

function clampPercent(value: number): number {
  return Math.max(0, Math.min(100, value))
}

function isLowThreshold(alert: LabAlert): boolean {
  const code = alert.code.toUpperCase()
  return (
    code.includes('LOW') ||
    code.includes('HYPO') ||
    code.includes('ANEMIA') ||
    code.includes('THROMBO') ||
    code.includes('ACIDOSIS')
  )
}

function labScale(alert: LabAlert): { valuePct: number; thresholdPct: number; direction: 'low' | 'high' } {
  const low = isLowThreshold(alert)
  if (low) {
    const max = Math.max(alert.threshold * 1.8, alert.value * 1.25, 1)
    return {
      direction: 'low',
      thresholdPct: clampPercent((alert.threshold / max) * 100),
      valuePct: clampPercent((alert.value / max) * 100),
    }
  }

  const max = Math.max(alert.value, alert.threshold * 1.35, 1)
  return {
    direction: 'high',
    thresholdPct: clampPercent((alert.threshold / max) * 100),
    valuePct: clampPercent((alert.value / max) * 100),
  }
}

// ── Real X-ray viewer with attention overlay ─────────────────────────────────

function XrayEvidence({
  result,
  activeRegionId,
  onRegionHover,
}: {
  result: CaseResult
  activeRegionId: string | null
  onRegionHover: (id: string | null) => void
}) {
  const findingMap = useMemo(
    () => new Map(result.findings.map((finding) => [finding.id, finding])),
    [result.findings],
  )

  const imgRef = useRef<HTMLImageElement>(null)
  const [imgSize, setImgSize] = useState({ width: 0, height: 0 })

  const handleImageLoad = useCallback(() => {
    if (imgRef.current) {
      setImgSize({
        width: imgRef.current.clientWidth,
        height: imgRef.current.clientHeight,
      })
    }
  }, [])

  useEffect(() => {
    window.addEventListener('resize', handleImageLoad)
    return () => window.removeEventListener('resize', handleImageLoad)
  }, [handleImageLoad])

  // NIH images are 1024x1024; scale coordinates to displayed size
  const scaleX = imgSize.width / 1024
  const scaleY = imgSize.height / 1024

  // Use public demo-images for offline, or backend endpoint when online
  const imageSrc = result.image_url
    ? `${import.meta.env.VITE_API_URL || ''}${result.image_url}`
    : `/demo-images/${result.case_id.split('::')[0]}.png`

  return (
    <article className="evidence-panel evidence-xray">
      <div className="evidence-panel-header">
        <div>
          <span className="evidence-kicker">Image</span>
          <h3>X-Ray Evidence</h3>
        </div>
        <span className="evidence-chip">
          <ScanLine size={12} />
          CXR PA
        </span>
      </div>

      <div className="xray-viewer">
        <img
          ref={imgRef}
          src={imageSrc}
          alt={`Chest X-ray for ${result.case_id}`}
          onLoad={handleImageLoad}
          draggable={false}
        />
        {imgSize.width > 0 && (
          <div className="xray-overlay">
            {result.attention_regions.map((region) => {
              const finding = findingMap.get(region.finding_id)
              const isActive = activeRegionId === region.finding_id
              return (
                <div
                  key={region.finding_id}
                  className={`xray-region ${isActive ? 'xray-region--active' : ''}`}
                  style={{
                    left: `${region.x * scaleX}px`,
                    top: `${region.y * scaleY}px`,
                    width: `${region.w * scaleX}px`,
                    height: `${region.h * scaleY}px`,
                  }}
                  onMouseEnter={() => onRegionHover(region.finding_id)}
                  onMouseLeave={() => onRegionHover(null)}
                  title={`${findingLabel(finding)} - ${(region.confidence * 100).toFixed(0)}% attention`}
                >
                  <span className="xray-region-label">
                    {findingLabel(finding)} ({(region.confidence * 100).toFixed(0)}%)
                  </span>
                </div>
              )
            })}
          </div>
        )}
      </div>

      <div className="xray-viewer-footer">
        <span>{result.attention_regions.length} attention regions</span>
        <span>{result.findings.length} findings linked</span>
      </div>
    </article>
  )
}

function FindingCard({
  finding,
  region,
  active,
  expanded,
  onHover,
  onToggle,
}: {
  finding: Finding
  region?: AttentionRegion
  active: boolean
  expanded: boolean
  onHover: (id: string | null) => void
  onToggle: () => void
}) {
  const tone = severityTone(finding.severity)
  const confidence = Math.round(finding.confidence * 100)
  const visualGrounding = region ? Math.round(region.confidence * 100) : 0
  const confTone = confidenceTone(finding.confidence)

  return (
    <li
      className={`evidence-finding-card evidence-finding-card--${tone} ${active ? 'evidence-finding-card--active' : ''}`}
      onMouseEnter={() => onHover(finding.id)}
      onMouseLeave={() => onHover(null)}
    >
      <div className="evidence-finding-top">
        <span className={`badge badge-${tone}`}>{finding.severity}</span>
        <strong>{finding.finding.replace(/_/g, ' ')}</strong>
        <span className={`evidence-confidence-value evidence-confidence-value--${confTone}`}>{confidence}%</span>
      </div>

      <div className="evidence-confidence-track" aria-label={`Confidence ${confidence}%`}>
        <div
          className={`evidence-confidence-fill evidence-confidence-fill--${confTone}`}
          style={{ width: `${confidence}%` }}
        />
      </div>

      <p>{finding.description}</p>

      <button className="why-toggle" type="button" onClick={onToggle} aria-expanded={expanded}>
        <Eye size={12} />
        Why?
        {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
      </button>

      {expanded && (
        <div className="why-panel">
          <div className="why-row">
            <span>Clinical location</span>
            <strong>{finding.location || 'Not specified'}</strong>
          </div>
          <div className="why-row">
            <span>Visual grounding</span>
            <strong>{region ? `${visualGrounding}% attention match` : 'No linked region'}</strong>
          </div>
          <div className="why-row">
            <span>Safety adjusted confidence</span>
            <strong>{confidence}%</strong>
          </div>
        </div>
      )}
    </li>
  )
}

function FindingsEvidence({
  result,
  activeRegionId,
  onFindingHover,
}: {
  result: CaseResult
  activeRegionId: string | null
  onFindingHover: (id: string | null) => void
}) {
  const [expandedId, setExpandedId] = useState<string | null>(result.findings[0]?.id ?? null)
  const regionMap = useMemo(
    () => new Map(result.attention_regions.map((region) => [region.finding_id, region])),
    [result.attention_regions],
  )

  return (
    <article className="evidence-panel">
      <div className="evidence-panel-header">
        <div>
          <span className="evidence-kicker">Findings</span>
          <h3>Reasoned Findings</h3>
        </div>
        <span className="evidence-count">{result.findings.length}</span>
      </div>

      {result.findings.length === 0 ? (
        <p className="evidence-empty">No findings reported.</p>
      ) : (
        <ul className="evidence-finding-list">
          {result.findings.map((finding) => (
            <FindingCard
              key={finding.id}
              finding={finding}
              region={regionMap.get(finding.id)}
              active={activeRegionId === finding.id}
              expanded={expandedId === finding.id}
              onHover={onFindingHover}
              onToggle={() => setExpandedId((prev) => (prev === finding.id ? null : finding.id))}
            />
          ))}
        </ul>
      )}
    </article>
  )
}

function LabValueBar({ alert }: { alert: LabAlert }) {
  const scale = labScale(alert)
  const status = severityTone(alert.severity)
  const operator = scale.direction === 'low' ? '<' : '>'

  return (
    <div className={`lab-threshold-card lab-threshold-card--${status}`}>
      <div className="lab-threshold-top">
        <div>
          <strong>{alert.lab.toUpperCase()}</strong>
          <span>{alert.description}</span>
        </div>
        <span className={`badge badge-${status}`}>{alert.severity}</span>
      </div>

      <div className="lab-threshold-scale">
        <div className="lab-threshold-fill" style={{ width: `${scale.valuePct}%` }} />
        <div className="lab-threshold-marker" style={{ left: `${scale.thresholdPct}%` }} />
        <div className="lab-threshold-dot" style={{ left: `${scale.valuePct}%` }} />
      </div>

      <div className="lab-threshold-meta">
        <span>
          Value <strong>{alert.value} {alert.unit}</strong>
        </span>
        <span>
          Threshold {operator} {alert.threshold}
        </span>
      </div>
    </div>
  )
}

function LabsEvidence({ result }: { result: CaseResult }) {
  const rawLabs = Object.entries(result.lab_values).slice(0, 8)

  return (
    <article className="evidence-panel">
      <div className="evidence-panel-header">
        <div>
          <span className="evidence-kicker">Labs</span>
          <h3>Threshold Evidence</h3>
        </div>
        <span className="evidence-chip">
          <FlaskConical size={12} />
          {result.lab_alerts.length} alerts
        </span>
      </div>

      <div className="lab-threshold-list">
        {result.lab_alerts.length === 0 ? (
          <p className="evidence-empty">No threshold-crossing values.</p>
        ) : (
          result.lab_alerts.map((alert) => <LabValueBar key={`${alert.code}-${alert.lab}`} alert={alert} />)
        )}
      </div>

      {result.lab_patterns.length > 0 && (
        <div className="evidence-patterns">
          {result.lab_patterns.map((pattern) => (
            <span key={pattern}>{pattern.replace(/_/g, ' ')}</span>
          ))}
        </div>
      )}

      <div className="compact-lab-grid">
        {rawLabs.map(([key, value]) => (
          <div key={key} className="compact-lab">
            <span>{key}</span>
            <strong>{value} {result.lab_units[key] ?? ''}</strong>
          </div>
        ))}
      </div>
    </article>
  )
}

export default function EvidenceRow({ result }: { result: CaseResult }) {
  const [activeRegionId, setActiveRegionId] = useState<string | null>(null)

  return (
    <div className="evidence-row">
      <XrayEvidence result={result} activeRegionId={activeRegionId} onRegionHover={setActiveRegionId} />
      <FindingsEvidence result={result} activeRegionId={activeRegionId} onFindingHover={setActiveRegionId} />
      <LabsEvidence result={result} />
    </div>
  )
}
