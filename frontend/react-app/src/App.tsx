import { useState, useEffect, useCallback } from 'react'
import { Cpu, HelpCircle, Info, Play, Square, Clock, Eye, FileText, AlertTriangle, ShieldCheck, Check, Users } from 'lucide-react'
import { CaseResult, DemoCase } from './types'
import EvidenceRow from './components/EvidenceRow'
import ClinicalReport from './components/ClinicalReport'
import AuditLog from './components/AuditLog'
import SafetyBanner from './components/SafetyBanner'
import PhysicianVeto from './components/PhysicianVeto'
import Dashboard from './components/Dashboard'
import WhatIfSimulator from './components/WhatIfSimulator'
import LivePipeline from './components/LivePipeline'
import SafetyTheater from './components/SafetyTheater'
import AboutModal from './components/AboutModal'
import AmdModal from './components/AmdModal'
import EmptyHero from './components/EmptyHero'
import ShortcutModal from './components/ShortcutModal'
import { useKeyboard } from './hooks/useKeyboard'
import { usePipelineStream } from './hooks/usePipelineStream'
import { DEMO_STEP_MS, GRAND_DEMO_SEQUENCE } from './DemoSequence'
import { getOfflineResult, OFFLINE_DEMO_CASES } from './offlineDemo'

const API_BASE = import.meta.env.VITE_API_URL || ''

const ESI_META: Record<number, { label: string }> = {
  1: { label: 'RESUSCITATION' },
  2: { label: 'EMERGENT' },
  3: { label: 'URGENT' },
  4: { label: 'LESS URGENT' },
  5: { label: 'NON-URGENT' },
}

// ── EKG pulse animation ───────────────────────────────────────────────────────
function EkgPulse() {
  return (
    <svg className="ekg-svg" viewBox="0 0 80 20" fill="none" aria-hidden="true">
      <polyline
        className="ekg-line"
        points="0,10 10,10 16,3 22,17 28,3 34,10 46,10 52,7 58,10 80,10"
      />
    </svg>
  )
}

// ── Vital tile ────────────────────────────────────────────────────────────────
function VitalTile({
  label,
  value,
  status = 'normal',
}: {
  label:   string
  value:   string | number
  status?: 'normal' | 'warning' | 'critical'
}) {
  return (
    <div className={`vital-tile${status !== 'normal' ? ` vital-tile--${status}` : ''}`}>
      <span className="vital-label">{label}</span>
      <span className="vital-value mono">{value}</span>
      <span className={`vital-dot vital-dot--${status}`} />
    </div>
  )
}

function vitalStatus(key: string, value: number): 'normal' | 'warning' | 'critical' {
  if (key === 'hr'   && value > 130) return 'critical'
  if (key === 'hr'   && value > 100) return 'warning'
  if (key === 'spo2' && value < 90)  return 'critical'
  if (key === 'spo2' && value < 95)  return 'warning'
  if (key === 'rr'   && value > 25)  return 'critical'
  if (key === 'rr'   && value > 20)  return 'warning'
  return 'normal'
}

function systemConfidence(result: CaseResult): number {
  if (result.findings.length === 0) return 75
  const avg     = result.findings.reduce((s, f) => s + f.confidence, 0) / result.findings.length
  const penalty = result.safety_flags.length * 0.04
  return Math.max(20, Math.min(99, Math.round((avg - penalty) * 100)))
}

function confidenceClass(pct: number): 'high' | 'medium' | 'low' {
  if (pct >= 80) return 'high'
  if (pct >= 60) return 'medium'
  return 'low'
}

// ─────────────────────────────────────────────────────────────────────────────

export default function App() {
  const [cases, setCases]             = useState<DemoCase[]>([])
  const [result, setResult]           = useState<CaseResult | null>(null)
  const [error, setError]             = useState('')
  const [auditOpen, setAuditOpen]     = useState(false)
  const [vetoAction, setVetoAction]   = useState<string | null>(null)
  const [selectedId, setSelectedId]   = useState('')
  const [aboutOpen, setAboutOpen]     = useState(false)
  const [amdOpen, setAmdOpen]         = useState(false)
  const [shortcutOpen, setShortcutOpen] = useState(false)
  const [demoRunning, setDemoRunning] = useState(false)
  const [demoStep, setDemoStep]       = useState(0)

  const { pipeline, startStream, stop, agentsFromResult } = usePipelineStream(API_BASE)

  // Load demo case list on mount
  useEffect(() => {
    fetch(`${API_BASE}/demo/cases`)
      .then(r => r.ok ? r.json() : [])
      .then((data: DemoCase[]) => setCases(data.length > 0 ? data : OFFLINE_DEMO_CASES))
      .catch(() => setCases(OFFLINE_DEMO_CASES))
  }, [])

  // When stream delivers its final result, set it as the active result
  useEffect(() => {
    if (pipeline.result) {
      setResult(pipeline.result)
    }
  }, [pipeline.result])

  // If stream errors, fall back to direct fetch
  useEffect(() => {
    if (pipeline.error === 'stream' && selectedId) {
      const fetchFallback = async () => {
        try {
          const res = await fetch(`${API_BASE}/demo/analyze/${encodeURIComponent(selectedId)}`)
          if (!res.ok) {
            const cached = getOfflineResult(selectedId)
            if (cached) {
              setResult(cached)
              setError('')
              return
            }
            const err = await res.json().catch(() => ({ detail: 'Unknown error' }))
            setError(err.detail?.reason || err.detail || `HTTP ${res.status}`)
            return
          }
          const data: CaseResult = await res.json()
          setResult(data)
        } catch {
          const cached = getOfflineResult(selectedId)
          if (cached) {
            setResult(cached)
            setError('')
            return
          }
          setError('Network error — is the backend running on :8000?')
        }
      }
      fetchFallback()
    }
  }, [pipeline.error, selectedId])

  const handleSelect = useCallback((caseId: string, keepDemo = false) => {
    setSelectedId(caseId)
    setError('')
    setResult(null)
    setVetoAction(null)
    setAuditOpen(false)
    if (!keepDemo) {
      setDemoRunning(false)
      setDemoStep(0)
    }
    startStream(caseId)
  }, [startStream])

  const stopGrandDemo = useCallback(() => {
    setDemoRunning(false)
    setDemoStep(0)
  }, [])

  const startGrandDemo = useCallback(() => {
    const first = GRAND_DEMO_SEQUENCE[0]
    if (!first) return
    setDemoRunning(true)
    setDemoStep(0)
    handleSelect(first.caseId, true)
  }, [handleSelect])

  useEffect(() => {
    if (!demoRunning) return

    const timer = window.setTimeout(() => {
      const nextStep = demoStep + 1
      if (nextStep >= GRAND_DEMO_SEQUENCE.length) {
        setDemoRunning(false)
        return
      }
      setDemoStep(nextStep)
      handleSelect(GRAND_DEMO_SEQUENCE[nextStep].caseId, true)
    }, DEMO_STEP_MS)

    return () => window.clearTimeout(timer)
  }, [demoRunning, demoStep, handleSelect])

  const handleVeto = useCallback((action: string) => {
    if (!result) return
    setVetoAction(action)
    const entry = {
      agent:     'physician',
      stage:     'veto',
      timestamp: new Date().toISOString(),
      details:   `Physician ${action} on case ${result.case_id}`,
    }
    setResult(prev => prev ? { ...prev, audit_log: [...prev.audit_log, entry] } : prev)
  }, [result])

  // Keyboard shortcuts
  useKeyboard({
    '1': () => { if (cases[0]) handleSelect(cases[0].case_id) },
    '2': () => { if (cases[1]) handleSelect(cases[1].case_id) },
    '3': () => { if (cases[2]) handleSelect(cases[2].case_id) },
    '4': () => { if (cases[3]) handleSelect(cases[3].case_id) },
    '5': () => { if (cases[4]) handleSelect(cases[4].case_id) },
    '6': () => { if (cases[5]) handleSelect(cases[5].case_id) },
    'a': () => { if (result && !vetoAction) handleVeto('agreed') },
    'o': () => { if (result && !vetoAction) handleVeto('overridden') },
    'd': () => { if (result && !vetoAction) handleVeto('dismissed') },
    'r': () => { if (selectedId) handleSelect(selectedId) },
    '?': () => setShortcutOpen(true),
    'Escape': () => {
      if (aboutOpen || amdOpen || shortcutOpen) {
        setAboutOpen(false)
        setAmdOpen(false)
        setShortcutOpen(false)
        return
      }
      if (demoRunning) {
        stopGrandDemo()
        return
      }
      stop()
    },
  })

  // Derive pipeline display agents: stream data when live, audit_log derivation when static
  const displayAgents = result && !pipeline.streaming
    ? agentsFromResult(result)
    : pipeline.agents

  const isLoading    = pipeline.streaming
  const conf         = result ? systemConfidence(result) : 0
  const confCls      = confidenceClass(conf)
  const esiMeta      = result ? (ESI_META[result.esi_level] ?? { label: 'UNKNOWN' }) : null

  return (
    <div className="app-shell">

      {/* ═══════════════════ SIDEBAR ═══════════════════ */}
      <aside className="sidebar">

        <div className="sidebar-logo">
          <span className="logo-icon" aria-hidden="true">⚕</span>
          <div className="logo-text-group">
            <span className="logo-name">ClinSight</span>
            <span className="logo-tag">Clinical AI</span>
          </div>
          <EkgPulse />
        </div>

        <button type="button" className="amd-strip" onClick={() => setAmdOpen(true)}>
          <Cpu size={12} />
          AMD MI300X · 192 GB · Qwen 7B + 35B
        </button>

        <div className="sidebar-section sidebar-section--scroll">
          <div className="sidebar-label">Cases</div>
          <Dashboard cases={cases} onSelect={handleSelect} activeCaseId={result?.case_id ?? selectedId} />
        </div>

        {result && (
          <div className="patient-snapshot">
            <div className="sidebar-label">Patient</div>
            <div className="patient-demo">
              {result.patient_age}yo {result.patient_sex}
              {result.patient_race ? ` · ${result.patient_race}` : ''}
            </div>
            <div className="patient-complaint">{result.chief_complaint}</div>
            <div className="vitals-grid">
              <VitalTile label="BP"   value={String(result.vitals.bp ?? '—')} />
              <VitalTile label="HR"   value={String(result.vitals.hr ?? '—')} status={vitalStatus('hr',   Number(result.vitals.hr))} />
              <VitalTile label="RR"   value={String(result.vitals.rr ?? '—')} status={vitalStatus('rr',   Number(result.vitals.rr))} />
              <VitalTile label="SpO₂" value={`${result.vitals.spo2 ?? '—'}%`} status={vitalStatus('spo2', Number(result.vitals.spo2))} />
              <VitalTile label="Temp" value={`${result.vitals.temp ?? '—'}°C`} />
            </div>
          </div>
        )}

        <div className="sidebar-spacer" />

        <div className="sidebar-footer">
          <button
            type="button"
            className={`demo-seq-btn ${demoRunning ? 'demo-seq-btn--active' : ''}`}
            onClick={demoRunning ? stopGrandDemo : startGrandDemo}
          >
            {demoRunning ? <Square size={13} /> : <Play size={13} />}
            {demoRunning ? 'Stop Grand Demo' : 'Run Grand Demo'}
          </button>
          <div className="sidebar-links">
            <span style={{ fontSize: '10px', color: 'var(--fg-dim)' }}>
              Keys: 1–6 · A agree · O override · D dismiss · R rerun
            </span>
          </div>
          <SafetyBanner />
        </div>

      </aside>

      {/* ═══════════════════ RIGHT SIDE ═══════════════════ */}
      <div className="right-side">
        <header className="story-header">
          <div>
            <span className="story-kicker">ClinSight Command Center</span>
            <strong>12 reasoning agents catch what a single model misses</strong>
          </div>
          <div className="story-header-actions">
            <button type="button" className="story-header-btn" onClick={() => setAboutOpen(true)}>
              <Info size={14} />
              Architecture
            </button>
            <button
              type="button"
              className="story-header-btn story-header-btn--icon"
              onClick={() => setShortcutOpen(true)}
              aria-label="Open keyboard shortcuts"
            >
              <HelpCircle size={15} />
            </button>
          </div>
        </header>
        <main className="main-scroll">

          {/* Loading */}
          {isLoading && (
            <div className="pipeline-loading">
              <div className="pipeline-loading-inner">
                <span className="pulse-dot" />
                Pipeline streaming — watch agents illuminate in real-time…
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="error-banner">
              <strong>Pipeline error:</strong> {error}
            </div>
          )}

          {/* Empty / welcome */}
          {!result && !isLoading && !error && !pipeline.streaming && (
            <EmptyHero onRunDemo={startGrandDemo} />
          )}

          {demoRunning && (
            <div className="demo-narration" aria-live="polite">
              <span className="demo-narration-step">
                {demoStep + 1}/{GRAND_DEMO_SEQUENCE.length}
              </span>
              <div>
                <strong>{GRAND_DEMO_SEQUENCE[demoStep]?.title}</strong>
                <p>{GRAND_DEMO_SEQUENCE[demoStep]?.narration}</p>
              </div>
              <button type="button" onClick={stopGrandDemo}>Stop</button>
            </div>
          )}

          {/* Pipeline animating (show while streaming even before result) */}
          {(isLoading || pipeline.streaming) && !result && (
            <div className="result-section result-pipeline">
              <div className="section-label">AI Pipeline — Live</div>
              <LivePipeline
                agents={displayAgents}
                result={null}
                streaming={pipeline.streaming}
              />
            </div>
          )}

          {/* ── Full case result ── */}
          {result && (
            <div className="case-result">

              {/* ▮ HERO BAND */}
              <section className="result-section result-hero">
                <div className="hero-esi">
                  <div className={`esi-ring esi-ring-${result.esi_level}`} aria-label={`ESI Level ${result.esi_level}`}>
                    <span className="esi-number">{result.esi_level}</span>
                  </div>
                  <div className="hero-esi-detail">
                    <div className={`esi-level-label esi-label-${result.esi_level}`}>
                      {esiMeta?.label}
                    </div>
                    <div className="esi-desc-text">{result.esi_description}</div>
                    <div className="hero-meta">
                      <span className="hero-case-id">{result.case_id}</span>
                      <span className="hero-timing">⏱ {result.total_time_ms} ms</span>
                    </div>
                    <div className="system-confidence">
                      <span className="confidence-label">Confidence</span>
                      <div className="confidence-bar-wrap">
                        <div
                          className={`confidence-bar confidence-bar--${confCls}`}
                          style={{ width: `${conf}%` }}
                        />
                      </div>
                      <span className={`confidence-pct confidence-pct--${confCls}`}>{conf}%</span>
                    </div>
                  </div>
                </div>
                <div className="hero-actions">
                  {vetoAction ? (
                    <div className="veto-confirmed">
                      Physician: <strong>{vetoAction}</strong> · {new Date().toLocaleTimeString()}
                    </div>
                  ) : (
                    <PhysicianVeto onVeto={handleVeto} />
                  )}
                </div>
              </section>

              {/* ▮ AI PIPELINE — LivePipeline (replaces AgentActivity) */}
              <section className="result-section result-pipeline">
                <div className="section-label">AI Pipeline</div>
                <LivePipeline
                  agents={displayAgents}
                  result={result}
                  streaming={pipeline.streaming}
                />
              </section>

              {/* ▮ CLINICAL EVIDENCE */}
              <section className="result-section result-evidence">
                <div className="section-label">Clinical Evidence</div>
                <EvidenceRow result={result} />
              </section>

              {/* ▮ AI SAFETY GUARDS — SafetyTheater (replaces SafetyPanel) */}
              <section className="result-section result-safety">
                <div className="section-label">AI Safety Guards</div>
                <SafetyTheater result={result} />
              </section>

              {/* ▮ CLINICAL REPORT */}
              <section className="result-section result-report">
                <div className="section-label">Clinical Report</div>
                <ClinicalReport result={result} />
              </section>

              {/* ▮ WHAT-IF SIMULATOR */}
              <section className="result-section result-whatif">
                <div className="section-label">What-If Simulator</div>
                <WhatIfSimulator result={result} apiBase={API_BASE} />
              </section>

              {/* ▮ IMPACT */}
              <section className="result-section">
                <div className="section-label">Impact</div>
                <div className="impact-grid">
                  <div className="impact-card impact-before">
                    <div className="impact-header">Status Quo</div>
                    <div className="impact-metric"><Clock size={13} /> ~30 min review</div>
                    <div className="impact-metric"><Eye size={13} /> 1 reviewer</div>
                    <div className="impact-metric"><FileText size={13} /> No audit trail</div>
                    <div className="impact-metric"><AlertTriangle size={13} /> Bias unflagged</div>
                    <div className="impact-metric"><AlertTriangle size={13} /> No safety layer</div>
                  </div>
                  <div className="impact-vs">VS</div>
                  <div className="impact-card impact-after">
                    <div className="impact-header">With ClinSight</div>
                    <div className="impact-metric"><Clock size={13} /> {result.total_time_ms} ms</div>
                    <div className="impact-metric"><Users size={13} /> 12 agents</div>
                    <div className="impact-metric"><FileText size={13} /> Cryptographic audit</div>
                    <div className="impact-metric"><Check size={13} /> Bias audited</div>
                    <div className="impact-metric"><ShieldCheck size={13} /> 4 safety guards</div>
                  </div>
                </div>
              </section>

            </div>
          )}
        </main>

        {/* ── Audit drawer ── */}
        <div className="audit-bar">
          <button
            className="audit-bar-toggle"
            onClick={() => setAuditOpen(o => !o)}
            aria-expanded={auditOpen}
          >
            <span>{auditOpen ? '▼' : '▲'}</span>
            Audit Trail · {result?.audit_log.length ?? 0} entries
            {result && (
              <span className="audit-bar-timing">{result.total_time_ms} ms total</span>
            )}
          </button>
          {auditOpen && result && (
            <div className="audit-bar-content">
              <AuditLog auditLog={result.audit_log} />
            </div>
          )}
        </div>
      </div>
      <AboutModal open={aboutOpen} onClose={() => setAboutOpen(false)} />
      <AmdModal open={amdOpen} onClose={() => setAmdOpen(false)} />
      <ShortcutModal open={shortcutOpen} onClose={() => setShortcutOpen(false)} />
    </div>
  )
}
