import type { CaseResult, DemoCase, Finding, LabAlert, SafetyFlag } from './types'

type OfflineCase = DemoCase & {
  lab_values: Record<string, number>
  lab_units: Record<string, string>
  patient_race: string
}

type OfflineProfile = {
  esi: number
  description: string
  findings: Finding[]
  labs: LabAlert[]
  differential: string[]
  actions: string[]
  safety: SafetyFlag[]
  labPatterns: string[]
}

export const OFFLINE_DEMO_CASES: OfflineCase[] = [
  {
    case_id: 'CS-2024-001',
    patient_age: 52,
    patient_sex: 'male',
    patient_race: 'White',
    chief_complaint: 'Chest pain',
    triage_note: '52M with substernal chest pressure radiating to left arm, nausea, and diaphoresis.',
    vitals: { bp: '148/92', hr: 102, rr: 20, spo2: 97, temp: 37.1 },
    lab_values: { troponin_i: 0.12, bnp: 180, crp: 12, wbc: 9.2 },
    lab_units: { troponin_i: 'ng/L', bnp: 'pg/mL', crp: 'mg/L', wbc: 'K/uL' },
  },
  {
    case_id: 'CS-2024-002',
    patient_age: 34,
    patient_sex: 'female',
    patient_race: 'Black',
    chief_complaint: 'Head trauma with brief LOC',
    triage_note: '34F restrained MVC driver with brief loss of consciousness, GCS 13, and scalp hematoma.',
    vitals: { bp: '132/84', hr: 96, rr: 18, spo2: 99, temp: 36.8 },
    lab_values: { glucose: 142, lactate: 1.8, platelets: 220, creatinine: 1.0 },
    lab_units: { glucose: 'mg/dL', lactate: 'mmol/L', platelets: 'K/uL', creatinine: 'mg/dL' },
  },
  {
    case_id: 'CS-2024-003',
    patient_age: 4,
    patient_sex: 'female',
    patient_race: 'Hispanic',
    chief_complaint: 'Fever and rash',
    triage_note: '4YO with fever to 39.4C and diffuse erythematous rash, tolerating PO.',
    vitals: { bp: '85/52', hr: 125, rr: 28, spo2: 98, temp: 38.6 },
    lab_values: { wbc: 11.5, hemoglobin: 11.2, platelets: 310, crp: 28 },
    lab_units: { wbc: 'K/uL', hemoglobin: 'g/dL', platelets: 'K/uL', crp: 'mg/L' },
  },
  {
    case_id: 'CS-2024-004',
    patient_age: 67,
    patient_sex: 'male',
    patient_race: 'White',
    chief_complaint: 'Altered mental status',
    triage_note: '67M nursing home resident with hypotension, oliguria, fever, and suspected UTI source.',
    vitals: { bp: '78/42', hr: 118, rr: 28, spo2: 91, temp: 38.9 },
    lab_values: { lactate: 5.2, creatinine: 2.4, platelets: 89, potassium: 5.8, wbc: 2.1 },
    lab_units: { lactate: 'mmol/L', creatinine: 'mg/dL', platelets: 'K/uL', potassium: 'mEq/L', wbc: 'K/uL' },
  },
  {
    case_id: 'CS-2024-005',
    patient_age: 28,
    patient_sex: 'female',
    patient_race: 'Asian',
    chief_complaint: 'Severe headache',
    triage_note: '28F with sudden worst-ever headache, photophobia, neck stiffness, and intact neuro exam.',
    vitals: { bp: '128/78', hr: 88, rr: 16, spo2: 99, temp: 37.2 },
    lab_values: { wbc: 7.1, crp: 2.0, esr: 8, platelets: 260 },
    lab_units: { wbc: 'K/uL', crp: 'mg/L', esr: 'mm/hr', platelets: 'K/uL' },
  },
  {
    case_id: 'CS-2024-006',
    patient_age: 55,
    patient_sex: 'male',
    patient_race: 'Hispanic',
    chief_complaint: 'Severe abdominal pain',
    triage_note: '55M with rigid abdomen, absent bowel sounds, tachycardia, and progressive diffuse pain.',
    vitals: { bp: '94/58', hr: 132, rr: 26, spo2: 95, temp: 37.8 },
    lab_values: { wbc: 16.5, lactate: 3.4, lipase: 38, creatinine: 1.1 },
    lab_units: { wbc: 'K/uL', lactate: 'mmol/L', lipase: 'U/L', creatinine: 'mg/dL' },
  },
]

const profiles: Record<string, OfflineProfile> = {
  'CS-2024-001': {
    esi: 2,
    description: 'Emergent cardiac rule-out with elevated troponin signal',
    findings: [
      { id: 'f1', finding: 'cardiomegaly', description: 'Mild enlarged cardiac silhouette', confidence: 0.84, severity: 'moderate', location: 'cardiac silhouette' },
      { id: 'f2', finding: 'vascular_congestion', description: 'Subtle central vascular congestion', confidence: 0.76, severity: 'moderate', location: 'perihilar' },
    ],
    labs: [
      { lab: 'Troponin I', value: 0.12, unit: 'ng/L', threshold: 0.04, code: 'troponin_i', description: 'Above ACS rule-out threshold', severity: 'critical' },
      { lab: 'CRP', value: 12, unit: 'mg/L', threshold: 10, code: 'crp', description: 'Inflammatory marker elevated', severity: 'warning' },
    ],
    differential: ['Acute coronary syndrome', 'Heart failure exacerbation', 'Non-cardiac chest pain'],
    actions: ['Immediate ECG and serial troponins', 'Cardiology review', 'Continuous telemetry'],
    safety: [],
    labPatterns: ['cardiac biomarker elevation', 'inflammation'],
  },
  'CS-2024-002': {
    esi: 2,
    description: 'High-risk head injury requiring rapid neuro imaging',
    findings: [
      { id: 'f1', finding: 'scalp_hematoma', description: 'Right parietal soft tissue swelling', confidence: 0.81, severity: 'moderate', location: 'right parietal' },
    ],
    labs: [
      { lab: 'Glucose', value: 142, unit: 'mg/dL', threshold: 140, code: 'glucose', description: 'Mild stress hyperglycemia', severity: 'warning' },
    ],
    differential: ['Intracranial hemorrhage', 'Concussion', 'Cervical spine injury'],
    actions: ['Non-contrast CT head', 'Neuro checks every 15 minutes', 'C-spine precautions'],
    safety: [{ rule: 'trauma_context', severity: 'moderate', message: 'LOC and GCS 13 require physician-led trauma pathway.' }],
    labPatterns: ['trauma stress response'],
  },
  'CS-2024-003': {
    esi: 3,
    description: 'Urgent pediatric fever/rash with explicit model-scope warning',
    findings: [
      { id: 'f1', finding: 'rash_distribution', description: 'Diffuse erythematous rash pattern documented from triage', confidence: 0.72, severity: 'moderate', location: 'trunk/extremities' },
    ],
    labs: [
      { lab: 'CRP', value: 28, unit: 'mg/L', threshold: 10, code: 'crp', description: 'Inflammation above threshold', severity: 'warning' },
      { lab: 'Hemoglobin', value: 11.2, unit: 'g/dL', threshold: 11.5, code: 'hemoglobin', description: 'Borderline low for context', severity: 'warning' },
    ],
    differential: ['Viral exanthem', 'Kawasaki disease', 'Scarlet fever'],
    actions: ['Pediatric review', 'Hydration and fever control', 'Escalate if mucosal or shock features emerge'],
    safety: [{ rule: 'pediatric_scope', severity: 'high', message: 'Pediatric case: adult-trained model requires clinician confirmation.' }],
    labPatterns: ['pediatric inflammation'],
  },
  'CS-2024-004': {
    esi: 1,
    description: 'Resuscitation: septic shock physiology with organ dysfunction',
    findings: [
      { id: 'f1', finding: 'pulmonary_opacity', description: 'Patchy basilar opacity may represent infectious source or edema', confidence: 0.79, severity: 'high', location: 'lung bases' },
      { id: 'f2', finding: 'low_volume', description: 'Low-volume film limits sensitivity', confidence: 0.68, severity: 'moderate', location: 'portable chest' },
    ],
    labs: [
      { lab: 'Lactate', value: 5.2, unit: 'mmol/L', threshold: 2, code: 'lactate', description: 'Severe hypoperfusion marker', severity: 'critical' },
      { lab: 'Creatinine', value: 2.4, unit: 'mg/dL', threshold: 1.3, code: 'creatinine', description: 'Acute kidney injury signal', severity: 'critical' },
      { lab: 'Platelets', value: 89, unit: 'K/uL', threshold: 150, code: 'platelets', description: 'Thrombocytopenia', severity: 'critical' },
    ],
    differential: ['Septic shock', 'Urosepsis with multiorgan dysfunction', 'Pneumonia with shock'],
    actions: ['Activate sepsis bundle now', 'Broad-spectrum antibiotics', 'Vasopressor and ICU escalation'],
    safety: [{ rule: 'critical_vitals', severity: 'high', message: 'Hypotension and lactate require immediate physician escalation.' }],
    labPatterns: ['shock', 'organ dysfunction', 'thrombocytopenia'],
  },
  'CS-2024-005': {
    esi: 2,
    description: 'Emergent headache red flags despite reassuring basic labs',
    findings: [
      { id: 'f1', finding: 'no_focal_deficit', description: 'No focal neurologic deficit reported, but red-flag history persists', confidence: 0.73, severity: 'moderate', location: 'neuro exam' },
    ],
    labs: [],
    differential: ['Subarachnoid hemorrhage', 'Meningitis', 'Migraine'],
    actions: ['Urgent CT/CTA pathway', 'Consider LP if imaging negative', 'Analgesia and neuro observation'],
    safety: [{ rule: 'red_flag_history', severity: 'high', message: 'Worst-ever sudden headache should not be downgraded by normal vitals.' }],
    labPatterns: ['normal inflammatory markers'],
  },
  'CS-2024-006': {
    esi: 2,
    description: 'Emergent surgical abdomen pattern with elevated lactate',
    findings: [
      { id: 'f1', finding: 'free_air_risk', description: 'Clinical rigidity raises concern for perforation despite limited imaging', confidence: 0.77, severity: 'high', location: 'abdomen' },
    ],
    labs: [
      { lab: 'WBC', value: 16.5, unit: 'K/uL', threshold: 11, code: 'wbc', description: 'Leukocytosis', severity: 'critical' },
      { lab: 'Lactate', value: 3.4, unit: 'mmol/L', threshold: 2, code: 'lactate', description: 'Hypoperfusion risk', severity: 'critical' },
    ],
    differential: ['Perforated viscus', 'Bowel ischemia', 'Severe intra-abdominal infection'],
    actions: ['Surgery consult now', 'NPO, IV fluids, antibiotics', 'CT abdomen/pelvis if stable'],
    safety: [{ rule: 'surgical_abdomen', severity: 'high', message: 'Rigid abdomen requires surgical review independent of model confidence.' }],
    labPatterns: ['infection', 'hypoperfusion'],
  },
}

export function getOfflineResult(caseId: string): CaseResult | null {
  const baseId = caseId.split('::')[0]
  const demoCase = OFFLINE_DEMO_CASES.find((item) => item.case_id === baseId)
  const profile = profiles[baseId]
  if (!demoCase || !profile) return null

  const auditLog = [
    { agent: 'coordinator', stage: 'offline_case_load', timestamp: '2026-05-06T00:00:00.000Z', details: 'Loaded contingency cache case', duration_ms: 4 },
    { agent: 'radiologist', stage: 'offline_image_review', timestamp: '2026-05-06T00:00:00.050Z', details: `${profile.findings.length} cached finding(s) linked`, duration_ms: 11 },
    { agent: 'lab_analyst', stage: 'offline_lab_review', timestamp: '2026-05-06T00:00:00.090Z', details: `${profile.labs.length} cached lab alert(s) linked`, duration_ms: 8 },
    { agent: 'safety', stage: 'offline_guard_review', timestamp: '2026-05-06T00:00:00.130Z', details: `${profile.safety.length} safety flag(s) surfaced`, duration_ms: 7 },
    { agent: 'documenter', stage: 'offline_report', timestamp: '2026-05-06T00:00:00.170Z', details: 'Prepared cached clinical handoff', duration_ms: 5 },
  ]

  return {
    case_id: demoCase.case_id,
    esi_level: profile.esi,
    esi_description: profile.description,
    findings: profile.findings,
    lab_alerts: profile.labs,
    differential: profile.differential,
    suggested_actions: profile.actions,
    safety_flags: profile.safety,
    report: { source: 'frontend_contingency_cache', generated_for: 'offline demo rehearsal' },
    audit_log: auditLog,
    quality_gate: { pass: true, reasons: [], dimensions: [1024, 1024], blur_variance: 144 },
    pediatric_gate: demoCase.patient_age < 18
      ? { status: 'WARNING', message: 'Pediatric case: clinician confirmation required.' }
      : { status: 'PASS' },
    lab_patterns: profile.labPatterns,
    attention_regions: profile.findings.map((finding, index) => ({
      finding_id: finding.id,
      x: 18 + index * 22,
      y: 20 + index * 10,
      w: 24,
      h: 22,
      confidence: finding.confidence,
    })),
    vitals: demoCase.vitals,
    triage_note: demoCase.triage_note,
    patient_age: demoCase.patient_age,
    patient_sex: demoCase.patient_sex,
    patient_race: demoCase.patient_race,
    chief_complaint: demoCase.chief_complaint,
    lab_values: demoCase.lab_values,
    lab_units: demoCase.lab_units,
    total_time_ms: 35,
    contradictions_count: 0,
    hallucination_count: 0,
    bias_count: profile.safety.some((flag) => flag.rule === 'pediatric_scope') ? 1 : 0,
  }
}
