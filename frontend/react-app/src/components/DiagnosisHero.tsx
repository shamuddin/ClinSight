import { Stethoscope } from 'lucide-react'
import { CaseResult } from '../types'

function diagnosisWeight(result: CaseResult, diagnosis: string, index: number): number {
  const text = diagnosis.toLowerCase()
  const findingBoost = result.findings.some((finding) =>
    text.includes(finding.finding.replace(/_/g, ' ').toLowerCase()) ||
    finding.description.toLowerCase().includes(text.split(' ')[0] ?? ''),
  ) ? 20 : 0
  const labBoost = (result.lab_patterns ?? []).some((pattern) =>
    text.includes(pattern.replace(/_/g, ' ').toLowerCase().split(' ')[0] ?? ''),
  ) ? 14 : 0
  const safetyPenalty = (result.safety_flags ?? []).length * 4
  return Math.max(28, Math.min(96, 90 - index * 11 + findingBoost + labBoost - safetyPenalty))
}

export default function DiagnosisHero({ result }: { result: CaseResult }) {
  const primary = result.differential[0]
  const confidence = primary
    ? diagnosisWeight(result, primary, 0)
    : 0

  return (
    <div className="diagnosis-hero">
      {primary && (
        <div className="diagnosis-primary">
          <div className="diagnosis-primary-icon">
            <Stethoscope size={22} />
          </div>
          <div className="diagnosis-primary-text">
            <h3>{primary}</h3>
            <p>Primary differential diagnosis based on image + lab correlation</p>
          </div>
          <div className="diagnosis-confidence-ring">
            <span>{confidence}%</span>
          </div>
        </div>
      )}

      <div className="diagnosis-list">
        {result.differential.map((diagnosis, index) => {
          const weight = diagnosisWeight(result, diagnosis, index)
          return (
            <div key={diagnosis} className="diagnosis-chip">
              <span className="diagnosis-chip-rank">{index + 1}</span>
              <span className="diagnosis-chip-name">{diagnosis}</span>
              <div className="diagnosis-chip-bar-wrap">
                <div className="diagnosis-chip-bar" style={{ width: `${weight}%` }} />
              </div>
              <span className="diagnosis-chip-pct">{weight}%</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
