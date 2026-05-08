export interface DemoStep {
  caseId: string
  title: string
  narration: string
}

export const GRAND_DEMO_SEQUENCE: DemoStep[] = [
  { caseId: 'CS-2024-001', title: 'Critical chest pain — tension pneumothorax', narration: 'Rapid triage and immediate intervention for life-threatening respiratory compromise.' },
  { caseId: 'CS-2024-004', title: 'Sepsis with shock — altered mental status', narration: 'Multi-agent detection of sepsis cascade triggering rapid fluid resuscitation and antibiotics.' },
  { caseId: 'CS-2024-005', title: 'GI hemorrhage — hematemesis', narration: 'Massive upper GI bleed requiring emergent blood products and endoscopy.' },
  { caseId: 'CS-2024-002', title: 'Head trauma — brief LOC', narration: 'Concussion protocol with neuroimaging decision support.' },
  { caseId: 'CS-2024-007', title: 'Acute coronary syndrome', narration: 'Chest pain triage with ECG and troponin-guided pathway.' },
  { caseId: 'CS-2024-009', title: 'Poisoning/overdose', narration: 'Toxidrome identification with antidote recommendation.' },
  { caseId: 'CS-2024-008', title: 'Trauma — arterial laceration', narration: 'Hemorrhage control and vascular injury assessment.' },
  { caseId: 'CS-2024-010', title: 'Chemical eye injury', narration: 'Ocular emergency with irrigation and vision preservation.' },
  { caseId: 'CS-2024-006', title: 'Pediatric asthma exacerbation', narration: 'Bronchospasm management with safety guard for pediatric dosing.' },
  { caseId: 'CS-2024-003', title: 'Pediatric fever and rash', narration: 'Viral exanthem vs serious pediatric infection differential.' },
]

// 40 seconds per case for live 35B inference demo
export const DEMO_STEP_MS = 40000
