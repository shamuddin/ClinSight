import { useState } from 'react'
import {
  Shuffle,
  EyeOff,
  BarChart2,
  CheckCircle2,
  XCircle,
  Baby,
  ChevronDown,
  ChevronUp,
} from 'lucide-react'
import { CaseResult, SafetyFlag } from '../types'

// ── Metric card ───────────────────────────────────────────────────────────────

interface MetricCardProps {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  Icon:    any
  value:   string | number
  label:   string
  sub:     string
  isGood:  boolean
  flags?:  SafetyFlag[]
}

function MetricCard({ Icon, value, label, sub, isGood, flags }: MetricCardProps) {
  const [open, setOpen] = useState(false)
  const hasFlags = (flags?.length ?? 0) > 0

  return (
    <div
      className={`theater-card ${isGood ? 'theater-card--good' : 'theater-card--bad'}`}
      onClick={() => hasFlags && setOpen(o => !o)}
      role={hasFlags ? 'button' : undefined}
      aria-expanded={hasFlags ? open : undefined}
    >
      <div className="theater-card-header">
        <Icon size={14} className="theater-card-icon" />
        <span className="theater-card-label">{label}</span>
        {hasFlags && (
          <span className="theater-card-toggle">
            {open ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
          </span>
        )}
      </div>

      <div className={`theater-card-value ${isGood ? 'theater-value--good' : 'theater-value--bad'}`}>
        {value}
      </div>

      <div className="theater-card-sub">{sub}</div>

      {/* Status indicator dot */}
      <div className={`theater-card-indicator ${isGood ? 'indicator--good' : 'indicator--bad'}`} />

      {/* Expanded flag list */}
      {open && flags && flags.length > 0 && (
        <div className="theater-card-flags">
          {flags.map((f, i) => (
            <div key={i} className="theater-flag-item">
              <span className={`badge badge-${f.severity.toLowerCase()}`}>{f.severity}</span>
              <div className="theater-flag-content">
                <span className="theater-flag-rule">{f.rule}</span>
                <span className="theater-flag-msg">{f.message}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ── Main component ────────────────────────────────────────────────────────────

export default function SafetyTheater({ result }: { result: CaseResult }) {
  const { safety_flags, quality_gate, pediatric_gate } = result

  // Partition merged flags by category
  const contradictions = safety_flags.filter(f =>
    f.rule.includes('CONTRA') || f.rule.includes('NORM') || f.rule.includes('MISMATCH')
  )
  const hallucinations = safety_flags.filter(f =>
    f.rule.includes('GROUNDING') || f.rule.includes('SCOPE') || f.rule.includes('HALLUC')
  )
  const biasFlags = safety_flags.filter(f =>
    f.rule.startsWith('BIAS')
  )

  // Use server-provided counts (more accurate) with client-side fallback
  const contrCount = result.contradictions_count ?? contradictions.length
  const hallCount  = result.hallucination_count  ?? hallucinations.length
  const biasCount  = result.bias_count           ?? biasFlags.length

  const isPedWarn  = pediatric_gate.status === 'WARNING'
  const qSub       = quality_gate.pass
    ? (isPedWarn ? '⚠ Pediatric patient detected' : 'All checks passed')
    : (quality_gate.reasons?.join(', ') ?? 'Failed')

  return (
    <div className="safety-theater">

      {/* 4 metric cards */}
      <div className="theater-grid">

        <MetricCard
          Icon={Shuffle}
          value={contrCount}
          label="Contradictions"
          sub="Findings vs. labs vs. history"
          isGood={contrCount === 0}
          flags={contradictions}
        />

        <MetricCard
          Icon={EyeOff}
          value={hallCount}
          label="Hallucinations"
          sub="vs. reference pathology"
          isGood={hallCount === 0}
          flags={hallucinations}
        />

        <MetricCard
          Icon={BarChart2}
          value={biasCount}
          label="Bias Flags"
          sub="Demographic pattern audit"
          isGood={biasCount === 0}
          flags={biasFlags}
        />

        <MetricCard
          Icon={quality_gate.pass ? CheckCircle2 : XCircle}
          value={quality_gate.pass ? 'PASS' : 'FAIL'}
          label="Image Quality"
          sub={qSub}
          isGood={quality_gate.pass && !isPedWarn}
        />

      </div>

      {/* Pediatric banner if triggered */}
      {isPedWarn && (
        <div className="theater-ped-banner">
          <Baby size={14} />
          <span>
            <strong>Pediatric Patient</strong> — {pediatric_gate.message ?? 'Adult-trained model. Increased correlation required.'}
          </span>
        </div>
      )}

      {/* All-clear banner */}
      {safety_flags.length === 0 && !isPedWarn && (
        <div className="theater-allclear">
          <CheckCircle2 size={14} />
          All 4 safety guards passed — no flags raised
        </div>
      )}

      {/* Any remaining uncategorised flags */}
      {safety_flags.length > 0 && (
        <div className="theater-summary-line">
          {safety_flags.length} total merged flag{safety_flags.length !== 1 ? 's' : ''} ·
          {contrCount} contradictions ·
          {hallCount} hallucinations ·
          {biasCount} bias
        </div>
      )}

    </div>
  )
}
