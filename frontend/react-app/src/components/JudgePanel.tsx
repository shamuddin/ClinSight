import { CheckCircle2, XCircle, ShieldCheck, AlertTriangle, Eye, Activity, Stethoscope, TrendingUp, Cpu, Info } from 'lucide-react'
import { useState, useEffect } from 'react'
import { CaseResult } from '../types'

interface AccuracyData {
  overall: {
    esi_correct: boolean
    esi_predicted: number
    esi_ground_truth: number
    mean_recall: number
    components_scored: number
  }
  radiologist: {
    findings_found: number
    findings_expected: number
    findings_matched: number
    finding_recall: number
    note?: string
  }
  lab_analyst: {
    alerts_found: number
    alerts_expected: number
    alerts_matched: number
    alert_recall: number
  }
  safety: {
    flags_found: number
    flags_expected: number
    flags_matched: number
    flag_recall: number
    hallucination_count: number
    contradiction_count: number
    bias_count: number
  }
  documenter: {
    differential_found: number
    differential_expected: number
    differential_matched: number
    differential_recall: number
  }
}

interface TransparencyData {
  models: Record<string, ModelTransparency>
  summary: string
  disclaimer: string
  validation_status: string
  intended_use: string
}

interface ModelTransparency {
  model_name: string
  parameter_count: string
  training_status: string
  medical_knowledge_source: string
  what_it_can_do: string[]
  what_it_cannot_do: string[]
  used_for: string
  safety_compensation: string
}

export default function JudgePanel({ result, apiBase }: { result: CaseResult; apiBase: string }) {
  const [accuracy, setAccuracy] = useState<AccuracyData | null>(null)
  const [transparency, setTransparency] = useState<TransparencyData | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!result?.case_id) return
    setLoading(true)

    // Fetch both accuracy and transparency
    const accuracyPromise = fetch(`${apiBase}/judge/accuracy/compute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(result),
    }).then(r => r.ok ? r.json() : Promise.reject(`HTTP ${r.status}`))

    const transparencyPromise = fetch(`${apiBase}/judge/transparency`)
      .then(r => r.ok ? r.json() : Promise.reject(`HTTP ${r.status}`))

    Promise.all([accuracyPromise, transparencyPromise])
      .then(([acc, trans]) => {
        setAccuracy(acc)
        setTransparency(trans)
      })
      .catch(() => {
        setAccuracy(null)
        setTransparency(null)
      })
      .finally(() => setLoading(false))
  }, [result, apiBase])

  const safetyFlags = result.safety_flags ?? []
  const audit = result.audit_log ?? []

  const models = transparency?.models ?? {}

  return (
    <div className="judge-panel">
      {/* ═══ ACCURACY SCORECARD ═══ */}
      {accuracy && (
        <div className="judge-scorecard">
          <div className="judge-scorecard-header">
            <TrendingUp size={18}/>
            <span>Model Accuracy Scorecard</span>
          </div>
          <div className="judge-scorecard-grid">
            <Score
              icon={<TrendingUp size={16}/>}
              label="Radiologist (Vision)"
              recall={accuracy.radiologist.finding_recall}
              detail={`${accuracy.radiologist.findings_matched}/${accuracy.radiologist.findings_expected} imaging findings`}
              note={accuracy.radiologist.note}
            />
            <Score
              icon={<Activity size={16}/>}
              label="Lab Analyst"
              recall={accuracy.lab_analyst.alert_recall}
              detail={`${accuracy.lab_analyst.alerts_matched}/${accuracy.lab_analyst.alerts_expected} alerts`}
            />
            <Score
              icon={<ShieldCheck size={16}/>}
              label="Safety Guard"
              recall={accuracy.safety.flag_recall}
              detail={`${accuracy.safety.flags_matched}/${accuracy.safety.flags_expected} flags`}
            />
            <Score
              icon={<Stethoscope size={16}/>}
              label="Documenter"
              recall={accuracy.documenter.differential_recall}
              detail={`${accuracy.documenter.differential_matched}/${accuracy.documenter.differential_expected} hits`}
            />
          </div>
          <div className="judge-overall">
            Mean Component Recall: <strong>{(accuracy.overall.mean_recall * 100).toFixed(1)}%</strong>
            {' · '}
            ESI: <strong className={accuracy.overall.esi_correct ? 'judge-pass' : 'judge-fail'}>
              {accuracy.overall.esi_correct ? 'CORRECT' : 'WRONG'} (predicted={accuracy.overall.esi_predicted}, GT={accuracy.overall.esi_ground_truth})
            </strong>
          </div>
        </div>
      )}
      {loading && <div className="judge-loading">Computing accuracy…</div>}

      {/* ═══ ACCURACY VERDICT ═══ */}
      <div className={`judge-verdict ${accuracy?.overall?.esi_correct ? 'judge-verdict--pass' : 'judge-verdict--fail'}`}>
        {accuracy?.overall?.esi_correct ? <CheckCircle2 size={28} /> : <XCircle size={28} />}
        <div>
          <div className="judge-verdict-title">
            {accuracy?.overall?.esi_correct ? 'ESI ACCURATE' : 'ESI MISMATCH'}
          </div>
          <div className="judge-verdict-sub">
            Ground Truth: ESI {accuracy?.overall?.esi_ground_truth ?? '—'} · Predicted: ESI {result.esi_level}
          </div>
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
            <span>BP {(result.vitals as any)?.bp ?? '—'} · HR {(result.vitals as any)?.hr ?? '—'} · SpO₂ {(result.vitals as any)?.spo2 ?? '—'}%</span>
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
            {audit.map((entry: any, i: number) => (
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

      {/* ═══ MODEL TRANSPARENCY (OPTION A) ═══ */}
      {transparency && (
        <div className="judge-section">
          <div className="judge-section-title"><Info size={14}/> Model & Medical Knowledge Transparency</div>
          <div className="judge-transparency-banner">
            <strong>TRUTHFUL DISCLOSURE:</strong> These are <strong>general-purpose models</strong>, not medically fine-tuned.
            {' '}Clinical rigor comes from <strong>multi-agent architecture</strong>, not from medical fine-tuning.
          </div>

          {Object.entries(models).map(([key, model]: [string, ModelTransparency]) => (
            <div key={key} className="judge-transparency-model">
              <div className="judge-transparency-header">
                <Cpu size={14}/>
                <strong>{model.model_name}</strong>
                <span className="judge-transparency-params">{model.parameter_count}</span>
                <span className="judge-transparency-status">{model.training_status}</span>
              </div>

              <div className="judge-transparency-source">
                <strong>Medical knowledge source:</strong> {model.medical_knowledge_source}
              </div>

              <div className="judge-transparency-lists">
                <div className="judge-transparency-can">
                  <strong>What it CAN do:</strong>
                  <ul>{model.what_it_can_do?.map((item: string, i: number) => <li key={i}>{item}</li>)}</ul>
                </div>
                <div className="judge-transparency-cannot">
                  <strong>What it CANNOT do:</strong>
                  <ul>{model.what_it_cannot_do?.map((item: string, i: number) => <li key={i}>{item}</li>)}</ul>
                </div>
              </div>

              <div className="judge-transparency-role">
                <strong>Role in pipeline:</strong> {model.used_for}
              </div>
              <div className="judge-transparency-safety">
                <strong>Safety compensation:</strong> {model.safety_compensation}
              </div>
            </div>
          ))}

          <div className="judge-transparency-footer">
            <div><strong>Validation status:</strong> {transparency.validation_status}</div>
            <div><strong>Intended use:</strong> {transparency.intended_use}</div>
            <div className="judge-transparency-disclaimer">{transparency.disclaimer}</div>
          </div>
        </div>
      )}

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
            {safetyFlags.map((f: any, i: number) => (
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
          <ul>{result.differential?.map((d: string, i: number) => <li key={i}>{d}</li>)}</ul>
        </div>
        <div className="judge-card">
          <strong>Suggested Actions ({result.suggested_actions?.length})</strong>
          <ul>{result.suggested_actions?.slice(0,5).map((a: string, i: number) => <li key={i}>{a}</li>)}</ul>
        </div>
      </div>

      <div className="judge-footer">
        Total inference time: <strong className="mono">{result.total_time_ms} ms</strong>
        {' · '}
        LLM calls: <strong>LIVE (no cache)</strong>
      </div>
    </div>
  )
}

function Score({ icon, label, recall, detail, note }: { icon: React.ReactNode; label: string; recall: number; detail: string; note?: string }) {
  const pct = Math.round((recall || 0) * 100)
  const color = pct >= 80 ? '#059669' : pct >= 50 ? '#d97706' : '#dc2626'
  return (
    <div className="judge-score">
      <div className="judge-score-icon">{icon}</div>
      <div className="judge-score-label">{label}</div>
      <div className="judge-score-bar">
        <div className="judge-score-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
      <div className="judge-score-value" style={{ color }}>{pct}%</div>
      <div className="judge-score-detail">{detail}</div>
      {note && <div className="judge-score-note">{note}</div>}
    </div>
  )
}
