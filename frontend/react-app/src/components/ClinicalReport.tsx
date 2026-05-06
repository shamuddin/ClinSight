import { useMemo, useState } from 'react'
import {
  AlertTriangle,
  ClipboardList,
  Download,
  FileText,
  FlaskConical,
  ScanLine,
  Send,
  ShieldCheck,
  X,
} from 'lucide-react'
import { CaseResult } from '../types'

function diagnosisWeight(result: CaseResult, diagnosis: string, index: number): number {
  const text = diagnosis.toLowerCase()
  const findingBoost = result.findings.some((finding) =>
    text.includes(finding.finding.replace(/_/g, ' ').toLowerCase()) ||
    finding.description.toLowerCase().includes(text.split(' ')[0] ?? ''),
  ) ? 20 : 0
  const labBoost = result.lab_patterns.some((pattern) =>
    text.includes(pattern.replace(/_/g, ' ').toLowerCase().split(' ')[0] ?? ''),
  ) ? 14 : 0
  const safetyPenalty = result.safety_flags.length * 4
  return Math.max(28, Math.min(96, 90 - index * 11 + findingBoost + labBoost - safetyPenalty))
}

function actionIcon(action: string) {
  const lower = action.toLowerCase()
  if (lower.includes('lab') || lower.includes('serial')) return <FlaskConical size={14} />
  if (lower.includes('image') || lower.includes('x-ray') || lower.includes('imaging')) return <ScanLine size={14} />
  if (lower.includes('icu') || lower.includes('critical') || lower.includes('immediate')) return <AlertTriangle size={14} />
  return <ClipboardList size={14} />
}

export default function ClinicalReport({ result }: { result: CaseResult }) {
  const [ehrOpen, setEhrOpen] = useState(false)
  const weights = useMemo(
    () => result.differential.map((diagnosis, index) => diagnosisWeight(result, diagnosis, index)),
    [result],
  )
  const safetyPassed = result.safety_flags.length === 0

  return (
    <div className="clinical-report">
      <div className="clinical-report-toolbar">
        <div>
          <h3>Clinical Report</h3>
          <p>Evidence-weighted differential and action handoff</p>
        </div>
        <div className="clinical-report-actions">
          <button type="button" className="report-action-btn" onClick={() => window.print()}>
            <Download size={14} />
            Export PDF
          </button>
          <button type="button" className="report-action-btn report-action-btn--ghost" onClick={() => setEhrOpen(true)}>
            <Send size={14} />
            Send to EHR
          </button>
        </div>
      </div>

      <div className="clinical-report-grid">
        <section className="report-column">
          <div className="report-column-header">
            <FileText size={15} />
            Differential Diagnosis
          </div>
          <ol className="differential-list">
            {result.differential.map((diagnosis, index) => (
              <li key={diagnosis} className="differential-item">
                <div className="differential-row">
                  <span className="differential-rank">{index + 1}</span>
                  <strong>{diagnosis}</strong>
                  <span className="differential-weight">{weights[index]}%</span>
                </div>
                <div className="differential-bar">
                  <div style={{ width: `${weights[index]}%` }} />
                </div>
              </li>
            ))}
          </ol>
        </section>

        <section className="report-column">
          <div className="report-column-header">
            <ClipboardList size={15} />
            Suggested Actions
          </div>
          <ul className="report-action-list">
            {result.suggested_actions.map((action) => (
              <li key={action}>
                <span className="report-action-icon">{actionIcon(action)}</span>
                <span>{action}</span>
              </li>
            ))}
          </ul>
        </section>
      </div>

      <div className="report-handoff">
        <div>
          <span className="report-handoff-label">Patient</span>
          <strong>
            {result.patient_age}yo {result.patient_sex}, {result.chief_complaint}
          </strong>
        </div>
        <div>
          <span className="report-handoff-label">Triage</span>
          <strong>ESI {result.esi_level} - {result.esi_description}</strong>
        </div>
        <div>
          <span className="report-handoff-label">Safety Gate</span>
          <strong className={safetyPassed ? 'handoff-good' : 'handoff-warn'}>
            {safetyPassed ? 'All guards passed' : `${result.safety_flags.length} flag(s) require review`}
          </strong>
        </div>
        <div>
          <span className="report-handoff-label">Pipeline</span>
          <strong>{result.total_time_ms} ms</strong>
        </div>
      </div>

      {ehrOpen && (
        <div className="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="ehr-modal-title">
          <div className="modal-card modal-card--small">
            <div className="modal-header">
              <div>
                <span className="evidence-kicker">Integration Preview</span>
                <h3 id="ehr-modal-title">EHR Handoff Package</h3>
              </div>
              <button type="button" className="icon-btn" onClick={() => setEhrOpen(false)} aria-label="Close EHR modal">
                <X size={16} />
              </button>
            </div>
            <div className="ehr-preview">
              <ShieldCheck size={18} />
              <div>
                <strong>FHIR DiagnosticReport ready</strong>
                <p>
                  Case summary, ESI score, differential, actions, safety flags, and audit references would be transmitted to the configured EHR endpoint.
                </p>
              </div>
            </div>
            <pre className="ehr-json">
{JSON.stringify({
  resourceType: 'DiagnosticReport',
  status: 'preliminary',
  code: 'ClinSight triage support',
  subject: result.case_id,
  conclusion: `ESI ${result.esi_level}: ${result.esi_description}`,
}, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  )
}
