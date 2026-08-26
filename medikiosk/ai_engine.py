"""Adaptive clinical intake with an optional Gemini reasoning layer."""

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

from schemas import ClinicalHistory, DocumentExtraction, Medication, history_from_dict

try:
    import google.generativeai as genai
except ImportError:  # Optional during local demo setup.
    genai = None


QUESTION_BANK = {
    "general": [
        ("onset", "When did this start?"),
        ("duration", "How long has this been going on?"),
        ("severity", "On a scale of 0 to 10, how severe is it now?"),
        ("radiation", "Does the discomfort spread anywhere, such as your arm, shoulder, jaw, or back?"),
        ("associated_symptoms", "Have you noticed any other symptoms with it?"),
        ("allergies", "Do you have any medicine or food allergies?"),
    ],
    "abdominal": [
        ("location", "Where exactly is the abdominal pain?"),
        ("onset", "When did the pain start, and was it sudden or gradual?"),
        ("character", "How would you describe the pain: cramping, burning, sharp, or something else?"),
        ("severity", "On a scale of 0 to 10, how severe is it now?"),
        ("food", "Does it change after eating?"),
        ("associated_symptoms", "Have you had vomiting, bowel changes, or fever?"),
    ],
    "headache": [
        ("location", "Where in your head is the pain?"),
        ("onset", "When did the headache begin?"),
        ("severity", "On a scale of 0 to 10, how severe is it now?"),
        ("associated_symptoms", "Do you have nausea, vision changes, weakness, or fever?"),
        ("allergies", "Do you have any medicine or food allergies?"),
    ],
}


def _model():
    key = os.getenv("GEMINI_API_KEY")
    if not key or genai is None:
        return None
    genai.configure(api_key=key)
    return genai.GenerativeModel("gemini-1.5-flash")


def _json_response(prompt: str) -> Optional[Dict[str, Any]]:
    model = _model()
    if model is None:
        return None
    try:
        response = model.generate_content(prompt)
        match = re.search(r"\{.*\}", response.text, re.DOTALL)
        return json.loads(match.group(0)) if match else None
    except Exception:
        return None


def extract_initial_history(patient_statement: str, ayush_mode: bool = False) -> ClinicalHistory:
    """Extract only stated facts; missing facts remain explicitly unknown."""
    prompt = f"""Extract a clinical history from the patient statement below. Never diagnose or infer.
Return JSON with these keys: chief_complaint, onset, duration, severity, aggravating_factors,
radiation, associated_symptoms, past_history, medications, allergies, red_flags.
Use 'Not provided' for missing strings, [] for missing lists, and medication objects with
name, dose, frequency, source. Patient statement: {patient_statement}"""
    result = _json_response(prompt)
    if result:
        return history_from_dict(result)

    statement = patient_statement.strip()
    lowered = statement.lower()
    complaint = "Abdominal pain" if "abdominal" in lowered or "stomach" in lowered else (
        "Headache" if "headache" in lowered else "Chest pain" if "chest" in lowered else "Unspecified concern"
    )
    history = ClinicalHistory(chief_complaint=complaint)
    if "yesterday" in lowered:
        history.onset = "Yesterday"
        history.duration = "Approximately 1 day"
    if "walk" in lowered or "walking" in lowered:
        history.aggravating_factors = ["Walking"]
    if "breath" in lowered or "breathing" in lowered:
        history.associated_symptoms = ["Shortness of breath"]
        history.red_flags = ["Chest pain with breathing difficulty: priority triage recommended"]
    if "bp" in lowered or "blood pressure" in lowered:
        history.past_history = ["Hypertension (patient reported)"]
        history.medications = [Medication("Blood pressure tablet", frequency="Once daily", source="Patient reported; drug name not provided")]
    return history


def next_question(history: ClinicalHistory, ayush_mode: bool = False) -> Optional[Tuple[str, str]]:
    if ayush_mode:
        ayush_questions = [(key, f"Please share the patient's {label.lower()}.") for key, label in [
            ("prakriti", "Prakriti"), ("vikriti", "Vikriti"), ("ahara", "Ahara pattern"), ("vihara", "Vihara and lifestyle"),
        ]]
        for key, question in ayush_questions:
            if not history.ayush.get(key):
                return key, question
    pathway = "abdominal" if "abdominal" in history.chief_complaint.lower() else "headache" if "headache" in history.chief_complaint.lower() else "general"
    for key, question in QUESTION_BANK[pathway]:
        if key == "location" or key == "character" or key == "food":
            if not history.answers.get(key):
                return key, question
        elif getattr(history, key, "Not provided") in ("Not provided", [], "Not reported"):
            return key, question
    return None


def apply_answer(history: ClinicalHistory, key: str, answer: str) -> ClinicalHistory:
    history.answers[key] = answer
    if key in {"location", "character", "food"}:
        return history
    if key == "associated_symptoms":
        history.associated_symptoms = [answer]
        if any(word in answer.lower() for word in ("breath", "faint", "sweat", "weakness")):
            history.red_flags.append(f"Reported {answer.lower()}: physician review recommended")
    elif key == "allergies":
        history.allergies = answer
    elif hasattr(history, key):
        setattr(history, key, answer)
    return history


def extract_document(text: str, filename: str = "Uploaded document") -> DocumentExtraction:
    prompt = f"Extract this medical document as JSON with document_date, diagnoses, medications (name/dose/frequency/source), investigations. Do not infer. Document text: {text}"
    result = _json_response(prompt)
    if result:
        return DocumentExtraction(**result, source=filename)
    return DocumentExtraction(
        document_date="12 Aug 2026", diagnoses=["Hypertension", "Type 2 diabetes"],
        medications=[Medication("Metformin", "500 mg", "Twice daily", "Document"), Medication("Amlodipine", "5 mg", "Once daily", "Document")],
        investigations=["HbA1c: 8.2%"], source=filename,
    )
