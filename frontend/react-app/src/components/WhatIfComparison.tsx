import { useState } from 'react'
import { CaseResult } from '../types'

interface Scenario {
  name: string
  label: string
  lab_override: Record<string, number>
  vitals_override: Record<string, any>
}

const SCENARIOS: Scenario[] = [
  {
    name: 'Current',
    label: 'Current labs & vitals',
    lab_override: {},
    vitals_override: {},
  },
  {
    name: 'Worse',
    label: 'If labs worsen',
    lab_override: { wbc: 16.5, lactate: 5.2, pO2: 55, potassium: 5.8 },
    vitals_override: { hr: 130, rr: 28, spo2: 88 },
  },
  {
    name: 'Better',
    label: 'If labs improve',
    lab_override: { wbc: 7.0, lactate: 1.1, pO2: 95, potassium: 4.0 },
    vitals_override: { hr: 72, rr: 16, spo2: 99 },
  },
]

export default function WhatIfComparison({ result }: { result?: CaseResult }) {
  const [selected, setSelected] = useState<string>('Current')
  const scenario = SCENARIOS.find((s) => s.name === selected)!

  // Compute a mock ESI delta from lab overrides (simplified preview)
  const labCount = Object.keys(scenario.lab_override).length
  const mockEsi = labCount === 0 ? (result?.esi_level ?? 3) : labCount > 2 ? 1 : 2

  return (
    <div className="panel">
      <h2>What-If Comparison</h2>
      <p className="dim">Compare outcomes by adjusting lab values and vitals.</p>

      <div className="scenario-tabs">
        {SCENARIOS.map((s) => (
          <button
            key={s.name}
            className={`scenario-tab ${selected === s.name ? 'active' : ''}`}
            onClick={() => setSelected(s.name)}
          >
            {s.name}
          </button>
        ))}
      </div>

      <div className="scenario-grid">
        <div className="scenario-card">
          <strong>{scenario.label}</strong>
          <div className="scenario-esi">
            ESI: <span className={`esi-badge esi-${mockEsi}`}>{mockEsi}</span>
          </div>

          {Object.keys(scenario.lab_override).length > 0 && (
            <div className="scenario-labs">
              <h4>Adjusted Labs</h4>
              <ul>
                {Object.entries(scenario.lab_override).map(([k, v]) => (
                  <li key={k}>
                    <strong>{k.toUpperCase()}</strong> → {v}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {Object.keys(scenario.vitals_override).length > 0 && (
            <div className="scenario-vitals">
              <h4>Adjusted Vitals</h4>
              <ul>
                {Object.entries(scenario.vitals_override).map(([k, v]) => (
                  <li key={k}>
                    <strong>{k.toUpperCase()}</strong> → {v}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {result && scenario.name === 'Current' && (
        <div className="whatif-note dim">
          This compares the baseline scenario against the selected modifications.
          A real API call would re-run the full pipeline with adjusted inputs.
        </div>
      )}
    </div>
  )
}
