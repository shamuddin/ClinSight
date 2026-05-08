// Types shared across frontend components

export interface Finding {
  id: string
  finding: string
  description: string
  confidence: number
  severity: string
  location: string
}

export interface AttentionRegion {
  finding_id: string
  x: number
  y: number
  w: number
  h: number
  confidence: number
}

export interface LabAlert {
  lab: string
  value: number
  unit: string
  threshold: number
  code: string
  description: string
  severity: string
}

export interface SafetyFlag {
  rule: string
  severity: string
  message: string
  confidence_penalty?: number
  finding_id?: string
}

export interface AuditEntry {
  agent: string
  stage: string
  timestamp: string
  details: string
  duration_ms?: number
}

export interface QualityGate {
  pass: boolean
  reasons: string[]
  dimensions?: number[]
  blur_variance?: number
}

export interface PediatricGate {
  status: string
  message?: string
}

export interface CaseResult {
  case_id: string
  esi_level: number
  esi_description: string
  findings: Finding[]
  lab_alerts: LabAlert[]
  differential: string[]
  suggested_actions: string[]
  safety_flags: SafetyFlag[]
  report: Record<string, unknown>
  audit_log: AuditEntry[]
  quality_gate: QualityGate
  pediatric_gate: PediatricGate
  lab_patterns: string[]
  attention_regions: AttentionRegion[]
  vitals: Record<string, unknown>
  triage_note: string
  patient_age: number
  patient_sex: string
  patient_race: string
  chief_complaint: string
  lab_values: Record<string, number>
  lab_units: Record<string, string>
  total_time_ms: number
  cached?: boolean
  // Safety sub-counts (from SafetyTheater)
  contradictions_count: number
  hallucination_count: number
  bias_count: number
  // Image URL for real X-ray display
  image_url?: string
}

export interface DemoCase {
  case_id: string
  patient_age: number
  patient_sex: string
  chief_complaint: string
  triage_note: string
  vitals: Record<string, unknown>
}

// ── Pipeline streaming types ──────────────────────────────────────────────────

export type AgentId =
  | 'coordinator'
  | 'radiologist'
  | 'lab_analyst'
  | 'safety'
  | 'documenter'

export type AgentStatus = 'pending' | 'running' | 'complete' | 'error'

export interface AgentNodeState {
  status: AgentStatus
  elapsedMs?: number
  summary?: Record<string, unknown>
}

export type PipelineAgents = Record<AgentId, AgentNodeState>
