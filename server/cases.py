from typing import List, Dict, Any

EASY_CASES = [
    {
        "raw_narrative": "Patient took Aspirin and developed hives standardly after 2 hours.",
        "gt_is_valid_case": True,
        "gt_suspect_drug": "Aspirin",
        "gt_event_term": "hives"
    },
    {
        "raw_narrative": "A guy told me he took Tylenol but nothing happened.",
        "gt_is_valid_case": False,
        "gt_suspect_drug": "Tylenol",
        "gt_event_term": "none"
    },
    {
        "raw_narrative": "After starting Lisinopril, the 45-year-old male developed a severe dry cough.",
        "gt_is_valid_case": True,
        "gt_suspect_drug": "Lisinopril",
        "gt_event_term": "dry cough"
    },
    {
        "raw_narrative": "I heard on the news that Ibuprofen is bad for your stomach.",
        "gt_is_valid_case": False,
        "gt_suspect_drug": "Ibuprofen",
        "gt_event_term": "none"
    },
    {
        "raw_narrative": "My mother applied the prescribed hydrocortisone cream and her skin turned very red and itchy.",
        "gt_is_valid_case": True,
        "gt_suspect_drug": "hydrocortisone",
        "gt_event_term": "itchy skin"
    },
    {
        "raw_narrative": "Subject was prescribed Warfarin. Three days later, they reported bruising on their arms.",
        "gt_is_valid_case": True,
        "gt_suspect_drug": "Warfarin",
        "gt_event_term": "bruising"
    },
    {
        "raw_narrative": "Patient feels tired today. They have been taking a multivitamin for 5 years.",
        "gt_is_valid_case": False,
        "gt_suspect_drug": "multivitamin",
        "gt_event_term": "none"
    },
    {
        "raw_narrative": "While on Prozac, the patient experienced a sudden onset of suicidal ideation.",
        "gt_is_valid_case": True,
        "gt_suspect_drug": "Prozac",
        "gt_event_term": "suicidal ideation"
    },
    {
        "raw_narrative": "I read online that vaccines cause autism.",
        "gt_is_valid_case": False,
        "gt_suspect_drug": "vaccines",
        "gt_event_term": "none"
    },
    {
        "raw_narrative": "The patient developed a severe rash after their first injection of Humira.",
        "gt_is_valid_case": True,
        "gt_suspect_drug": "Humira",
        "gt_event_term": "rash"
    }
]

MEDIUM_CASES = [
    {
        "raw_narrative": "A 50-year-old female patient developed acute myocardial infarction (heart attack) two days after starting Vioxx. She was hospitalized immediately. She has a history of high blood pressure.",
        "available_meddra_terms": {
            "Cardiac disorders": ["Myocardial infarction", "Angina pectoris", "Palpitations"],
            "Vascular disorders": ["Hypertension", "Hypotension"]
        },
        "gt_meddra_soc": "Cardiac disorders",
        "gt_meddra_pt": "Myocardial infarction",
        "gt_is_serious": True
    },
    {
        "raw_narrative": "Patient complains of a mild headache after taking 200mg of caffeine. Rested for an hour and felt better.",
        "available_meddra_terms": {
            "Nervous system disorders": ["Headache", "Dizziness", "Tremor"],
            "Gastrointestinal disorders": ["Nausea", "Vomiting"]
        },
        "gt_meddra_soc": "Nervous system disorders",
        "gt_meddra_pt": "Headache",
        "gt_is_serious": False
    },
    {
        "raw_narrative": "Following administration of the Rocephin antibiotic, the patient experienced a severe anaphylactic reaction requiring emergency intubation in the ICU.",
        "available_meddra_terms": {
            "Immune system disorders": ["Anaphylactic reaction", "Hypersensitivity"],
            "Respiratory disorders": ["Dyspnea", "Asthma"]
        },
        "gt_meddra_soc": "Immune system disorders",
        "gt_meddra_pt": "Anaphylactic reaction",
        "gt_is_serious": True
    },
    {
        "raw_narrative": "The subject reported feeling slightly nauseous after the first dose of Metformin. Did not seek medical attention and symptom resolved with food.",
        "available_meddra_terms": {
            "Gastrointestinal disorders": ["Nausea", "Diarrhea", "Abdominal pain"],
            "General disorders": ["Fatigue", "Malaise"]
        },
        "gt_meddra_soc": "Gastrointestinal disorders",
        "gt_meddra_pt": "Nausea",
        "gt_is_serious": False
    },
    {
        "raw_narrative": "Patient was admitted to the hospital with life-threatening liver failure one month into taking the new antifungal drug, Ketoconazole.",
        "available_meddra_terms": {
            "Hepatobiliary disorders": ["Hepatic failure", "Hepatitis", "Jaundice"],
            "Renal disorders": ["Renal impairment"]
        },
        "gt_meddra_soc": "Hepatobiliary disorders",
        "gt_meddra_pt": "Hepatic failure",
        "gt_is_serious": True
    },
    {
        "raw_narrative": "A 30-year-old man experienced visual hallucinations after taking Ambien for insomnia. He woke up while driving and was hospitalized.",
        "available_meddra_terms": {
            "Psychiatric disorders": ["Hallucination, visual", "Insomnia", "Anxiety"],
            "Nervous system disorders": ["Somnolence", "Dizziness"]
        },
        "gt_meddra_soc": "Psychiatric disorders",
        "gt_meddra_pt": "Hallucination, visual",
        "gt_is_serious": True
    },
    {
        "raw_narrative": "Patient reported a persistent dry mouth after starting Amitriptyline. Drinks more water, no other action taken.",
        "available_meddra_terms": {
            "Gastrointestinal disorders": ["Dry mouth", "Constipation"],
            "Nervous system disorders": ["Tremor"]
        },
        "gt_meddra_soc": "Gastrointestinal disorders",
        "gt_meddra_pt": "Dry mouth",
        "gt_is_serious": False
    },
    {
        "raw_narrative": "Severe tendon rupture occurred in a 65-year-old taking Ciprofloxacin for a UTI. Required surgery to repair the Achilles tendon.",
        "available_meddra_terms": {
            "Musculoskeletal and connective tissue disorders": ["Tendon rupture", "Arthralgia"],
            "Infections and infestations": ["Urinary tract infection"]
        },
        "gt_meddra_soc": "Musculoskeletal and connective tissue disorders",
        "gt_meddra_pt": "Tendon rupture",
        "gt_is_serious": True
    },
    {
        "raw_narrative": "Patient noted mild skin peeling of the face after using Tretinoin cream. Continued use, symptom persistent but tolerable.",
        "available_meddra_terms": {
            "Skin and subcutaneous tissue disorders": ["Skin exfoliation", "Erythema"],
            "General disorders": ["Pain"]
        },
        "gt_meddra_soc": "Skin and subcutaneous tissue disorders",
        "gt_meddra_pt": "Skin exfoliation",
        "gt_is_serious": False
    },
    {
        "raw_narrative": "After the second dose of the COVID-19 vaccine, the patient developed myocarditis and was admitted to the cardiology ward.",
        "available_meddra_terms": {
            "Cardiac disorders": ["Myocarditis", "Pericarditis"],
            "General disorders": ["Pyrexia", "Fatigue"]
        },
        "gt_meddra_soc": "Cardiac disorders",
        "gt_meddra_pt": "Myocarditis",
        "gt_is_serious": True
    }
]

HARD_CASES = [
    {
        "clinical_timeline": "Day 1: Started Drug A. Day 5: Developed rash. Day 6: Stopped Drug A, rash improved. Day 10: Restarted Drug A, rash returned (positive rechallenge). No other new medications or changes in diet.",
        "gt_did_event_follow_drug": True,
        "gt_is_there_alternative_cause": False,
        "gt_causality_category": "Certain"
    },
    {
        "clinical_timeline": "Day 1: Started Drug B. Day 10: Developed liver enzyme elevation. Patient also started daily heavy alcohol consumption on Day 5.",
        "gt_did_event_follow_drug": True,
        "gt_is_there_alternative_cause": True,
        "gt_causality_category": "Possible"
    },
    {
        "clinical_timeline": "Day 1: Started taking Drug C. Day 15: Had a car accident leading to a broken leg. The accident was caused by another driver running a red light.",
        "gt_did_event_follow_drug": True,
        "gt_is_there_alternative_cause": True,
        "gt_causality_category": "Unlikely"
    },
    {
        "clinical_timeline": "Day 1: Started Drug D. Day 3: Developed mild fever. No other reasonable cause identified. No rechallenge performed as the drug was continued.",
        "gt_did_event_follow_drug": True,
        "gt_is_there_alternative_cause": False,
        "gt_causality_category": "Probable"
    },
    {
        "clinical_timeline": "Patient experienced vomiting on May 1st. They started taking Drug E on May 5th for an unrelated issue.",
        "gt_did_event_follow_drug": False,
        "gt_is_there_alternative_cause": True,
        "gt_causality_category": "Unlikely"
    },
    {
        "clinical_timeline": "Day 1: Started Medication X. Day 14: Developed severe pancreatitis. Patient has chronic gallstones, a known cause of pancreatitis.",
        "gt_did_event_follow_drug": True,
        "gt_is_there_alternative_cause": True,
        "gt_causality_category": "Possible"
    },
    {
        "clinical_timeline": "Day 1: Started Medication Y. Day 2: Developed anaphylaxis. Previous history of allergy to a similar drug class noted. Recurrence upon first dose.",
        "gt_did_event_follow_drug": True,
        "gt_is_there_alternative_cause": False,
        "gt_causality_category": "Certain"
    },
    {
        "clinical_timeline": "Day 1: Started Medication Z. Day 30: Reports hair loss. Patient also underwent significant stress and weight loss during this period.",
        "gt_did_event_follow_drug": True,
        "gt_is_there_alternative_cause": True,
        "gt_causality_category": "Possible"
    },
    {
        "clinical_timeline": "Day 1: Started Medication W. Day 5: Reports increased appetite. Drug W is known to cause metabolic changes.",
        "gt_did_event_follow_drug": True,
        "gt_is_there_alternative_cause": False,
        "gt_causality_category": "Probable"
    },
    {
        "clinical_timeline": "Patient had a seizure on Monday. They starting taking a new medication on Friday of the same week.",
        "gt_did_event_follow_drug": False,
        "gt_is_there_alternative_cause": True,
        "gt_causality_category": "Unlikely"
    }
]

def get_case(task_level: str, case_index: int) -> Dict[str, Any]:
    if task_level == "easy":
        return EASY_CASES[case_index % len(EASY_CASES)]
    elif task_level == "medium":
        return MEDIUM_CASES[case_index % len(MEDIUM_CASES)]
    elif task_level == "hard":
        return HARD_CASES[case_index % len(HARD_CASES)]
    return {}
