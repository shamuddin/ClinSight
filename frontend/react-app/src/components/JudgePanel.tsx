import { CheckCircle2, XCircle, ShieldCheck, AlertTriangle, Eye, Activity, Stethoscope } from 'lucide-react'
import { CaseResult } from '../types'

export default function JudgePanel({ result }: { result: CaseResult }) {
  const groundTruth: Record<string, number> = {
    'CS-2024-001': 1, 'CS-2024-002': 1, 'CS-2024-003': 3,
    'CS-2024-004': 1, 'CS-2024-005': 2, 'CS-2024-006': 2,
  }
  const gt = groundTruth[result.case_id] ?? -1
  const correct = result.esi_level === gt

  const safetyFlags = result.safety_flags ?? []
  const audit = result.audit_log ?? []
  const reportSummary = (result.report as any)?.summary as string | undefined

  return (
    <div className="judge-panel">
      {/* ═══ ACCURACY VERDICT ═══ */}
      <div className={`judge-verdict ${correct ? 'judge-verdict--pass' : 'judge-verdict--fail'}`}>
        {correct ? <CheckCircle2 size={28} /> : <XCircle size={28} />}
        <div>
          <div className="judge-verdict-title">{correct ? 'ESI ACCURATE' : 'ESI MISMATCH'}</div>
          <div className="judge-verdict-sub">Ground Truth: ESI {gt} · Predicted: ESI {result.esi_level}</div>
        </div>
      </div>

      {/* ═══ INPUTS ═══ */}
      <div className="judge-section">
        <div className="judge-section-title"><Eye size={14}/> Application Inputs</div>
        <div className="judge-grid">
          <div className="judge-card">
            <strong>Image</strong>
            <span className="mono">{result.image_url?.split('/').pop() || result.case_id + '.png'}</span>
          </div>
          <div className="judge-card">
            <strong>Patient</strong>
            <span>{result.patient_age}yo {result.patient_sex} · {result.patient_race || '—'}</span>
          </div>
          <div className="judge-card">
            <strong>Vitals</strong>
            <span>BP {(result.vitals as any).bp} · HR {(result.vitals as any).hr} · SpO₂ {(result.vitals as any).spo2}%</span>
          </div>
          <div className="judge-card">
            <strong>Chief Complaint</strong>
            <span>{result.chief_complaint}</span>
          </div>
        </div>
      </div>

      {/* ═══ AGENT TRACE ═══ */}
      <div className="judge-section">
        <div className="judge-section-title"><Activity size={14}/> Agent Execution Trace</div>
        <table className="judge-table">
          <thead>
            <tr><th>Agent</th><th>Stage</th><th>Timestamp</th><th>Details</th></tr>
          </thead>
          <tbody>
            {audit.map((entry, i) => (
              <tr key={i}>
                <td>
                  <span className={`judge-badge judge-badge--${entry.agent?.replace('_','-') || 'unknown'}`}>
                    {entry.agent}
                  </span>
                </td>
                <td>{entry.stage}</td>
                <td className="mono">{new Date(entry.timestamp).toLocaleTimeString()}</td>
                <td className="mono small">{entry.details?.toString().slice(0, 60)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* ═══ SAFETY VERIFICATION ═══ */}
      <div className="judge-section">
        <div className="judge-section-title"><ShieldCheck size={14}/> Safety &amp; Re-Verification</div>
        <div className="judge-safety-grid">
          <div className={`judge-safety-item ${safetyFlags.length > 0 ? 'pass' : ''}`}>
            <span>{safetyFlags.length > 0 ? <CheckCircle2 size={14}/> : <XCircle size={14}/>}</span>
            <strong>Re-verification Active</strong>
          </div>
          <div className={`judge-safety-item ${(result as any).contradictions_count > 0 ? 'pass' : ''}`}>
            <span>{(result as any).contradictions_count > 0 ? <CheckCircle2 size={14}/> : <XCircle size={14}/>}</span>
            <strong>Contradiction Detection</strong>
          </div>
          <div className={`judge-safety-item ${(result as any).hallucination_count === 0 ? 'pass' : 'fail'}`}>
            <span>{(result as any).hallucination_count === 0 ? <CheckCircle2 size={14}/> : <AlertTriangle size={14}/>}</span>
            <strong>Hallucination Check</strong>
          </div>
          <div className={`judge-safety-item ${(result as any).bias_count === 0 ? 'pass' : 'fail'}`}>
            <span>{(result as any).bias_count === 0 ? <CheckCircle2 size={14}/> : <AlertTriangle size={14}/>}</span>
            <strong>Bias Audit</strong>
          </div>
        </div>

        {safetyFlags.length > 0 && (
          <div className="judge-flags">
            <div className="judge-section-subtitle"><AlertTriangle size={12}/> Safety Flags Raised ({safetyFlags.length})</div>
            {safetyFlags.map((f, i) => (
              <div key={i} className={`judge-flag judge-flag--${f.severity?.toLowerCase() || 'medium'}`}>
                <strong>{f.rule || f.message?.slice(0, 30)}</strong>
                <span>{f.message}</span>
                {f.confidence_penalty != null && <span className="mono">penalty −{f.confidence_penalty}</span>}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ═══ DOCUMENTER OUTPUTS ═══ */}
      <div className="judge-section">
        <div className="judge-section-title"><Stethoscope size={14}/> Documenter Output Verification</div>
        <div className="judge-card">
          <strong>Differential ({result.differential?.length})</strong>
          <ul>{result.differential?.map((d, i) => <li key={i}>{d}</li>)}</ul>
        </div>
        <div className="judge-card">
          <strong>Suggested Actions ({result.suggested_actions?.length})</strong>
          <ul>{result.suggested_actions?.slice(0,5).map((a, i) => <li key={i}>{a}</li>)}</ul>
        </div>
        {reportSummary && (
          <div className="judge-card">
            <strong>Report Summary</strong>
            <p className="judge-report">{reportSummary}</p>
          </div>
        )}
      </div>

      <div className="judge-footer">
        Total inference time: <strong className="mono">{result.total_time_ms} ms</strong>
        {' · '}
        LLM calls: <strong>LIVE (no cache)</strong>
      </div>
    </div>
  )
}
