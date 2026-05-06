export interface DemoStep {
  caseId: string
  title: string
  narration: string
}

export const GRAND_DEMO_SEQUENCE: DemoStep[] = [
  {
    caseId: 'CS-2024-001',
    title: 'Critical chest pain',
    narration: 'The pipeline catches elevated cardiac risk, cross-checks labs, and produces an immediate triage recommendation.',
  },
  {
    caseId: 'CS-2024-003',
    title: 'Pediatric safety gate',
    narration: 'A pediatric case triggers model-scope caution, keeping physician review front and center.',
  },
  {
    caseId: 'CS-2024-004',
    title: 'Sepsis deterioration',
    narration: 'Multimodal evidence converges across vitals, labs, imaging, and safety guards for an urgent handoff.',
  },
]

export const DEMO_STEP_MS = 10000
