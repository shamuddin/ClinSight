import { useState, useEffect, useCallback } from 'react'
import { Cpu, HelpCircle, Info, Play, Square, Clock, Eye, FileText, AlertTriangle, ShieldCheck, Check, Users, Activity, Stethoscope, BarChart2 } from 'lucide-react'
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
import DiagnosisHero from './components/DiagnosisHero'
import AboutModal from './components/AboutModal'
import AmdModal from './components/AmdModal'
import EmptyHero from './components/EmptyHero'
import ShortcutModal from './components/ShortcutModal'
import JudgePanel from './components/JudgePanel'
import BenchmarkModal from './components/BenchmarkModal'
import { useKeyboard } from './hooks/useKeyboard'
import { usePipelineStream } from './hooks/usePipelineStream'
import { DEMO_STEP_MS, DEMO_SEQUENCE } from './DemoSequence'
import { getOfflineResult, OFFLINE_DEMO_CASES } from './offlineDemo'

const API_BASE = import.meta.env.VITE_API_URL || ''

const ESI_META: Record<number, { label: string; color: string }> = {
  1: { label: 'RESUSCITATION', color: '#dc2626' },
  2: { label: 'EMERGENT', color: '#ea580c' },
  3: { label: 'URGENT', color: '#d97706' },
  4: { label: 'LESS URGENT', color: '#2563eb' },
  5: { label: 'NON-URGENT', color: '#64748b' },
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

// ── View tabs ─────────────────────────────────────────────────────────────────
function ViewTabs({
  mode,
  onChange,
}: {
  mode: 'clinical' | 'technical' | 'judge'
  onChange: (m: 'clinical' | 'technical' | 'judge') => void
}) {
  return (
    <div className="view-tabs">
      <button
        type="button"
        className={`view-tab ${mode === 'clinical' ? 'view-tab--active' : ''}`}
        onClick={() => onChange('clinical')}
      >
        <Stethoscope size={13} style={{ marginRight: 4, verticalAlign: 'middle' }} />
        Clinical
      </button>
      <button
        type="button"
        className={`view-tab ${mode === 'technical' ? 'view-tab--active' : ''}`}
        onClick={() => onChange('technical')}
      >
        <Activity size={13} style={{ marginRight: 4, verticalAlign: 'middle' }} />
        Behind the Scenes
      </button>
      <button
        type="button"
        className={`view-tab ${mode === 'judge' ? 'view-tab--active' : ''}`}
        onClick={() => onChange('judge')}
      >
        Verification
      </button>
    </div>
  )
}

// ── Model specs card for technical view ───────────────────────────────────────
function ModelSpecs() {
  return (
    <div className="result-section" style={{ padding: '20px' }}>
      <div className="section-label">Model Stack</div>
      <div className="hardware-stats">
        <div>
          <span>Vision Model</span>
          <strong>Qwen2.5-VL-7B-Instruct</strong>
        </div>
        <div>
          <span>Text Model</span>
          <strong>Qwen3.5-35B-A3B (MoE)</strong>
        </div>
        <div>
          <span>GPU</span>
          <strong>AMD MI300X · 192 GB VRAM</strong>
        </div>
        <div>
          <span>Framework</span>
          <strong>LangGraph · vLLM · ROCm</strong>
        </div>
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────

export default function App() {
  const [cases, setCases]             = useState<DemoCase[]>([])
  const [result, setResult]           = useState<CaseResult | null>(null)
  const [error, setError]             = useState('')
  const [auditOpen, setAuditOpen]     = useState(false)
  const [vetoAction, setVetoAction]   = useState<string | null>(null)
  const [cached, setCached]           = useState(false)
  const [selectedId, setSelectedId]   = useState('')
  const [aboutOpen, setAboutOpen]     = useState(false)
  const [amdOpen, setAmdOpen]         = useState(false)
  const [shortcutOpen, setShortcutOpen] = useState(false)
  const [benchmarkOpen, setBenchmarkOpen] = useState(false)
  const [demoRunning, setDemoRunning] = useState(false)
  const [demoStep, setDemoStep]       = useState(0)
  const [viewMode, setViewMode]       = useState<'clinical' | 'technical' | 'judge'>('clinical')

  const { pipeline, startStream, stop, agentsFromResult } = usePipelineStream(API_BASE)

  // Load demo case list on mount
  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then(r => r.ok ? r.json() : {})
      .then((data: any) => setCached(!!data.cached))
      .catch(() => setCached(false))
  }, [])

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
    setViewMode('clinical')
    if (!keepDemo) {
      setDemoRunning(false)
      setDemoStep(0)
    }
    startStream(caseId)
  }, [startStream])

  const stopDemo = useCallback(() => {
    setDemoRunning(false)
    setDemoStep(0)
  }, [])

  const startDemo = useCallback(() => {
    const first = DEMO_SEQUENCE[0]
    if (!first) return
    setDemoRunning(true)
    setDemoStep(0)
    handleSelect(first.caseId, true)
  }, [handleSelect])

  useEffect(() => {
    if (!demoRunning) return

    const timer = window.setTimeout(() => {
      const nextStep = demoStep + 1
      if (nextStep >= DEMO_SEQUENCE.length) {
        setDemoRunning(false)
        return
      }
      setDemoStep(nextStep)
      handleSelect(DEMO_SEQUENCE[nextStep].caseId, true)
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
        stopDemo()
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
  const esiMeta      = result ? (ESI_META[result.esi_level] ?? { label: 'UNKNOWN', color: '#64748b' }) : null

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
              <VitalTile label="BP"   value={String(result.vitals?.bp ?? '—')} />
              <VitalTile label="HR"   value={String(result.vitals?.hr ?? '—')} status={vitalStatus('hr',   Number(result.vitals?.hr))} />
              <VitalTile label="RR"   value={String(result.vitals?.rr ?? '—')} status={vitalStatus('rr',   Number(result.vitals?.rr))} />
              <VitalTile label="SpO₂" value={`${result.vitals?.spo2 ?? '—'}%`} status={vitalStatus('spo2', Number(result.vitals?.spo2))} />
              <VitalTile label="Temp" value={`${result.vitals?.temp ?? '—'}°C`} />
            </div>
          </div>
        )}

        <div className="sidebar-spacer" />

        <div className="sidebar-footer">
          <button
            type="button"
            className={`demo-seq-btn ${demoRunning ? 'demo-seq-btn--active' : ''}`}
            onClick={demoRunning ? stopDemo : startDemo}
          >
            {demoRunning ? <Square size={13} /> : <Play size={13} />}
            {demoRunning ? 'Stop Demo' : 'Run Demo'}
          </button>
          <div className="sidebar-links">
            <span style={{ fontSize: '10px', color: 'var(--fg-dim)' }}>
              Keys: 1–6 · A agree · O override · D dismiss · R rerun
            </span>
          </div>
          <div className="live-badge" style={{ fontSize: '10px', color: cached ? '#f59e0b' : '#00ff88', textAlign: 'center', marginTop: '6px', fontWeight: 'bold' }}>
            {cached ? '◉ CACHED — demo data' : '◉ LIVE — AMD MI300X · Qwen VL7B + 35B'}
          </div>
          <SafetyBanner />
        </div>

      </aside>

      {/* ═══════════════════ RIGHT SIDE ═══════════════════ */}
      <div className="right-side">
        <header className="story-header">
          <div>
            <span className="story-kicker">ClinSight Command Center</span>
            <strong>Multi-agent clinical decision support</strong>
          </div>
          <div className="story-header-actions">
            <button type="button" className="story-header-btn" onClick={() => setBenchmarkOpen(true)}>
              <BarChart2 size={14} />
              Benchmark Proof
            </button>
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
                Analyzing case with 12 agents…
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
            <EmptyHero onRunDemo={startDemo} />
          )}

          {demoRunning && (
            <div className="demo-narration" aria-live="polite">
              <span className="demo-narration-step">
                {demoStep + 1}/{DEMO_SEQUENCE.length}
              </span>
              <div>
                <strong>{DEMO_SEQUENCE[demoStep]?.title}</strong>
                <p>{DEMO_SEQUENCE[demoStep]?.narration}</p>
              </div>
              <button type="button" onClick={stopDemo}>Stop</button>
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

              {/* View tabs */}
              <div style={{ padding: '16px 24px 0' }}>
                <ViewTabs mode={viewMode} onChange={setViewMode} />
              </div>

              {/* ▮ HERO BAND (always visible) */}
              <section className="result-section result-hero">
                <div className="hero-esi">
                  <div
                    className={`esi-ring esi-ring-${result.esi_level}`}
                    aria-label={`ESI Level ${result.esi_level}`}
                  >
                    <span className="esi-number">{result.esi_level}</span>
                  </div>
                  <div className="hero-esi-detail">
                    <div className="esi-level-label" style={{ color: esiMeta?.color }}>
                      {esiMeta?.label}
                    </div>
                    <div className="esi-desc-text">{result.esi_description}</div>
                    <div className="hero-meta">
                      <span className="hero-case-id">{result.case_id}</span>
                      <span className="hero-timing">⏱ {(result.total_time_ms >= 1000) ? `${(result.total_time_ms/1000).toFixed(1)}s` : `${result.total_time_ms}ms`} · {result.cached ? 'CACHED' : 'LIVE — AMD MI300X'} · {'35B'}</span>
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

              {viewMode === 'clinical' ? (
                <>
                  {/* ▮ DIAGNOSIS HIGHLIGHT */}
                  <section className="result-section">
                    <div className="section-label">Diagnosis</div>
                    <DiagnosisHero result={result} />
                  </section>

                  {/* ▮ CLINICAL EVIDENCE */}
                  <section className="result-section result-evidence">
                    <div className="section-label">Clinical Evidence</div>
                    <EvidenceRow result={result} />
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
                </>
              ) : viewMode === 'technical' ? (
                <>
                  {/* ▮ AI PIPELINE */}
                  <section className="result-section result-pipeline">
                    <div className="section-label">AI Pipeline — Agent Activity</div>
                    <LivePipeline
                      agents={displayAgents}
                      result={result}
                      streaming={pipeline.streaming}
                    />
                  </section>

                  {/* ▮ AI SAFETY GUARDS */}
                  <section className="result-section result-safety">
                    <div className="section-label">AI Safety Guards</div>
                    <SafetyTheater result={result} />
                  </section>

                  {/* ▮ MODEL SPECS */}
                  <ModelSpecs />

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
                </>
              ) : (
                <>
                  {/* ▮ JUDGE VERIFICATION */}
                  <section className="result-section">
                    <div className="section-label">Verification Panel</div>
                    <JudgePanel result={result} apiBase={API_BASE} />
                  </section>
                </>
              )}
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
      <BenchmarkModal open={benchmarkOpen} onClose={() => setBenchmarkOpen(false)} />
    </div>
  )
}
