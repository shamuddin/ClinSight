#!/usr/bin/env python3
"""Generate 50 chest X-ray demo cases and ground truth."""

import json
import random

random.seed(42)

# ─── 50 Chest X-ray case templates ─────────────────────────────────────────

CASE_TEMPLATES = [
    # ESI 1 (critical)
    {"esi": 1, "complaint": "Severe dyspnea and chest pain", "finding": "Cardiomegaly with pulmonary edema", "findings": ["cardiomegaly", "pulmonary_edema"], "diff": ["Acute decompensated CHF", "Cardiogenic shock", "Acute pulmonary edema", "Myocardial infarction"], "labs": {"wbc": 12.5, "crp": 45, "bnp": 850, "troponin_i": 0.85, "creatinine": 1.4, "glucose": 142, "hemoglobin": 13.2, "platelets": 220, "sodium": 135, "potassium": 5.1}, "vitals": {"bp": "78/52", "hr": 132, "rr": 34, "spo2": 84, "temp": 36.8}, "note": "68M acute onset severe dyspnea, orthopnea, pink frothy sputum. History of CHF."},
    {"esi": 1, "complaint": "Sudden chest pain and collapse", "finding": "Tension pneumothorax with mediastinal shift", "findings": ["tension_pneumothorax", "mediastinal_shift", "tracheal_deviation"], "diff": ["Tension pneumothorax", "Massive hemothorax", "Cardiac tamponade", "Aortic dissection"], "labs": {"wbc": 9.0, "crp": 8, "lactate": 4.2, "creatinine": 1.1, "glucose": 110, "hemoglobin": 11.5, "platelets": 280, "sodium": 138, "potassium": 4.0}, "vitals": {"bp": "65/40", "hr": 145, "rr": 38, "spo2": 72, "temp": 36.5}, "note": "24M tall thin male sudden L-sided chest pain after lifting weights, rapidly deteriorating."},
    {"esi": 1, "complaint": "Massive hemoptysis", "finding": "Cavitary lesion with air-fluid level", "findings": ["cavitary_lesion", "air_fluid_level", "consolidation"], "diff": ["Tuberculosis", "Lung abscess", "Cavitating lung cancer", "Wegener granulomatosis"], "labs": {"wbc": 18.5, "crp": 120, "creatinine": 0.9, "glucose": 95, "hemoglobin": 8.2, "platelets": 450, "sodium": 140, "potassium": 3.8}, "vitals": {"bp": "90/60", "hr": 128, "rr": 32, "spo2": 88, "temp": 38.9}, "note": "45M active smoker coughing 300mL blood over 2 hours. Weight loss 10kg over 3 months."},
    {"esi": 1, "complaint": "Chest pain after MVC", "finding": "Multiple rib fractures with hemothorax", "findings": ["rib_fractures", "hemothorax", "pulmonary_contusion"], "diff": ["Traumatic hemothorax", "Flail chest", "Pulmonary contusion", "Aortic injury"], "labs": {"wbc": 14.0, "crp": 25, "creatinine": 1.0, "glucose": 130, "hemoglobin": 10.5, "platelets": 200, "sodium": 138, "potassium": 4.2}, "vitals": {"bp": "85/55", "hr": 125, "rr": 30, "spo2": 90, "temp": 36.6}, "note": "32M high-speed MVC, restrained. Severe R chest wall tenderness, crepitus, decreased breath sounds R."},
    {"esi": 1, "complaint": "Severe sepsis with respiratory failure", "finding": "Bilateral diffuse infiltrates (ARDS pattern)", "findings": ["bilateral_infiltrates", "ards_pattern", "consolidation"], "diff": ["ARDS", "Severe pneumonia", "Septic shock with DIC", "Aspiration pneumonitis"], "labs": {"wbc": 2.5, "crp": 280, "lactate": 6.8, "creatinine": 2.4, "glucose": 180, "hemoglobin": 9.8, "platelets": 85, "sodium": 132, "potassium": 5.5}, "vitals": {"bp": "70/45", "hr": 155, "rr": 40, "spo2": 68, "temp": 39.5}, "note": "58F post-op day 3 after colectomy, sudden severe dyspnea, hypoxemic respiratory failure."},
    {"esi": 1, "complaint": " Crushing chest pain radiating to back", "finding": "Widened mediastinum with pleural effusion", "findings": ["widened_mediastinum", "pleural_effusion", "left_apical_capping"], "diff": ["Aortic dissection (Stanford A)", "Traumatic aortic rupture", "Mediastinal hematoma", "Pericardial tamponade"], "labs": {"wbc": 11.0, "crp": 15, "d_dimer": 4500, "creatinine": 1.3, "glucose": 125, "hemoglobin": 12.8, "platelets": 210, "sodium": 138, "potassium": 4.3}, "vitals": {"bp": "195/120", "hr": 110, "rr": 26, "spo2": 94, "temp": 36.7}, "note": "67M tearing chest pain radiating to interscapular region, BP differential 40mmHg between arms."},
    # ESI 2 (emergent)
    {"esi": 2, "complaint": "Pleuritic chest pain and dyspnea", "finding": "Right lower lobe pneumonia with pleural effusion", "findings": ["consolidation", "pleural_effusion", "air_bronchogram"], "diff": ["Community-acquired pneumonia", "Parapneumonic effusion", "Pulmonary embolism", "Lung abscess"], "labs": {"wbc": 16.8, "crp": 180, "creatinine": 0.9, "glucose": 105, "hemoglobin": 13.5, "platelets": 310, "sodium": 139, "potassium": 3.9}, "vitals": {"bp": "118/76", "hr": 108, "rr": 24, "spo2": 91, "temp": 39.1}, "note": "55M 4-day productive cough, fever, sharp R pleuritic chest pain. Former smoker."},
    {"esi": 2, "complaint": "Spontaneous pneumothorax", "finding": "Left apical pneumothorax with 35% collapse", "findings": ["pneumothorax", "visceral_pleural_line", "lung_collapse"], "diff": ["Primary spontaneous pneumothorax", "Secondary pneumothorax (COPD)", "Pneumocystis pneumonia", "Lymphangioleiomyomatosis"], "labs": {"wbc": 8.5, "crp": 12, "creatinine": 0.8, "glucose": 95, "hemoglobin": 14.2, "platelets": 250, "sodium": 140, "potassium": 4.1}, "vitals": {"bp": "128/82", "hr": 98, "rr": 22, "spo2": 93, "temp": 37.0}, "note": "19M tall thin male sudden L chest pain and dyspnea while playing basketball. No trauma."},
    {"esi": 2, "complaint": "Progressive dyspnea on exertion", "finding": "Large left pleural effusion with mediastinal shift", "findings": ["pleural_effusion", "mediastinal_shift", "blunting_costophrenic_angle"], "diff": ["Malignant pleural effusion", "Empyema", "Tuberculous pleuritis", "Chylothorax"], "labs": {"wbc": 9.2, "crp": 65, "creatinine": 1.0, "glucose": 102, "hemoglobin": 11.8, "platelets": 380, "sodium": 138, "potassium": 3.7}, "vitals": {"bp": "132/84", "hr": 102, "rr": 24, "spo2": 90, "temp": 37.5}, "note": "62F 3-week progressive dyspnea, 15kg weight loss, night sweats. Former smoker 40 pack-years."},
    {"esi": 2, "complaint": "Chest pain with ST elevation", "finding": "Cardiomegaly with cephalization of vessels", "findings": ["cardiomegaly", "cephalization", "interstitial_edema"], "diff": ["Acute STEMI", "Acute pulmonary edema", "Hypertensive emergency", "Aortic dissection"], "labs": {"wbc": 10.5, "crp": 22, "bnp": 1200, "troponin_i": 2.5, "creatinine": 1.1, "glucose": 145, "hemoglobin": 13.8, "platelets": 240, "sodium": 136, "potassium": 4.8}, "vitals": {"bp": "165/105", "hr": 115, "rr": 26, "spo2": 89, "temp": 37.0}, "note": "71M crushing substernal chest pain 2 hours, radiating to L jaw. Diaphoretic, nauseated."},
    {"esi": 2, "complaint": "Fever and productive cough", "finding": "Right upper lobe consolidation with cavitation", "findings": ["consolidation", "cavitation", "air_fluid_level"], "diff": ["Lung abscess", "Necrotizing pneumonia", "Cavitating TB", "Cavitating lung cancer"], "labs": {"wbc": 22.0, "crp": 250, "creatinine": 1.0, "glucose": 110, "hemoglobin": 12.5, "platelets": 420, "sodium": 138, "potassium": 3.5}, "vitals": {"bp": "125/78", "hr": 115, "rr": 28, "spo2": 89, "temp": 39.8}, "note": "48M alcoholic, 1-week productive cough with foul-smelling sputum, fevers, night sweats."},
    {"esi": 2, "complaint": "Acute asthma exacerbation", "finding": "Hyperinflated lungs with flattened diaphragms", "findings": ["hyperinflation", "flattened_diaphragms", "increased_retrosternal_space"], "diff": ["Severe asthma exacerbation", "COPD exacerbation", "Anaphylaxis", "Foreign body aspiration"], "labs": {"wbc": 11.5, "crp": 18, "creatinine": 0.9, "glucose": 115, "hemoglobin": 14.0, "platelets": 260, "sodium": 140, "potassium": 3.8}, "vitals": {"bp": "138/88", "hr": 118, "rr": 30, "spo2": 88, "temp": 37.2}, "note": "28F known asthmatic, exposure to cats, severe wheeze, using accessory muscles, cannot speak in full sentences."},
    {"esi": 2, "complaint": "Hemoptysis and weight loss", "finding": "Right hilar mass with post-obstructive pneumonia", "findings": ["hilar_mass", "post_obstructive_pneumonia", "atelectasis"], "diff": ["Lung cancer (NSCLC)", "Carcinoid tumor", "Lymphoma", "Benign lung tumor"], "labs": {"wbc": 12.0, "crp": 45, "creatinine": 0.9, "glucose": 98, "hemoglobin": 10.2, "platelets": 350, "sodium": 138, "potassium": 4.0}, "vitals": {"bp": "128/78", "hr": 95, "rr": 20, "spo2": 92, "temp": 37.3}, "note": "58M 40 pack-year smoker, 3-month cough, 12kg weight loss, intermittent hemoptysis."},
    {"esi": 2, "complaint": "Chest pain after long flight", "finding": "Westermark sign with Hampton hump", "findings": ["westermark_sign", "hampton_hump", "pleural_effusion"], "diff": ["Pulmonary embolism", "Pneumonia", "Pneumothorax", "Musculoskeletal chest pain"], "labs": {"wbc": 9.5, "crp": 25, "d_dimer": 3200, "creatinine": 0.9, "glucose": 100, "hemoglobin": 13.5, "platelets": 210, "sodium": 140, "potassium": 4.1}, "vitals": {"bp": "120/80", "hr": 118, "rr": 24, "spo2": 91, "temp": 37.0}, "note": "42F 14-hour flight yesterday, sudden pleuritic chest pain, mild hemoptysis, tachypneic."},
    {"esi": 2, "complaint": "Traumatic chest wall injury", "finding": "Multiple left rib fractures with pulmonary contusion", "findings": ["rib_fractures", "pulmonary_contusion", "subcutaneous_emphysema"], "diff": ["Pulmonary contusion", "Flail chest", "Hemothorax", "Pneumothorax"], "labs": {"wbc": 14.5, "crp": 35, "creatinine": 1.0, "glucose": 120, "hemoglobin": 11.8, "platelets": 230, "sodium": 138, "potassium": 4.2}, "vitals": {"bp": "115/72", "hr": 108, "rr": 26, "spo2": 90, "temp": 36.8}, "note": "35M fall from ladder 6m, L chest wall deformity, severe tenderness, subcutaneous crepitus."},
    # ESI 3 (urgent)
    {"esi": 3, "complaint": "Fever and cough", "finding": "Right middle lobe consolidation", "findings": ["consolidation", "air_bronchogram", "silhouette_sign"], "diff": ["Community-acquired pneumonia", "Atypical pneumonia", "Pulmonary infarction", "Lung contusion"], "labs": {"wbc": 14.2, "crp": 95, "creatinine": 0.8, "glucose": 105, "hemoglobin": 13.8, "platelets": 280, "sodium": 140, "potassium": 4.0}, "vitals": {"bp": "128/82", "hr": 102, "rr": 22, "spo2": 93, "temp": 38.7}, "note": "38M 5-day cough with yellow sputum, fever, pleuritic R chest pain. No comorbidities."},
    {"esi": 3, "complaint": "Chronic cough and dyspnea", "finding": "Hyperinflated lungs with bullae", "findings": ["hyperinflation", "bullae", "flattened_diaphragms"], "diff": ["COPD exacerbation", "Emphysema", "Alpha-1 antitrypsin deficiency", "Bronchiectasis"], "labs": {"wbc": 10.5, "crp": 28, "creatinine": 1.0, "glucose": 110, "hemoglobin": 15.2, "platelets": 240, "sodium": 138, "potassium": 4.3}, "vitals": {"bp": "145/90", "hr": 95, "rr": 20, "spo2": 91, "temp": 37.0}, "note": "65M 40 pack-year smoker, progressive dyspnea 2 years, chronic productive cough, barrel chest."},
    {"esi": 3, "complaint": "Pleuritic chest pain", "finding": "Small left apical pneumothorax (~15%)", "findings": ["pneumothorax", "visceral_pleural_line", "apical_bullae"], "diff": ["Primary spontaneous pneumothorax", "Apical bullous disease", "Marfan syndrome", "Lymphangioleiomyomatosis"], "labs": {"wbc": 8.0, "crp": 5, "creatinine": 0.8, "glucose": 95, "hemoglobin": 14.5, "platelets": 250, "sodium": 140, "potassium": 4.0}, "vitals": {"bp": "130/82", "hr": 88, "rr": 18, "spo2": 96, "temp": 36.8}, "note": "22M tall thin male, sudden L-sided pleuritic pain at rest. Mild dyspnea. No trauma."},
    {"esi": 3, "complaint": "Recurrent pneumonia", "finding": "Right lower lobe collapse with volume loss", "findings": ["atelectasis", "volume_loss", "elevated_hemidiaphragm"], "diff": ["Post-obstructive atelectasis", "Mucus plugging", "Foreign body aspiration", "Endobronchial tumor"], "labs": {"wbc": 12.0, "crp": 55, "creatinine": 0.9, "glucose": 100, "hemoglobin": 12.5, "platelets": 300, "sodium": 139, "potassium": 4.1}, "vitals": {"bp": "125/78", "hr": 95, "rr": 20, "spo2": 94, "temp": 37.8}, "note": "52F 3 episodes R lower lobe pneumonia in 6 months. Persistent cough, low-grade fever."},
    {"esi": 3, "complaint": "Intermittent hemoptysis", "finding": "Cavitary lesion in right upper lobe", "findings": ["cavitary_lesion", "upper_lobe_predilection", "fibrotic_changes"], "diff": ["Reactivation tuberculosis", "Lung abscess", "Cavitating lung cancer", "Aspergilloma"], "labs": {"wbc": 9.5, "crp": 40, "creatinine": 0.9, "glucose": 95, "hemoglobin": 11.5, "platelets": 280, "sodium": 140, "potassium": 3.9}, "vitals": {"bp": "118/76", "hr": 92, "rr": 18, "spo2": 95, "temp": 37.5}, "note": "35M recent immigrant, night sweats, weight loss 8kg, intermittent blood-streaked sputum."},
    {"esi": 3, "complaint": "Dyspnea on exertion", "finding": "Bilateral interstitial infiltrates with honeycombing", "findings": ["interstitial_infiltrates", "honeycombing", "reticular_pattern"], "diff": ["Idiopathic pulmonary fibrosis", "Connective tissue disease ILD", "Asbestosis", "Hypersensitivity pneumonitis"], "labs": {"wbc": 8.5, "crp": 35, "creatinine": 1.0, "glucose": 100, "hemoglobin": 13.8, "platelets": 220, "sodium": 140, "potassium": 4.2}, "vitals": {"bp": "135/85", "hr": 95, "rr": 20, "spo2": 90, "temp": 36.9}, "note": "68M progressive exertional dyspnea 18 months, dry cough, Velcro crackles at bases bilaterally."},
    {"esi": 3, "complaint": "Chest pain after cocaine use", "finding": "Pneumomediastinum with subcutaneous emphysema", "findings": ["pneumomediastinum", "subcutaneous_emphysema", "continuous_diaphragm_sign"], "diff": ["Cocaine-induced pneumomediastinum", "Esophageal rupture (Boerhaave)", "Traumatic pneumomediastinum", "Asthma exacerbation"], "labs": {"wbc": 11.0, "crp": 15, "creatinine": 1.1, "glucose": 110, "hemoglobin": 14.0, "platelets": 240, "sodium": 138, "potassium": 4.5}, "vitals": {"bp": "155/95", "hr": 125, "rr": 24, "spo2": 94, "temp": 37.2}, "note": "29M chest pain and neck swelling after cocaine use. Hamman crunch on auscultation."},
    {"esi": 3, "complaint": "Productive cough and fever", "finding": "Left lower lobe consolidation with air bronchograms", "findings": ["consolidation", "air_bronchogram", "silhouette_sign"], "diff": ["Lobar pneumonia", "Atypical pneumonia", "Pulmonary infarction", "Cryptogenic organizing pneumonia"], "labs": {"wbc": 15.5, "crp": 120, "creatinine": 0.9, "glucose": 105, "hemoglobin": 13.5, "platelets": 290, "sodium": 139, "potassium": 3.8}, "vitals": {"bp": "132/84", "hr": 105, "rr": 22, "spo2": 93, "temp": 38.9}, "note": "45F 4-day fever, productive cough with rust-colored sputum, pleuritic L chest pain."},
    {"esi": 3, "complaint": "Shortness of breath", "finding": "Bilateral pleural effusions with cardiomegaly", "findings": ["pleural_effusion", "cardiomegaly", "cephalization"], "diff": ["Congestive heart failure", "Nephrotic syndrome", "Liver cirrhosis", "Constrictive pericarditis"], "labs": {"wbc": 8.0, "crp": 12, "bnp": 680, "creatinine": 1.3, "glucose": 110, "hemoglobin": 12.5, "platelets": 200, "sodium": 133, "potassium": 4.8}, "vitals": {"bp": "142/88", "hr": 98, "rr": 22, "spo2": 91, "temp": 36.8}, "note": "74F worsening dyspnea, orthopnea, bilateral ankle edema. Known CHF, non-compliant with meds."},
    {"esi": 3, "complaint": "Chronic cough with blood-streaked sputum", "finding": "Cavitary lesion with fungus ball", "findings": ["cavitary_lesion", "fungus_ball", "air_crescent_sign"], "diff": ["Aspergilloma", "Lung abscess", "Cavitating TB", "Cavitating lung cancer"], "labs": {"wbc": 10.0, "crp": 30, "creatinine": 0.9, "glucose": 100, "hemoglobin": 12.8, "platelets": 260, "sodium": 140, "potassium": 4.0}, "vitals": {"bp": "128/80", "hr": 88, "rr": 18, "spo2": 95, "temp": 37.0}, "note": "50F prior TB history, chronic cavitary lesion, now with hemoptysis. Weight stable."},
    {"esi": 3, "complaint": "Chest tightness and wheeze", "finding": "Peribronchial cuffing with diffuse infiltrates", "findings": ["peribronchial_cuffing", "diffuse_infiltrates", "hyperinflation"], "diff": ["Acute bronchitis", "Viral pneumonia", "Asthma exacerbation", "COPD exacerbation"], "labs": {"wbc": 11.0, "crp": 45, "creatinine": 0.8, "glucose": 100, "hemoglobin": 14.0, "platelets": 250, "sodium": 140, "potassium": 4.0}, "vitals": {"bp": "130/84", "hr": 95, "rr": 20, "spo2": 94, "temp": 37.5}, "note": "33M URI symptoms 1 week, now with chest tightness, diffuse wheeze, productive cough."},
    {"esi": 3, "complaint": "Unilateral pleural effusion workup", "finding": "Large right pleural effusion with meniscus sign", "findings": ["pleural_effusion", "meniscus_sign", "blunting_costophrenic_angle"], "diff": ["Malignant pleural effusion", "Parapneumonic effusion", "Tuberculous pleuritis", "Pulmonary embolism with infarction"], "labs": {"wbc": 9.0, "crp": 55, "creatinine": 1.0, "glucose": 95, "hemoglobin": 11.5, "platelets": 350, "sodium": 138, "potassium": 3.7}, "vitals": {"bp": "125/78", "hr": 95, "rr": 20, "spo2": 93, "temp": 37.3}, "note": "60F 2-week progressive dyspnea, dullness to percussion R base, decreased breath sounds R."},
    # ESI 4 (less urgent)
    {"esi": 4, "complaint": "Mild cough and low-grade fever", "finding": "Subtle right lower lobe patchy infiltrate", "findings": ["patchy_infiltrate", "subtle_consolidation"], "diff": ["Early pneumonia", "Atypical pneumonia", "Viral bronchitis", "Post-infectious cough"], "labs": {"wbc": 11.0, "crp": 35, "creatinine": 0.8, "glucose": 95, "hemoglobin": 14.0, "platelets": 250, "sodium": 140, "potassium": 4.0}, "vitals": {"bp": "120/78", "hr": 85, "rr": 16, "spo2": 97, "temp": 37.8}, "note": "25F 3-day cough, mild fever, otherwise well. No comorbidities. Works as teacher."},
    {"esi": 4, "complaint": "Chest wall pain after minor trauma", "finding": "Isolated left 6th rib fracture", "findings": ["rib_fracture", "cortical_disruption"], "diff": ["Rib fracture", "Costochondritis", "Muscle strain", "Pneumothorax"], "labs": {"wbc": 8.5, "crp": 15, "creatinine": 0.8, "glucose": 95, "hemoglobin": 13.8, "platelets": 240, "sodium": 140, "potassium": 4.0}, "vitals": {"bp": "125/80", "hr": 80, "rr": 16, "spo2": 98, "temp": 36.8}, "note": "30M minor MVC, seatbelt on, focal L chest wall tenderness over 6th rib. No dyspnea."},
    {"esi": 4, "complaint": "Routine follow-up chest X-ray", "finding": "Stable small pulmonary nodule (8mm)", "findings": ["pulmonary_nodule", "well_circumscribed"], "diff": ["Benign pulmonary nodule", "Granuloma", "Hamartoma", "Early lung cancer"], "labs": {"wbc": 7.5, "crp": 5, "creatinine": 0.8, "glucose": 90, "hemoglobin": 14.2, "platelets": 230, "sodium": 140, "potassium": 4.0}, "vitals": {"bp": "118/76", "hr": 72, "rr": 14, "spo2": 98, "temp": 36.6}, "note": "55F incidental 8mm nodule found on pre-op CXR 6 months ago. Asymptomatic, smoker 10 pack-years."},
    {"esi": 4, "complaint": "Mild dyspnea on exertion", "finding": "Mild cardiomegaly without pulmonary congestion", "findings": ["cardiomegaly", "normal_vascularity"], "diff": ["Mild cardiomegaly", "Hypertensive heart disease", "Pericardial effusion", "Athletic heart"], "labs": {"wbc": 8.0, "crp": 5, "bnp": 120, "creatinine": 1.0, "glucose": 100, "hemoglobin": 13.5, "platelets": 220, "sodium": 140, "potassium": 4.2}, "vitals": {"bp": "145/92", "hr": 78, "rr": 16, "spo2": 97, "temp": 36.8}, "note": "62M mild DOE climbing stairs, no orthopnea. BP elevated, on lisinopril."},
    {"esi": 4, "complaint": "Cough and rhinorrhea", "finding": "Normal chest X-ray", "findings": ["normal_cxr", "clear_lung_fields"], "diff": ["Upper respiratory infection", "Viral bronchitis", "Allergic rhinitis", "Post-nasal drip"], "labs": {"wbc": 9.5, "crp": 12, "creatinine": 0.8, "glucose": 95, "hemoglobin": 14.0, "platelets": 250, "sodium": 140, "potassium": 4.0}, "vitals": {"bp": "118/74", "hr": 82, "rr": 16, "spo2": 98, "temp": 37.2}, "note": "20F college student, 4-day URI symptoms, clear lungs on exam, otherwise healthy."},
    {"esi": 4, "complaint": "Pre-operative chest X-ray", "finding": "Mild plate-like atelectasis at bases", "findings": ["plate_like_atelectasis", "basilar_opacities"], "diff": ["Basilar atelectasis", "Early pneumonia", "Pleural effusion", "Normal variant"], "labs": {"wbc": 8.0, "crp": 8, "creatinine": 0.9, "glucose": 100, "hemoglobin": 13.0, "platelets": 240, "sodium": 140, "potassium": 4.1}, "vitals": {"bp": "132/84", "hr": 76, "rr": 14, "spo2": 97, "temp": 36.7}, "note": "48F pre-op for cholecystectomy, asymptomatic, routine pre-op CXR."},
    {"esi": 4, "complaint": "Follow-up for pneumonia", "finding": "Near-complete resolution of prior right lower lobe opacity", "findings": ["resolving_infiltrate", "decreased_opacity"], "diff": ["Resolving pneumonia", "Post-infectious scarring", "Atelectasis", "Recurrent pneumonia"], "labs": {"wbc": 8.5, "crp": 15, "creatinine": 0.8, "glucose": 95, "hemoglobin": 13.8, "platelets": 250, "sodium": 140, "potassium": 4.0}, "vitals": {"bp": "122/78", "hr": 78, "rr": 16, "spo2": 98, "temp": 36.9}, "note": "40F treated for RLL pneumonia 3 weeks ago. Symptoms resolved. Follow-up CXR."},
    {"esi": 4, "complaint": "Chest discomfort, anxiety", "finding": "Normal chest X-ray", "findings": ["normal_cxr", "clear_lung_fields"], "diff": ["Anxiety/panic attack", "Musculoskeletal chest pain", "GERD", "Costochondritis"], "labs": {"wbc": 7.5, "crp": 5, "creatinine": 0.8, "glucose": 90, "hemoglobin": 14.0, "platelets": 240, "sodium": 140, "potassium": 4.0}, "vitals": {"bp": "128/82", "hr": 95, "rr": 18, "spo2": 98, "temp": 36.8}, "note": "28F episodic chest tightness, panic attacks, normal exam, no cardiac risk factors."},
    {"esi": 4, "complaint": "Mild wheeze", "finding": "Mild hyperinflation without acute infiltrate", "findings": ["mild_hyperinflation", "clear_lung_fields"], "diff": ["Asthma (well-controlled)", "COPD (stable)", "Bronchitis", "Normal variant"], "labs": {"wbc": 8.0, "crp": 10, "creatinine": 0.9, "glucose": 100, "hemoglobin": 14.5, "platelets": 230, "sodium": 140, "potassium": 4.2}, "vitals": {"bp": "130/84", "hr": 82, "rr": 16, "spo2": 97, "temp": 36.9}, "note": "55M known asthmatic, mild wheeze after pollen exposure. Otherwise well, good inhaler technique."},
    {"esi": 4, "complaint": "Incidental finding on X-ray", "finding": "Calcified granuloma right upper lobe", "findings": ["calcified_granuloma", "benign_appearing"], "diff": ["Healed granuloma", "Histoplasmosis scar", "TB scar", "Benign calcified nodule"], "labs": {"wbc": 7.0, "crp": 3, "creatinine": 0.8, "glucose": 90, "hemoglobin": 14.0, "platelets": 240, "sodium": 140, "potassium": 4.0}, "vitals": {"bp": "120/78", "hr": 70, "rr": 14, "spo2": 98, "temp": 36.6}, "note": "45F CXR for immigration paperwork. Asymptomatic. Prior BCG vaccination."},
    {"esi": 4, "complaint": "Mild chest congestion", "finding": "Subtle peribronchial thickening", "findings": ["peribronchial_thickening", "subtle_changes"], "diff": ["Viral bronchitis", "Early asthma exacerbation", "Allergic bronchitis", "Post-infectious changes"], "labs": {"wbc": 9.0, "crp": 18, "creatinine": 0.8, "glucose": 95, "hemoglobin": 13.8, "platelets": 250, "sodium": 140, "potassium": 4.0}, "vitals": {"bp": "118/76", "hr": 80, "rr": 16, "spo2": 98, "temp": 37.3}, "note": "35M 5-day cough with clear sputum, mild congestion. No fever, no dyspnea."},
    # ESI 5 (non-urgent)
    {"esi": 5, "complaint": "Routine health screening", "finding": "Normal chest X-ray", "findings": ["normal_cxr", "clear_lung_fields"], "diff": ["Normal study", "No acute cardiopulmonary process"], "labs": {"wbc": 7.0, "crp": 2, "creatinine": 0.8, "glucose": 88, "hemoglobin": 14.2, "platelets": 240, "sodium": 140, "potassium": 4.0}, "vitals": {"bp": "118/76", "hr": 68, "rr": 14, "spo2": 99, "temp": 36.6}, "note": "30F annual health screening, asymptomatic, no complaints. Non-smoker."},
    {"esi": 5, "complaint": "Pre-employment chest X-ray", "finding": "Normal chest X-ray", "findings": ["normal_cxr", "clear_lung_fields"], "diff": ["Normal study", "No acute cardiopulmonary process"], "labs": {"wbc": 6.5, "crp": 1, "creatinine": 0.9, "glucose": 90, "hemoglobin": 14.5, "platelets": 230, "sodium": 140, "potassium": 4.1}, "vitals": {"bp": "122/78", "hr": 72, "rr": 14, "spo2": 99, "temp": 36.5}, "note": "25M pre-employment physical for construction job. Healthy, no symptoms."},
    {"esi": 5, "complaint": "Follow-up for old TB scar", "finding": "Stable calcified granulomas bilaterally", "findings": ["calcified_granuloma", "stable_appearance"], "diff": ["Healed TB", "Old histoplasmosis", "Benign calcified nodules"], "labs": {"wbc": 7.0, "crp": 2, "creatinine": 0.8, "glucose": 90, "hemoglobin": 13.8, "platelets": 240, "sodium": 140, "potassium": 4.0}, "vitals": {"bp": "120/78", "hr": 70, "rr": 14, "spo2": 99, "temp": 36.6}, "note": "50F annual follow-up of known old TB scars. Asymptomatic, stable for 10 years."},
    {"esi": 5, "complaint": "Routine asthma monitoring", "finding": "Normal chest X-ray", "findings": ["normal_cxr", "clear_lung_fields"], "diff": ["Normal study", "Well-controlled asthma"], "labs": {"wbc": 7.5, "crp": 3, "creatinine": 0.8, "glucose": 92, "hemoglobin": 14.0, "platelets": 240, "sodium": 140, "potassium": 4.0}, "vitals": {"bp": "118/76", "hr": 72, "rr": 14, "spo2": 99, "temp": 36.7}, "note": "22F well-controlled asthmatic on low-dose ICS. No exacerbations in 2 years."},
    {"esi": 5, "complaint": "Insurance requirement", "finding": "Mild scoliosis, lungs clear", "findings": ["mild_scoliosis", "clear_lung_fields"], "diff": ["Mild idiopathic scoliosis", "Normal lungs"], "labs": {"wbc": 7.0, "crp": 1, "creatinine": 0.8, "glucose": 90, "hemoglobin": 13.5, "platelets": 240, "sodium": 140, "potassium": 4.0}, "vitals": {"bp": "115/72", "hr": 68, "rr": 14, "spo2": 99, "temp": 36.5}, "note": "18F insurance medical exam. Incidental mild scoliosis. Asymptomatic."},
    {"esi": 5, "complaint": "Travel clearance", "finding": "Normal chest X-ray", "findings": ["normal_cxr", "clear_lung_fields"], "diff": ["Normal study", "No acute cardiopulmonary process"], "labs": {"wbc": 6.8, "crp": 2, "creatinine": 0.8, "glucose": 90, "hemoglobin": 14.0, "platelets": 230, "sodium": 140, "potassium": 4.0}, "vitals": {"bp": "120/78", "hr": 70, "rr": 14, "spo2": 99, "temp": 36.6}, "note": "35F travel clearance for work assignment abroad. Healthy, asymptomatic."},
    {"esi": 5, "complaint": "Routine post-op check", "finding": "Normal chest X-ray", "findings": ["normal_cxr", "clear_lung_fields"], "diff": ["Normal study", "No acute cardiopulmonary process"], "labs": {"wbc": 8.0, "crp": 15, "creatinine": 0.9, "glucose": 100, "hemoglobin": 12.5, "platelets": 250, "sodium": 140, "potassium": 4.1}, "vitals": {"bp": "128/82", "hr": 78, "rr": 16, "spo2": 98, "temp": 37.0}, "note": "55F post-op day 7 laparoscopic cholecystectomy, routine CXR. Mild pain, otherwise well."},
    {"esi": 5, "complaint": "Wellness check", "finding": "Small hiatal hernia, lungs clear", "findings": ["hiatal_hernia", "clear_lung_fields"], "diff": ["Small hiatal hernia", "Normal lungs", "GERD"], "labs": {"wbc": 7.0, "crp": 2, "creatinine": 0.8, "glucose": 90, "hemoglobin": 13.8, "platelets": 240, "sodium": 140, "potassium": 4.0}, "vitals": {"bp": "118/76", "hr": 70, "rr": 14, "spo2": 99, "temp": 36.6}, "note": "42F wellness visit, occasional heartburn. Otherwise asymptomatic."},
    {"esi": 5, "complaint": "School physical", "finding": "Normal chest X-ray", "findings": ["normal_cxr", "clear_lung_fields"], "diff": ["Normal study", "No acute cardiopulmonary process"], "labs": {"wbc": 7.0, "crp": 1, "creatinine": 0.7, "glucose": 85, "hemoglobin": 13.5, "platelets": 250, "sodium": 140, "potassium": 4.0}, "vitals": {"bp": "110/70", "hr": 72, "rr": 16, "spo2": 99, "temp": 36.8}, "note": "16M school sports physical. Healthy, active, no complaints."},
]

# Pad to 50 with more varied cases if needed
while len(CASE_TEMPLATES) < 50:
    # Add some more variations
    extra = [
        {"esi": 3, "complaint": "Persistent cough", "finding": "Left upper lobe infiltrate with volume loss", "findings": ["consolidation", "volume_loss", "hilar_prominence"], "diff": ["Lung cancer with post-obstructive pneumonia", "Tuberculosis", "Fungal infection", "Chronic pneumonia"], "labs": {"wbc": 11.0, "crp": 55, "creatinine": 0.9, "glucose": 100, "hemoglobin": 12.0, "platelets": 300, "sodium": 138, "potassium": 4.0}, "vitals": {"bp": "130/82", "hr": 92, "rr": 18, "spo2": 94, "temp": 37.4}, "note": "48M 2-month persistent cough, 8kg weight loss, smoker 30 pack-years."},
        {"esi": 2, "complaint": "Acute respiratory distress", "finding": "Bilateral patchy infiltrates with air bronchograms", "findings": ["bilateral_infiltrates", "air_bronchogram", "ground_glass_opacities"], "diff": ["Severe pneumonia", "ARDS", "Pulmonary hemorrhage", "Diffuse alveolar damage"], "labs": {"wbc": 18.0, "crp": 200, "lactate": 3.5, "creatinine": 1.5, "glucose": 140, "hemoglobin": 11.0, "platelets": 180, "sodium": 135, "potassium": 4.5}, "vitals": {"bp": "105/68", "hr": 125, "rr": 34, "spo2": 82, "temp": 39.2}, "note": "52M influenza-like illness 5 days, sudden worsening dyspnea, hypoxemia."},
        {"esi": 4, "complaint": "Chest pain after exercise", "finding": "Small left pneumothorax (~10%)", "findings": ["small_pneumothorax", "apical_bullae"], "diff": ["Spontaneous pneumothorax", "Exercise-induced pneumothorax", "Apical bleb rupture"], "labs": {"wbc": 8.0, "crp": 5, "creatinine": 0.8, "glucose": 95, "hemoglobin": 14.2, "platelets": 250, "sodium": 140, "potassium": 4.0}, "vitals": {"bp": "125/80", "hr": 85, "rr": 16, "spo2": 97, "temp": 36.8}, "note": "21M sudden L chest pain while running. Minimal dyspnea, stable vitals."},
        {"esi": 3, "complaint": "Worsening dyspnea", "finding": "Bilateral hilar lymphadenopathy with interstitial pattern", "findings": ["hilar_lymphadenopathy", "interstitial_pattern", "reticulonodular"], "diff": ["Sarcoidosis", "Lymphoma", "Tuberculosis", "Pneumoconiosis"], "labs": {"wbc": 8.5, "crp": 25, "creatinine": 1.0, "glucose": 100, "hemoglobin": 13.5, "platelets": 220, "sodium": 140, "potassium": 4.2}, "vitals": {"bp": "132/84", "hr": 88, "rr": 20, "spo2": 93, "temp": 36.9}, "note": "35F progressive dyspnea 6 months, dry cough, erythema nodosum on shins."},
        {"esi": 1, "complaint": "Near-drowning", "finding": "Bilateral diffuse alveolar infiltrates", "findings": ["bilateral_alveolar_infiltrates", "patchy_consolidation", "cephalization"], "diff": ["Aspiration pneumonitis", "ARDS", "Pulmonary edema", "Bacterial pneumonia"], "labs": {"wbc": 14.0, "crp": 80, "creatinine": 1.8, "glucose": 120, "hemoglobin": 13.0, "platelets": 250, "sodium": 128, "potassium": 5.0}, "vitals": {"bp": "95/60", "hr": 135, "rr": 36, "spo2": 75, "temp": 35.8}, "note": "8YO F pulled from swimming pool, unconscious 2 minutes, now alert but severe respiratory distress."},
    ]
    CASE_TEMPLATES.extend(extra)

CASE_TEMPLATES = CASE_TEMPLATES[:50]

# Demographic variations
AGES = [4, 8, 16, 19, 21, 22, 24, 25, 28, 29, 30, 32, 33, 35, 38, 40, 42, 45, 48, 50, 52, 55, 55, 58, 60, 62, 65, 67, 68, 71, 74, 76, 78, 80, 82, 84, 86, 88, 90, 92]
SEXES = ["male", "female"]
RACES = ["White", "Black", "Asian", "Hispanic", "Native American"]

LAB_UNITS = {
    "wbc": "K/\u03bcL", "hemoglobin": "g/dL", "platelets": "K/\u03bcL",
    "creatinine": "mg/dL", "glucose": "mg/dL", "sodium": "mEq/L",
    "potassium": "mEq/L", "crp": "mg/L", "bnp": "pg/mL",
    "troponin_i": "ng/L", "lactate": "mmol/L", "d_dimer": "ng/mL",
}

# Standard lab keys to include in every case
ALL_LAB_KEYS = ["wbc", "hemoglobin", "platelets", "creatinine", "glucose", "sodium", "potassium", "crp"]

# Safety flag templates per ESI
SAFETY_FLAGS = {
    1: [
        {"rule": "LIFE_THREATENING", "keywords": ["life-threatening", "critical", "emergent"]},
        {"rule": "DESATURATION", "keywords": ["desaturation", "hypoxemia", "spo2"]},
        {"rule": "RESPIRATORY_DISTRESS", "keywords": ["respiratory", "distress", "breathing"]},
        {"rule": "HEMORRHAGIC_SHOCK", "keywords": ["hemorrhage", "shock", "bleeding"]},
        {"rule": "SEPSIS_ALERT", "keywords": ["sepsis", "septic", "shock"]},
        {"rule": "ACS_ALERT", "keywords": ["acs", "coronary", "cardiac"]},
        {"rule": "HYPERTENSION", "keywords": ["hypertension", "bp"]},
    ],
    2: [
        {"rule": "ACS_ALERT", "keywords": ["acs", "coronary", "cardiac"]},
        {"rule": "HEMORRHAGIC_SHOCK", "keywords": ["hemorrhage", "shock", "bleeding"]},
        {"rule": "TRAUMA_PROTOCOL", "keywords": ["trauma", "injury"]},
        {"rule": "OVERDOSE_PROTOCOL", "keywords": ["overdose", "poisoning", "toxicity"]},
        {"rule": "VISION_THREAT", "keywords": ["vision", "eye", "sight"]},
        {"rule": "CHEMICAL_EXPOSURE", "keywords": ["chemical", "exposure", "burn"]},
    ],
    3: [
        {"rule": "RESPIRATORY_DISTRESS", "keywords": ["respiratory", "distress", "breathing"]},
        {"rule": "PEDIATRIC_MONITOR", "keywords": ["pediatric", "child", "peds"]},
        {"rule": "CHEMICAL_EXPOSURE", "keywords": ["chemical", "exposure", "burn"]},
    ],
    4: [
        {"rule": "PEDIATRIC_MONITOR", "keywords": ["pediatric", "child", "peds"]},
    ],
    5: [],
}

# Lab alert templates
LAB_ALERT_TEMPLATES = {
    "wbc_high": {"code": "WBC_ELEVATED", "lab": "WBC", "keywords": ["wbc", "white blood cell", "leukocytosis"]},
    "wbc_low": {"code": "WBC_LOW", "lab": "WBC", "keywords": ["wbc", "white blood cell", "leukopenia"]},
    "crp_high": {"code": "CRP_ELEVATED", "lab": "CRP", "keywords": ["crp", "c-reactive protein", "inflammation"]},
    "spo2_low": {"code": "SPO2_LOW", "lab": "SpO2", "keywords": ["spo2", "oxygen", "hypoxemia"]},
    "hr_high": {"code": "HR_ELEVATED", "lab": "Heart Rate", "keywords": ["hr", "heart rate", "tachycardia"]},
    "hr_low": {"code": "HR_LOW", "lab": "Heart Rate", "keywords": ["hr", "heart rate", "bradycardia"]},
    "rr_high": {"code": "RR_ELEVATED", "lab": "Respiratory Rate", "keywords": ["rr", "respiratory rate", "tachypnea"]},
    "bp_low": {"code": "BP_LOW", "lab": "Blood Pressure", "keywords": ["bp", "blood pressure", "hypotension"]},
    "bp_high": {"code": "BP_ELEVATED", "lab": "Blood Pressure", "keywords": ["bp", "blood pressure", "hypertension"]},
    "temp_high": {"code": "FEVER", "lab": "Temperature", "keywords": ["temperature", "fever", "hyperthermia"]},
    "temp_low": {"code": "HYPOTHERMIA", "lab": "Temperature", "keywords": ["temperature", "hypothermia"]},
    "lactate_high": {"code": "LACTATE_ELEVATED", "lab": "Lactate", "keywords": ["lactate", "lactic acidosis"]},
    "troponin_high": {"code": "ELEVATED_TROPONIN", "lab": "Troponin", "keywords": ["troponin", "elevated"]},
    "bnp_high": {"code": "BNP_ELEVATED", "lab": "BNP", "keywords": ["bnp", "heart failure"]},
    "ddimer_high": {"code": "D_DIMER_ELEVATED", "lab": "D-Dimer", "keywords": ["d-dimer", "embolism"]},
    "hemoglobin_low": {"code": "HEMOGLOBIN_LOW", "lab": "Hemoglobin", "keywords": ["hemoglobin", "anemia"]},
    "platelets_low": {"code": "PLATELETS_LOW", "lab": "Platelets", "keywords": ["platelets", "thrombocytopenia"]},
    "creatinine_high": {"code": "CREATININE_ELEVATED", "lab": "Creatinine", "keywords": ["creatinine", "renal"]},
    "glucose_high": {"code": "GLUCOSE_ELEVATED", "lab": "Glucose", "keywords": ["glucose", "hyperglycemia"]},
    "glucose_low": {"code": "GLUCOSE_LOW", "lab": "Glucose", "keywords": ["glucose", "hypoglycemia"]},
    "sodium_low": {"code": "SODIUM_LOW", "lab": "Sodium", "keywords": ["sodium", "hyponatremia"]},
    "sodium_high": {"code": "SODIUM_HIGH", "lab": "Sodium", "keywords": ["sodium", "hypernatremia"]},
    "potassium_low": {"code": "POTASSIUM_LOW", "lab": "Potassium", "keywords": ["potassium", "hypokalemia"]},
    "potassium_high": {"code": "POTASSIUM_HIGH", "lab": "Potassium", "keywords": ["potassium", "hyperkalemia"]},
}


def make_lab_alerts(template, vitals, labs):
    alerts = []
    # Check vitals
    hr = vitals.get("hr", 80)
    rr = vitals.get("rr", 16)
    spo2 = vitals.get("spo2", 98)
    temp = vitals.get("temp", 37.0)
    bp = vitals.get("bp", "120/80")
    try:
        sbp = int(bp.split("/")[0])
    except:
        sbp = 120

    if hr > 100:
        alerts.append(LAB_ALERT_TEMPLATES["hr_high"])
    if hr < 60:
        alerts.append(LAB_ALERT_TEMPLATES["hr_low"])
    if rr > 20:
        alerts.append(LAB_ALERT_TEMPLATES["rr_high"])
    if spo2 < 94:
        alerts.append(LAB_ALERT_TEMPLATES["spo2_low"])
    if temp >= 38.0:
        alerts.append(LAB_ALERT_TEMPLATES["temp_high"])
    if temp < 36.0:
        alerts.append(LAB_ALERT_TEMPLATES["temp_low"])
    if sbp < 90:
        alerts.append(LAB_ALERT_TEMPLATES["bp_low"])
    if sbp > 180:
        alerts.append(LAB_ALERT_TEMPLATES["bp_high"])

    # Check labs
    if labs.get("wbc", 8) > 12:
        alerts.append(LAB_ALERT_TEMPLATES["wbc_high"])
    if labs.get("wbc", 8) < 4:
        alerts.append(LAB_ALERT_TEMPLATES["wbc_low"])
    if labs.get("crp", 5) > 50:
        alerts.append(LAB_ALERT_TEMPLATES["crp_high"])
    if labs.get("lactate", 1) > 2.5:
        alerts.append(LAB_ALERT_TEMPLATES["lactate_high"])
    if labs.get("troponin_i", 0) > 0.04:
        alerts.append(LAB_ALERT_TEMPLATES["troponin_high"])
    if labs.get("bnp", 50) > 400:
        alerts.append(LAB_ALERT_TEMPLATES["bnp_high"])
    if labs.get("d_dimer", 200) > 1000:
        alerts.append(LAB_ALERT_TEMPLATES["ddimer_high"])
    if labs.get("hemoglobin", 14) < 11:
        alerts.append(LAB_ALERT_TEMPLATES["hemoglobin_low"])
    if labs.get("platelets", 250) < 100:
        alerts.append(LAB_ALERT_TEMPLATES["platelets_low"])
    if labs.get("creatinine", 1.0) > 1.5:
        alerts.append(LAB_ALERT_TEMPLATES["creatinine_high"])
    if labs.get("glucose", 100) > 160:
        alerts.append(LAB_ALERT_TEMPLATES["glucose_high"])
    if labs.get("glucose", 100) < 60:
        alerts.append(LAB_ALERT_TEMPLATES["glucose_low"])
    if labs.get("sodium", 140) < 133:
        alerts.append(LAB_ALERT_TEMPLATES["sodium_low"])
    if labs.get("sodium", 140) > 150:
        alerts.append(LAB_ALERT_TEMPLATES["sodium_high"])
    if labs.get("potassium", 4.0) < 3.5:
        alerts.append(LAB_ALERT_TEMPLATES["potassium_low"])
    if labs.get("potassium", 4.0) > 5.5:
        alerts.append(LAB_ALERT_TEMPLATES["potassium_high"])

    return alerts


def make_safety_flags(esi, findings, labs, vitals):
    flags = []
    available = SAFETY_FLAGS.get(esi, [])

    # Pick relevant flags based on case content
    finding_keywords = " ".join(f.lower() for f in findings)
    for flag in available:
        flag_kw = " ".join(flag["keywords"]).lower()
        # Include flag if keywords match findings or labs or if it's a high-severity case
        if any(kw in finding_keywords for kw in flag["keywords"]):
            flags.append(flag)
        elif esi <= 2 and len(flags) < 2:
            flags.append(flag)

    if not flags and esi <= 3:
        # Default flags for urgent cases
        flags = [{"rule": "RESPIRATORY_DISTRESS", "keywords": ["respiratory", "distress"]}]

    return flags[:3]


def generate_demo_case(idx, template):
    case_id = f"CS-2024-{idx:03d}"
    img_idx = ((idx - 1) % 6) + 1
    image_path = f"backend/data/images/CS-2024-{img_idx:03d}.png"

    age = template.get("patient_age") or random.choice(AGES)
    sex = template.get("patient_sex") or random.choice(SEXES)
    race = template.get("patient_race") or random.choice(RACES)

    labs = template["labs"].copy()
    vitals = template["vitals"].copy()

    # Ensure all standard labs are present
    for key in ALL_LAB_KEYS:
        if key not in labs:
            labs[key] = round(random.uniform(4.0, 15.0) if key == "wbc" else
                             random.uniform(11.0, 16.0) if key == "hemoglobin" else
                             random.uniform(150, 400) if key == "platelets" else
                             random.uniform(0.6, 1.3) if key == "creatinine" else
                             random.uniform(70, 140) if key == "glucose" else
                             random.uniform(135, 145) if key == "sodium" else
                             random.uniform(3.5, 5.0) if key == "potassium" else
                             random.uniform(2, 20), 1)

    lab_units = {k: LAB_UNITS.get(k, "") for k in labs}

    # Build case
    case = {
        "case_id": case_id,
        "image_path": image_path,
        "lab_values": labs,
        "lab_units": lab_units,
        "triage_note": template["note"],
        "patient_age": age,
        "patient_sex": sex,
        "patient_race": race,
        "chief_complaint": template["complaint"],
        "vitals": vitals,
    }
    return case


def generate_ground_truth(idx, template):
    case_id = f"CS-2024-{idx:03d}"
    labs = template["labs"]
    vitals = template["vitals"]

    # Build findings with keywords
    finding_names = {
        "cardiomegaly": {"name": "Cardiomegaly", "keywords": ["cardiomegaly", "cardiac", "heart", "enlarged"]},
        "pulmonary_edema": {"name": "Pulmonary Edema", "keywords": ["pulmonary edema", "edema", "interstitial", "effusion"]},
        "tension_pneumothorax": {"name": "Tension Pneumothorax", "keywords": ["tension pneumothorax", "pneumothorax", "collapsed lung"]},
        "mediastinal_shift": {"name": "Mediastinal Shift", "keywords": ["mediastinal shift", "shift", "deviation"]},
        "tracheal_deviation": {"name": "Tracheal Deviation", "keywords": ["tracheal deviation", "trachea", "airway"]},
        "cavitary_lesion": {"name": "Cavitary Lesion", "keywords": ["cavitary lesion", "cavity", "cavitating"]},
        "air_fluid_level": {"name": "Air-Fluid Level", "keywords": ["air-fluid level", "fluid level", "cavity"]},
        "consolidation": {"name": "Consolidation", "keywords": ["consolidation", "opacity", "infiltrate"]},
        "rib_fractures": {"name": "Rib Fractures", "keywords": ["rib fracture", "fracture", "rib"]},
        "hemothorax": {"name": "Hemothorax", "keywords": ["hemothorax", "blood", "pleural"]},
        "pulmonary_contusion": {"name": "Pulmonary Contusion", "keywords": ["pulmonary contusion", "contusion", "bruising"]},
        "bilateral_infiltrates": {"name": "Bilateral Infiltrates", "keywords": ["bilateral infiltrates", "infiltrates", "diffuse"]},
        "ards_pattern": {"name": "ARDS Pattern", "keywords": ["ards", "acute respiratory distress", "diffuse infiltrates"]},
        "widened_mediastinum": {"name": "Widened Mediastinum", "keywords": ["widened mediastinum", "mediastinum", "aortic"]},
        "pleural_effusion": {"name": "Pleural Effusion", "keywords": ["pleural effusion", "effusion", "fluid"]},
        "left_apical_capping": {"name": "Left Apical Capping", "keywords": ["apical capping", "apex", "blood"]},
        "pneumothorax": {"name": "Pneumothorax", "keywords": ["pneumothorax", "collapsed lung", "air"]},
        "visceral_pleural_line": {"name": "Visceral Pleural Line", "keywords": ["visceral pleural line", "pleural line", "lung edge"]},
        "lung_collapse": {"name": "Lung Collapse", "keywords": ["lung collapse", "atelectasis", "collapsed"]},
        "hyperinflation": {"name": "Hyperinflation", "keywords": ["hyperinflation", "hyperexpanded", "copd"]},
        "flattened_diaphragms": {"name": "Flattened Diaphragms", "keywords": ["flattened diaphragm", "diaphragm", "copd"]},
        "increased_retrosternal_space": {"name": "Increased Retrosternal Space", "keywords": ["retrosternal space", "emphysema"]},
        "bullae": {"name": "Bullae", "keywords": ["bulla", "bullae", "emphysema"]},
        "atelectasis": {"name": "Atelectasis", "keywords": ["atelectasis", "collapse", "volume loss"]},
        "volume_loss": {"name": "Volume Loss", "keywords": ["volume loss", "collapse", "small lung"]},
        "elevated_hemidiaphragm": {"name": "Elevated Hemidiaphragm", "keywords": ["elevated hemidiaphragm", "diaphragm"]},
        "hilar_mass": {"name": "Hilar Mass", "keywords": ["hilar mass", "hilum", "mass"]},
        "post_obstructive_pneumonia": {"name": "Post-Obstructive Pneumonia", "keywords": ["post-obstructive pneumonia", "obstruction"]},
        "westermark_sign": {"name": "Westermark Sign", "keywords": ["westermark sign", "oligemia", "embolism"]},
        "hampton_hump": {"name": "Hampton Hump", "keywords": ["hampton hump", "wedge-shaped", "infarct"]},
        "subcutaneous_emphysema": {"name": "Subcutaneous Emphysema", "keywords": ["subcutaneous emphysema", "air", "crepitus"]},
        "interstitial_infiltrates": {"name": "Interstitial Infiltrates", "keywords": ["interstitial infiltrates", "interstitial", "fibrosis"]},
        "honeycombing": {"name": "Honeycombing", "keywords": ["honeycombing", "fibrosis", "UIP"]},
        "reticular_pattern": {"name": "Reticular Pattern", "keywords": ["reticular pattern", "reticulation", "fibrosis"]},
        "pneumomediastinum": {"name": "Pneumomediastinum", "keywords": ["pneumomediastinum", "mediastinal air", "air"]},
        "continuous_diaphragm_sign": {"name": "Continuous Diaphragm Sign", "keywords": ["continuous diaphragm sign", "mediastinum"]},
        "air_bronchogram": {"name": "Air Bronchogram", "keywords": ["air bronchogram", "bronchogram", "consolidation"]},
        "silhouette_sign": {"name": "Silhouette Sign", "keywords": ["silhouette sign", "border", "opacity"]},
        "cephalization": {"name": "Cephalization of Vessels", "keywords": ["cephalization", "vascular redistribution", "chf"]},
        "fungus_ball": {"name": "Fungus Ball", "keywords": ["fungus ball", "aspergilloma", "mycetoma"]},
        "air_crescent_sign": {"name": "Air Crescent Sign", "keywords": ["air crescent sign", "crescent", "aspergilloma"]},
        "peribronchial_cuffing": {"name": "Peribronchial Cuffing", "keywords": ["peribronchial cuffing", "cuffing", "bronchial"]},
        "diffuse_infiltrates": {"name": "Diffuse Infiltrates", "keywords": ["diffuse infiltrates", "diffuse", "widespread"]},
        "meniscus_sign": {"name": "Meniscus Sign", "keywords": ["meniscus sign", "meniscus", "pleural"]},
        "blunting_costophrenic_angle": {"name": "Blunted Costophrenic Angle", "keywords": ["blunted costophrenic angle", "angle", "effusion"]},
        "patchy_infiltrate": {"name": "Patchy Infiltrate", "keywords": ["patchy infiltrate", "patchy", "subtle"]},
        "subtle_consolidation": {"name": "Subtle Consolidation", "keywords": ["subtle consolidation", "subtle", "faint"]},
        "pulmonary_nodule": {"name": "Pulmonary Nodule", "keywords": ["pulmonary nodule", "nodule", "mass"]},
        "well_circumscribed": {"name": "Well-Circumscribed Lesion", "keywords": ["well circumscribed", "nodule", "round"]},
        "normal_vascularity": {"name": "Normal Vascularity", "keywords": ["normal vascularity", "vessels"]},
        "clear_lung_fields": {"name": "Clear Lung Fields", "keywords": ["clear lung fields", "clear", "normal"]},
        "normal_cxr": {"name": "Normal Chest X-Ray", "keywords": ["normal chest x-ray", "normal", "clear"]},
        "cortical_disruption": {"name": "Cortical Disruption", "keywords": ["cortical disruption", "fracture line", "rib"]},
        "rib_fracture": {"name": "Rib Fracture", "keywords": ["rib fracture", "fracture", "rib"]},
        "resolving_infiltrate": {"name": "Resolving Infiltrate", "keywords": ["resolving infiltrate", "resolving", "clearing"]},
        "decreased_opacity": {"name": "Decreased Opacity", "keywords": ["decreased opacity", "fading", "clearing"]},
        "mild_hyperinflation": {"name": "Mild Hyperinflation", "keywords": ["mild hyperinflation", "hyperinflation"]},
        "calcified_granuloma": {"name": "Calcified Granuloma", "keywords": ["calcified granuloma", "granuloma", "calcified"]},
        "stable_appearance": {"name": "Stable Appearance", "keywords": ["stable", "unchanged", "chronic"]},
        "benign_appearing": {"name": "Benign-Appearing Lesion", "keywords": ["benign", "calcified", "stable"]},
        "peribronchial_thickening": {"name": "Peribronchial Thickening", "keywords": ["peribronchial thickening", "thickening"]},
        "subtle_changes": {"name": "Subtle Changes", "keywords": ["subtle changes", "subtle", "minimal"]},
        "hilar_lymphadenopathy": {"name": "Hilar Lymphadenopathy", "keywords": ["hilar lymphadenopathy", "lymph nodes", "hilar"]},
        "reticulonodular": {"name": "Reticulonodular Pattern", "keywords": ["reticulonodular", "nodules", "interstitial"]},
        "bilateral_alveolar_infiltrates": {"name": "Bilateral Alveolar Infiltrates", "keywords": ["bilateral alveolar infiltrates", "alveolar"]},
        "ground_glass_opacities": {"name": "Ground-Glass Opacities", "keywords": ["ground-glass", "ground glass", "GGO"]},
        "small_pneumothorax": {"name": "Small Pneumothorax", "keywords": ["small pneumothorax", "minimal pneumothorax"]},
        "apical_bullae": {"name": "Apical Bullae", "keywords": ["apical bullae", "bullae", "bleb"]},
        "plate_like_atelectasis": {"name": "Plate-Like Atelectasis", "keywords": ["plate-like atelectasis", "platelike", "linear"]},
        "basilar_opacities": {"name": "Basilar Opacities", "keywords": ["basilar opacities", "bases", "opacity"]},
        "hiatal_hernia": {"name": "Hiatal Hernia", "keywords": ["hiatal hernia", "hernia", "stomach"]},
        "mild_scoliosis": {"name": "Mild Scoliosis", "keywords": ["mild scoliosis", "scoliosis", "spine"]},
        "upper_lobe_predilection": {"name": "Upper Lobe Predilection", "keywords": ["upper lobe", "apex", "apical"]},
        "fibrotic_changes": {"name": "Fibrotic Changes", "keywords": ["fibrotic changes", "fibrosis", "scarring"]},
    }

    expected_findings = []
    for fid in template["findings"]:
        info = finding_names.get(fid, {"name": fid.replace("_", " ").title(), "keywords": [fid.replace("_", " ")]})
        expected_findings.append({"id": fid, "name": info["name"], "keywords": info["keywords"]})

    lab_alerts = make_lab_alerts(template, vitals, labs)
    safety_flags = make_safety_flags(template["esi"], template["findings"], labs, vitals)

    return {
        "case_id": case_id,
        "esi_level": template["esi"],
        "expected_findings": expected_findings,
        "expected_lab_alerts": lab_alerts,
        "expected_safety_flags": safety_flags,
        "expected_differential": template["diff"],
    }


def main():
    demo_cases = []
    ground_truth = {}

    for i, template in enumerate(CASE_TEMPLATES, 1):
        demo_cases.append(generate_demo_case(i, template))
        ground_truth[f"CS-2024-{i:03d}"] = generate_ground_truth(i, template)

    # Write demo_cases.json
    with open("backend/data/demo_cases.json", "w", encoding="utf-8") as f:
        json.dump(demo_cases, f, indent=2, ensure_ascii=False)

    # Write ground_truth.py
    lines = [
        "# =========================================================================",
        "# GROUND TRUTH - 50 Chest X-Ray Emergency Cases",
        "# =========================================================================",
        "",
        "GROUND_TRUTH = {",
    ]

    for case_id in sorted(ground_truth.keys()):
        gt = ground_truth[case_id]
        lines.append(f'    "{case_id}": {{')
        lines.append(f'        "case_id": "{case_id}",')
        lines.append(f'        "esi_level": {gt["esi_level"]},')

        # findings
        findings_str = ", ".join(
            f'{{"id": "{f["id"]}", "name": "{f["name"]}", "keywords": {f["keywords"]}}}'
            for f in gt["expected_findings"]
        )
        lines.append(f'        "expected_findings": [{findings_str}],')

        # lab alerts
        alerts_str = ", ".join(
            f'{{"code": "{a["code"]}", "lab": "{a["lab"]}", "keywords": {a["keywords"]}}}'
            for a in gt["expected_lab_alerts"]
        )
        lines.append(f'        "expected_lab_alerts": [{alerts_str}],')

        # safety flags
        flags_str = ", ".join(
            f'{{"rule": "{flag["rule"]}", "keywords": {flag["keywords"]}}}'
            for flag in gt["expected_safety_flags"]
        )
        lines.append(f'        "expected_safety_flags": [{flags_str}],')

        # differential
        diff_str = ", ".join(f'"{d}"' for d in gt["expected_differential"])
        lines.append(f'        "expected_differential": [{diff_str}],')

        lines.append("    },")

    lines.append("}")

    with open("backend/data/ground_truth.py", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Generated {len(demo_cases)} demo cases and ground truth entries.")
    print("Files written: backend/data/demo_cases.json, backend/data/ground_truth.py")


if __name__ == "__main__":
    main()
