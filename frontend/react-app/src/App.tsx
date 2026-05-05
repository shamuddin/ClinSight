import { useState, useEffect, useCallback } from 'react'
import { CaseResult, DemoCase } from './types'
import AgentActivity from './components/AgentActivity'
import ImageViewer from './components/ImageViewer'
import FindingsPanel from './components/FindingsPanel'
import LabAlertsPanel from './components/LabAlertsPanel'
import SafetyPanel from './components/SafetyPanel'
import ReportViewer from './components/ReportViewer'
import AuditLog from './components/AuditLog'
import SafetyBanner from './components/SafetyBanner'
import PhysicianVeto from './components/PhysicianVeto'
import Dashboard from './components/Dashboard'

const API_BASE = import.meta.env.VITE_API_URL || ''

function App() {
  const [cases, setCases] = useState<DemoCase[]>([])
  const [result, setResult] = useState<CaseResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetch(`${API_BASE}/demo/cases`)
      .then(r => r.ok ? r.json() : [])
      .then(data => setCases(data))
      .catch(() => setCases([]))
  }, [])

  const handleSelect = useCallback(async (caseId: string) => {
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await fetch(`${API_BASE}/demo/analyze/${encodeURIComponent(caseId)}`)
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Unknown error' }))
        setError(err.detail?.reason || err.detail || `HTTP ${res.status}`)
        setLoading(false)
        return
      }
      const data: CaseResult = await res.json()
      setResult(data)
    } catch (e) {
      setError('Network error — is backend running on :8000?')
    } finally {
      setLoading(false)
    }
  }, [])

  const handleVeto = (action: string) => {
    if (!result) return
    const entry = {
      agent: 'physician',
      stage: 'veto',
      timestamp: new Date().toISOString(),
      details: `Physician ${action} on case ${result.case_id}`,
    }
    setResult(prev => prev ? { ...prev, audit_log: [...prev.audit_log, entry] } : prev)
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>ClinSight</h1>
        <span className="subtitle">Multi-agent Clinical Decision Support</span>
      </header>
      <SafetyBanner />
      <Dashboard cases={cases} onSelect={handleSelect} activeCaseId={result?.case_id} />

      {loading && (
        <div className="loading-bar">
          <div className="loading-inner">Running pipeline — coordinator → radiologist → lab → safety → documenter...</div>
        </div>
      )}
      {error && (
        <div className="error-banner">
          <strong>Pipeline Error:</strong> {error}
        </div>
      )}

      {result && (
        <>
          <div className="esi-bar">
            <span className={`esi-badge esi-${result.esi_level}`}>ESI Level {result.esi_level}</span>
            <span className="esi-desc">{result.esi_description}</span>
            <span className="esi-time">{result.total_time_ms} ms</span>
          </div>
          <div className="panels">
            <ImageViewer result={result} />
            <AgentActivity auditLog={result.audit_log} />
            <FindingsPanel findings={result.findings} regions={result.attention_regions} />
            <LabAlertsPanel alerts={result.lab_alerts} patterns={result.lab_patterns} labs={result.lab_values} units={result.lab_units} />
            <SafetyPanel flags={result.safety_flags} qualityGate={result.quality_gate} pediatricGate={result.pediatric_gate} />
            <ReportViewer result={result} />
            <PhysicianVeto onVeto={handleVeto} />
            <AuditLog auditLog={result.audit_log} />
          </div>
        </>
      )}

      {!result && !loading && !error && (
        <div className="empty-state">Select a case from the dashboard above to begin analysis.</div>
      )}
    </div>
  )
}

export default App
