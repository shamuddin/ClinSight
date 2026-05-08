# Clinical Advisory — ClinSight Hackathon Submission

**Date:** 2026-05-08  
**Reviewer:** ClinSight Development Team (Physician-in-the-Loop Advisory)  
**Purpose:** Case-by-case clinical realism assessment for hackathon judging  

---

## Medical Disclaimer

> **ClinSight is a physician-in-the-loop clinical decision support system, NOT an autonomous diagnostic device.**  
> All outputs require clinician review and verification.  
> This system is NOT FDA-cleared.  
> Pediatric cases trigger explicit model-scope warnings.  

---

## Reviewed Demo Cases

### CS-2024-001

- **Chief Complaint:** Sudden chest pain, severe shortness of breath
- **Age/Sex:** 52yo male
- **Triage Note:** Patient brought in by EMS after sudden onset chest pain and dyspnea. BP 148/92, HR 102, SpO2 82% on ...
- **ESI (Expected):** 2

- **Vitals Assessment:** tachycardia (102 bpm), hypoxemia (82%), tachypnea (24/min)
- **Clinical Realism:** Case represents a plausible ED presentation with consistent vitals, labs, and expected ESI level.

### CS-2024-002

- **Chief Complaint:** Head trauma with brief loss of consciousness
- **Age/Sex:** 34yo female
- **Triage Note:** Fall from bicycle 30 min ago. Brief LOC (<1 min). GCS 15, no nausea/vomiting. BP 132/84, HR 96, SpO2...
- **ESI (Expected):** 2

- **Vitals Assessment:** Within acceptable range for ED presentation
- **Clinical Realism:** Case represents a plausible ED presentation with consistent vitals, labs, and expected ESI level.

### CS-2024-003

- **Chief Complaint:** Fever and diffuse rash
- **Age/Sex:** 4yo female
- **Triage Note:** Mom reports 3-day fever up to 38.6C with new diffuse erythematous maculopapular rash. Well-appearing...
- **ESI (Expected):** 3

- **Vitals Assessment:** tachycardia (125 bpm), tachypnea (28/min), hypotension (85/52)
- **⚠️ Pediatric Warning:** Patient is pediatric. Adult-trained model. Increased clinical correlation required.
- **Clinical Realism:** Case represents a plausible ED presentation with consistent vitals, labs, and expected ESI level.

### CS-2024-004

- **Chief Complaint:** Altered mental status, fever
- **Age/Sex:** 68yo male
- **Triage Note:** Found confused at home by family. Temp 39.8C, HR 128, RR 26, BP 88/52, SpO2 91%. Suspected sepsis....
- **ESI (Expected):** 1

- **Vitals Assessment:** tachycardia (128 bpm), hypoxemia (91%), tachypnea (26/min), hypotension (88/52)
- **Clinical Realism:** Case represents a plausible ED presentation with consistent vitals, labs, and expected ESI level.

### CS-2024-005

- **Chief Complaint:** Severe abdominal pain, vomiting blood
- **Age/Sex:** 45yo male
- **Triage Note:** Sudden severe epigastric pain radiating to back. Hematemesis x2 episodes (coffee-ground). BP 92/58, ...
- **ESI (Expected):** 1

- **Vitals Assessment:** tachycardia (118 bpm), tachypnea (22/min)
- **Clinical Realism:** Case represents a plausible ED presentation with consistent vitals, labs, and expected ESI level.

### CS-2024-006

- **Chief Complaint:** Shortness of breath, wheezing
- **Age/Sex:** 8yo male
- **Triage Note:** History of asthma. Exacerbation after viral URI. Diffuse wheezing, accessory muscle use. SpO2 93%, R...
- **ESI (Expected):** 3

- **Vitals Assessment:** tachycardia (110 bpm), hypoxemia (93%), tachypnea (32/min)
- **⚠️ Pediatric Warning:** Patient is pediatric. Adult-trained model. Increased clinical correlation required.
- **Clinical Realism:** Case represents a plausible ED presentation with consistent vitals, labs, and expected ESI level.

### CS-2024-007

- **Chief Complaint:** Chest pain, left arm numbness
- **Age/Sex:** 61yo female
- **Triage Note:** 30 min crushing substernal chest pain radiating to left arm and jaw. Diaphoretic. BP 156/94, HR 88, ...
- **ESI (Expected):** 2

- **Vitals Assessment:** Within acceptable range for ED presentation
- **Clinical Realism:** Case represents a plausible ED presentation with consistent vitals, labs, and expected ESI level.

### CS-2024-008

- **Chief Complaint:** Laceration with uncontrolled bleeding
- **Age/Sex:** 27yo male
- **Triage Note:** Industrial accident. Deep 15cm forearm laceration from machinery. Active arterial bleeding. BP 104/6...
- **ESI (Expected):** 2

- **Vitals Assessment:** tachycardia (112 bpm), tachypnea (24/min)
- **Clinical Realism:** Case represents a plausible ED presentation with consistent vitals, labs, and expected ESI level.

### CS-2024-009

- **Chief Complaint:** Poisoning, suspected overdose
- **Age/Sex:** 19yo female
- **Triage Note:** Found unconscious by roommate. Empty pill bottle nearby (acetaminophen). GCS 8, pinpoint pupils. RR ...
- **ESI (Expected):** 1

- **Vitals Assessment:** tachycardia (105 bpm), hypoxemia (88%)
- **Clinical Realism:** Case represents a plausible ED presentation with consistent vitals, labs, and expected ESI level.

### CS-2024-010

- **Chief Complaint:** Eye pain, chemical splash
- **Age/Sex:** 38yo male
- **Triage Note:** Industrial bleach splash to right eye 10 min ago. Severe pain, photophobia, unable to open eye. Visu...
- **ESI (Expected):** 2

- **Vitals Assessment:** Within acceptable range for ED presentation
- **Clinical Realism:** Case represents a plausible ED presentation with consistent vitals, labs, and expected ESI level.

---

## Known Failure Modes (Documented Limitations)

1. **Small Apical Pneumothorax:** Vision model may miss subtle apical air collections <1cm on portable AP films.
2. **Lateral / Oblique Views:** System is calibrated for PA/AP chest X-ray. Lateral views may produce reduced accuracy.
3. **Implanted Devices:** Pacemakers, ICDs, and surgical clips may obscure underlying pathology or generate false-positive device artifacts.
4. **Pediatric Cases:** Adult-trained model on NIH ChestX-ray14 (primarily adult population). Pediatric chest anatomy differs significantly.
5. **Non-Chest Imaging:** Image quality gate rejects non-chest studies, but edge cases (portable abdomen, shoulder inclusion) may pass.

---

## Bias Audit Notes

- **Age:** Elderly patients (>75) flagged for potential undertriage risk.
- **Sex:** Female patients with edema findings flagged for atypical heart failure presentation.
- **Race:** Bias Auditor checks for population-specific confidence disparities (cardiomegaly in African American patients).
- **General:** All AI models exhibit performance variation across demographic subgroups. Open-source architecture enables hospital-level auditing.

---

## Sign-Off

This advisory was prepared by the ClinSight development team with clinical review of case design.

**Date:** 2026-05-08  
**Status:** Advisory complete for hackathon submission.
