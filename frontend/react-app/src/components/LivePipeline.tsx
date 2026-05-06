import { useState } from 'react'
import {
  ShieldCheck,
  ScanLine,
  FlaskConical,
  AlertTriangle,
  FileText,
  CheckCircle2,
  XCircle,
  Loader2,
  Circle,
} from 'lucide-react'
import { PipelineAgents, AgentId, CaseResult } from '../types'

// ── Agent node definitions ────────────────────────────────────────────────────

interface NodeDef {
  id:        AgentId
  name:      string
  shortName: string
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  Icon:      any
  subagents: string[]
}

const NODES: NodeDef[] = [
  {
    id:        'coordinator',
    name:      'Coordinator',
    shortName: 'Coord',
    Icon:      ShieldCheck,
    subagents: ['Image Quality Gate', 'Pediatric Safety Gate'],
  },
  {
    id:        'radiologist',
    name:      'Radiologist',
    shortName: 'Rad',
    Icon:      ScanLine,
    subagents: ['Image Prep', 'Pathology Analyzer'],
  },
  {
    id:        'lab_analyst',
    name:      'Lab Analyst',
    shortName: 'Lab',
    Icon:      FlaskConical,
    subagents: ['Critical Value Detector', 'Pattern Correlator'],
  },
  {
    id:        'safety',
    name:      'Safety',
    shortName: 'Safety',
    Icon:      AlertTriangle,
    subagents: ['Contradiction Checker', 'Hallucination Guard', 'Bias Auditor', 'Safety Merge'],
  },
  {
    id:        'documenter',
    name:      'Documenter',
    shortName: 'Doc',
    Icon:      FileText,
    subagents: ['ESI Scorer', 'Differential Builder'],
  },
]

// ── Summary line per agent ────────────────────────────────────────────────────

function summaryLine(nodeId: AgentId, summary: Record<string, unknown> | undefined, result: CaseResult | null): string {
  if (!summary && !result) return ''

  if (nodeId === 'coordinator') {
    const qPass = summary?.quality_pass ?? result?.quality_gate?.pass
    const ped   = summary?.pediatric_status ?? result?.pediatric_gate?.status
    const parts = []
    if (qPass !== undefined) parts.push(qPass ? 'Quality ✓' : 'Quality ✗')
    if (ped   !== undefined) parts.push(`Peds: ${ped}`)
    return parts.join(' · ')
  }
  if (nodeId === 'radiologist') {
    const fc = summary?.findings_count ?? result?.findings.length
    const rc = result?.attention_regions.length
    if (fc !== undefined) return `${fc} finding${fc !== 1 ? 's' : ''}${rc !== undefined ? ` · ${rc} regions` : ''}`
  }
  if (nodeId === 'lab_analyst') {
    const lc = summary?.lab_alerts_count ?? result?.lab_alerts.length
    const patterns = (summary?.patterns as string[] | undefined) ?? result?.lab_patterns ?? []
    if (lc !== undefined) return `${lc} alert${lc !== 1 ? 's' : ''}${patterns.length ? ` · ${patterns.join(', ')}` : ''}`
  }
  if (nodeId === 'safety') {
    const ft = summary?.flags_total ?? result?.safety_flags.length
    if (ft !== undefined) return `${ft} flag${ft !== 1 ? 's' : ''} · ${summary?.contradictions ?? result?.contradictions_count ?? 0} contra · ${summary?.hallucinations ?? result?.hallucination_count ?? 0} halluc`
  }
  if (nodeId === 'documenter') {
    const esi = summary?.esi_level ?? result?.esi_level
    const dc  = summary?.differential_count ?? result?.differential.length
    if (esi !== undefined) return `ESI ${esi} · ${dc ?? 0} differential`
  }
  return ''
}

// ── Timeline node circle ──────────────────────────────────────────────────────

function TimelineNode({
  node,
  agentState,
  result,
  expanded,
  onToggle,
}: {
  node:       NodeDef
  agentState: { status: string; elapsedMs?: number; summary?: Record<string, unknown> }
  result:     CaseResult | null
  expanded:   boolean
  onToggle:   () => void
}) {
  const { status, elapsedMs, summary } = agentState
  const isComplete = status === 'complete'
  const isRunning  = status === 'running'
  const isPending  = status === 'pending'
  const isError    = status === 'error'

  const hint = isComplete ? summaryLine(node.id, summary, result) : ''

  return (
    <div
      className={[
        'timeline-node',
        `timeline-node--${status}`,
      ].join(' ')}
      onClick={isComplete ? onToggle : undefined}
      role={isComplete ? 'button' : undefined}
      aria-expanded={isComplete ? expanded : undefined}
    >
      {/* Circle indicator */}
      <div className="timeline-node-circle-wrap">
        <div className={`timeline-node-circle timeline-node-circle--${status}`}>
          {isComplete && <CheckCircle2 size={14} color="#fff" />}
          {isError && <XCircle size={14} color="#fff" />}
          {isRunning && <Loader2 size={14} color="#000" className="spin" />}
          {isPending && <Circle size={14} color="#a3a3a3" />}
        </div>
      </div>

      {/* Label */}
      <div className="timeline-node-label">{node.name}</div>

      {/* Time */}
      {isComplete && elapsedMs !== undefined && (
        <div className="timeline-node-time">{elapsedMs} ms</div>
      )}

      {/* Summary */}
      {hint && <div className="timeline-node-hint">{hint}</div>}

      {/* Expanded subagents */}
      {expanded && (
        <div className="timeline-node-expanded">
          <ul className="timeline-subagents">
            {node.subagents.map(s => (
              <li key={s} className="timeline-subagent">
                <CheckCircle2 size={10} color="#000" />
                {s}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

// ── Connector line between nodes ──────────────────────────────────────────────

function TimelineConnector({ lit }: { lit: boolean }) {
  return (
    <div className={`timeline-connector ${lit ? 'timeline-connector--lit' : ''}`}>
      <div className="timeline-connector-line" />
    </div>
  )
}

// ── Main component ────────────────────────────────────────────────────────────

interface LivePipelineProps {
  agents:    PipelineAgents
  result:    CaseResult | null
  streaming: boolean
}

export default function LivePipeline({ agents, result, streaming }: LivePipelineProps) {
  const [expanded, setExpanded] = useState<AgentId | null>(null)

  const toggle = (id: AgentId) => setExpanded(prev => prev === id ? null : id)

  const totalNodes  = NODES.length
  const doneCount   = NODES.filter(n => agents[n.id]?.status === 'complete').length
  const totalMs     = result?.total_time_ms

  return (
    <div className="live-pipeline">

      {/* Progress strip */}
      <div className="pipeline-progress">
        <div
          className="pipeline-progress-bar"
          style={{ width: `${(doneCount / totalNodes) * 100}%` }}
        />
      </div>

      {/* Timeline */}
      <div className="timeline-flow" role="list">
        {NODES.map((node, i) => {
          const agentState = agents[node.id] ?? { status: 'pending' }
          const prevComplete = i === 0 || agents[NODES[i - 1].id]?.status === 'complete'

          return (
            <div key={node.id} className="timeline-flow-item" role="listitem">
              <TimelineNode
                node={node}
                agentState={agentState}
                result={result}
                expanded={expanded === node.id}
                onToggle={() => toggle(node.id)}
              />
              {i < NODES.length - 1 && (
                <TimelineConnector lit={prevComplete && agentState.status === 'complete'} />
              )}
            </div>
          )
        })}
      </div>

      {/* Footer */}
      <div className="pipeline-footer">
        {streaming && (
          <span className="pipeline-streaming-badge">
            <Loader2 size={10} className="spin" />
            Pipeline running…
          </span>
        )}
        {!streaming && totalMs !== undefined && (
          <span className="pipeline-total-time">
            Total pipeline: <strong>{totalMs} ms</strong>
          </span>
        )}
        {!streaming && doneCount === totalNodes && (
          <span className="pipeline-done-badge">All {totalNodes} agents complete ✓</span>
        )}
      </div>
    </div>
  )
}
