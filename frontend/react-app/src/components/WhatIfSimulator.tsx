import { useEffect, useState } from 'react'
import { Activity, AlertTriangle, CheckCircle2, Loader2, Play, TrendingDown, TrendingUp } from 'lucide-react'
import { CaseResult } from '../types'

interface Scenario {
  name: string
  label: string
  intent: string
  labOverrides: Record<string, number>
  vitalsOverrides: Record<string, number>
}

const SCENARIOS: Scenario[] = [
  {
    name: 'Current',
    label: 'Baseline',
    intent: 'Original case as analyzed',
    labOverrides: {},
    vitalsOverrides: {},
  },
  {
    name: 'Worse',
    label: 'Deterioration',
    intent: 'Hypoxia, lactate rise, unstable vitals',
    labOverrides: { wbc: 16.5, lactate: 5.2, pO2: 55, potassium: 5.8 },
    vitalsOverrides: { hr: 130, rr: 28, spo2: 88 },
  },
  {
    name: 'Better',
    label: 'Improvement',
    intent: 'Normalized labs and respiratory status',
    labOverrides: { wbc: 7.0, lactate: 1.1, pO2: 95, potassium: 4.0 },
    vitalsOverrides: { hr: 72, rr: 16, spo2: 99 },
  },
]

function baseCaseId(caseId: string): string {
  return caseId.split('::')[0]
}

function deltaText(base: number, next: number): string {
  const delta = next - base
  if (delta === 0) return 'No ESI change'
  if (delta < 0) return `${Math.abs(delta)} level more urgent`
  return `${delta} level less urgent`
}

function deltaTone(base: number, next: number): string {
  if (next < base) return 'worse'
  if (next > base) return 'better'
  return 'same'
}

export default function WhatIfSimulator({ result, apiBase }: { result: CaseResult; apiBase: string }) {
  const [scenarioResults, setScenarioResults] = useState<Record<string, CaseResult>>({ Current: result })
  const [loading, setLoading] = useState<string | null>(null)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    setScenarioResults({ Current: result })
    setLoading(null)
    setError('')
  }, [result.case_id])

  const runScenario = async (scenario: Scenario) => {
    if (scenario.name === 'Current') {
      setScenarioResults((prev) => ({ ...prev, Current: result }))
      return
    }

    setLoading(scenario.name)
    setError('')
    try {
      const res = await fetch(`${apiBase}/demo/analyze/${encodeURIComponent(baseCaseId(result.case_id))}/override`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scenario_name: scenario.name.toLowerCase(),
          lab_overrides: scenario.labOverrides,
          vitals_overrides: scenario.vitalsOverrides,
        }),
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.detail?.reason || body.detail || `HTTP ${res.status}`)
      }
      const data: CaseResult = await res.json()
      setScenarioResults((prev) => ({ ...prev, [scenario.name]: data }))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Scenario failed')
    } finally {
      setLoading(null)
    }
  }

  return (
    <div className="whatif-simulator">
      <div className="whatif-header">
        <div>
          <h3>What-If Simulator</h3>
          <p>Each scenario reruns the clinical pipeline with explicit lab and vital overrides.</p>
        </div>
        {error && <span className="whatif-error">{error}</span>}
      </div>

      <div className="whatif-grid">
        {SCENARIOS.map((scenario) => {
          const scenarioResult = scenarioResults[scenario.name]
          const running = loading === scenario.name
          const tone = scenarioResult ? deltaTone(result.esi_level, scenarioResult.esi_level) : 'same'

          return (
            <article key={scenario.name} className={`whatif-card whatif-card--${tone}`}>
              <div className="whatif-card-header">
                <div>
                  <span className="evidence-kicker">{scenario.label}</span>
                  <h4>{scenario.name}</h4>
                </div>
                {scenarioResult ? (
                  <span className={`esi-badge esi-${scenarioResult.esi_level}`}>ESI {scenarioResult.esi_level}</span>
                ) : (
                  <span className="whatif-pending">Not run</span>
                )}
              </div>

              <p className="whatif-intent">{scenario.intent}</p>

              <div className="whatif-delta">
                {tone === 'worse' && <TrendingUp size={14} />}
                {tone === 'better' && <TrendingDown size={14} />}
                {tone === 'same' && <Activity size={14} />}
                <span>{scenarioResult ? deltaText(result.esi_level, scenarioResult.esi_level) : 'Awaiting pipeline run'}</span>
              </div>

              <div className="whatif-overrides">
                <div>
                  <strong>Labs</strong>
                  {Object.keys(scenario.labOverrides).length === 0 ? (
                    <span>No changes</span>
                  ) : (
                    Object.entries(scenario.labOverrides).map(([key, value]) => (
                      <span key={key}>{key.toUpperCase()} to {value}</span>
                    ))
                  )}
                </div>
                <div>
                  <strong>Vitals</strong>
                  {Object.keys(scenario.vitalsOverrides).length === 0 ? (
                    <span>No changes</span>
                  ) : (
                    Object.entries(scenario.vitalsOverrides).map(([key, value]) => (
                      <span key={key}>{key.toUpperCase()} to {value}</span>
                    ))
                  )}
                </div>
              </div>

              {scenarioResult && (
                <div className="whatif-result-line">
                  {(scenarioResult.safety_flags ?? []).length === 0 ? <CheckCircle2 size={13} /> : <AlertTriangle size={13} />}
                  <span>
                    {(scenarioResult.lab_alerts ?? []).length} lab alerts, {(scenarioResult.safety_flags ?? []).length} safety flags, {scenarioResult.total_time_ms} ms
                  </span>
                </div>
              )}

              <button
                type="button"
                className="whatif-run-btn"
                onClick={() => runScenario(scenario)}
                disabled={running}
              >
                {running ? <Loader2 size={13} className="spin" /> : <Play size={13} />}
                {scenario.name === 'Current' ? 'Reset Baseline' : 'Run Scenario'}
              </button>
            </article>
          )
        })}
      </div>
    </div>
  )
}
