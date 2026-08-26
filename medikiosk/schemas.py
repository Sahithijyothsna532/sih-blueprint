"""Data contracts used by the MediKiosk prototype."""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Medication:
    name: str
    dose: str = "Not provided"
    frequency: str = "Not provided"
    source: str = "Patient reported"


@dataclass
class DocumentExtraction:
    document_date: str = "Not provided"
    diagnoses: List[str] = field(default_factory=list)
    medications: List[Medication] = field(default_factory=list)
    investigations: List[str] = field(default_factory=list)
    source: str = "Uploaded document"
    verification_required: bool = True


@dataclass
class ClinicalHistory:
    chief_complaint: str = "Not provided"
    onset: str = "Not provided"
    duration: str = "Not provided"
    severity: str = "Not provided"
    aggravating_factors: List[str] = field(default_factory=list)
    radiation: str = "Not provided"
    associated_symptoms: List[str] = field(default_factory=list)
    past_history: List[str] = field(default_factory=list)
    medications: List[Medication] = field(default_factory=list)
    allergies: str = "Not reported"
    ayush: Dict[str, str] = field(default_factory=dict)
    red_flags: List[str] = field(default_factory=list)
    answers: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def history_from_dict(values: Dict[str, Any]) -> ClinicalHistory:
    """Build a typed history while tolerating incomplete model responses."""
    values = dict(values)
    values["medications"] = [
        item if isinstance(item, Medication) else Medication(**item)
        for item in values.get("medications", [])
    ]
    return ClinicalHistory(**{
        field_name: values[field_name]
        for field_name in ClinicalHistory.__dataclass_fields__
        if field_name in values
    })
