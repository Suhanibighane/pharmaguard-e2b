from typing import Optional, Dict, List, Any
from pydantic import BaseModel

class PharmaObservation(BaseModel):
    task_level: str  # "easy", "medium", "hard"
    raw_narrative: str
    available_meddra_terms: Optional[Dict[str, List[str]]] = None
    clinical_timeline: Optional[str] = None
    case_index: int = 0
    feedback: Optional[str] = None

class PharmaAction(BaseModel):
    # Task 1 fields
    is_valid_case: Optional[bool] = None
    suspect_drug: Optional[str] = None
    event_term: Optional[str] = None
    
    # Task 2 fields
    meddra_soc: Optional[str] = None
    meddra_pt: Optional[str] = None
    is_serious: Optional[bool] = None
    
    # Task 3 fields
    did_event_follow_drug: Optional[bool] = None
    is_there_alternative_cause: Optional[bool] = None
    causality_category: Optional[str] = None # "Certain", "Probable", "Possible", "Unlikely"

class StepResponse(BaseModel):
    observation: PharmaObservation
    reward: float
    done: bool
    info: Dict[str, Any]

class ResetRequest(BaseModel):
    task_id: Optional[str] = None
    case_index: Optional[int] = None
    seed: Optional[int] = None

class StepRequest(BaseModel):
    action: PharmaAction
