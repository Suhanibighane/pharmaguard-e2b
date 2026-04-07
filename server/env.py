import random
import re
from typing import Dict, Any, Tuple
from server.models import PharmaAction, PharmaObservation
from server.cases import get_case, EASY_CASES, MEDIUM_CASES, HARD_CASES

def fuzzy_match(expected: str, actual: str) -> bool:
    """Utility to compare strings while ignoring case, punctuation, and extra whitespace."""
    if not actual:
        return False
    
    def clean(s: str) -> str:
        s = s.lower()
        s = re.sub(r'[^\w\s]', '', s) # Remove punctuation
        return " ".join(s.split())    # Normalize whitespace
    
    clean_expected = clean(expected)
    clean_actual = clean(actual)
    
    # Check if expected is in actual (robustness for "Aspirin 500mg" vs "Aspirin")
    return clean_expected in clean_actual or clean_actual in clean_expected

class PharmaEnv:
    def __init__(self):
        self.current_case_index = 0
        self.current_task_level = "easy"
        self.state_info = {}
        self.done = True
        self.current_step = 0
        self.max_steps = 3
        self.accumulated_reward = 0.0
        self.last_feedback = ""

    def reset(self, task_id: str = None, case_index: int = None, seed: int = None) -> PharmaObservation:
        if seed is not None:
            random.seed(seed)
            
        if task_id in ["easy", "medium", "hard"]:
            self.current_task_level = task_id
        else:
            self.current_task_level = random.choice(["easy", "medium", "hard"])
            
        if case_index is not None:
            self.current_case_index = case_index
        else:
            if self.current_task_level == "easy":
                self.current_case_index = random.randint(0, len(EASY_CASES) - 1)
            elif self.current_task_level == "medium":
                self.current_case_index = random.randint(0, len(MEDIUM_CASES) - 1)
            else:
                self.current_case_index = random.randint(0, len(HARD_CASES) - 1)
                
        self.done = False
        self.current_step = 0
        self.accumulated_reward = 0.0
        self.last_feedback = ""
        self.state_info = {
            "task_level": self.current_task_level,
            "case_index": self.current_case_index
        }
        
        return self.get_observation()
        
    def get_observation(self) -> PharmaObservation:
        case = get_case(self.current_task_level, self.current_case_index)
        obs = PharmaObservation(
            task_level=self.current_task_level,
            raw_narrative=case.get("raw_narrative", ""),
            available_meddra_terms=case.get("available_meddra_terms", None),
            clinical_timeline=case.get("clinical_timeline", None),
            case_index=self.current_case_index,
            feedback=self.last_feedback
        )
        return obs

    def step(self, action: PharmaAction) -> Tuple[PharmaObservation, float, bool, Dict[str, Any]]:
        if self.done:
            return self.get_observation(), 0.0, True, {"error": "Episode already done. Call reset."}
            
        self.current_step += 1
        case = get_case(self.current_task_level, self.current_case_index)
        
        reward = 0.0
        feedback = ""
        
        if self.current_task_level == "easy":
            reward, feedback = self._grade_easy(action, case)
        elif self.current_task_level == "medium":
            reward, feedback = self._grade_medium(action, case)
        elif self.current_task_level == "hard":
            reward, feedback = self._grade_hard(action, case)
            
        # Multi-step logic: if not perfect and steps left, allow correction
        step_penalty = (self.current_step - 1) * 0.1
        final_reward = max(reward - step_penalty, 0.0)
        
        # We define "success" as a high reward. If perfect, we're done.
        # Otherwise, if we have steps remaining, allow retry.
        if reward >= 0.95 or self.current_step >= self.max_steps:
            self.done = True
            msg = "Task complete."
        else:
            self.done = False
            msg = f"Incomplete or incorrect. {feedback} Try again."
            self.last_feedback = feedback

        return self.get_observation(), final_reward, self.done, {"message": msg, "step": self.current_step}

    def _grade_easy(self, action: PharmaAction, case: Dict[str, Any]) -> Tuple[float, str]:
        reward = 0.0
        feedback_parts = []
        
        if action.is_valid_case is not None and action.is_valid_case == case["gt_is_valid_case"]:
            reward += 0.4
        else:
            feedback_parts.append("Check if all case validity criteria (Identifiable patient, Reporter, Drug, Event) are met.")
        
        if action.suspect_drug and fuzzy_match(case["gt_suspect_drug"], action.suspect_drug):
            reward += 0.3
        else:
            feedback_parts.append("Verify the primary suspect drug name.")
            
        if action.event_term and fuzzy_match(case["gt_event_term"], action.event_term):
            reward += 0.3
        else:
            feedback_parts.append("Clarify the main adverse event term.")
            
        return reward, " ".join(feedback_parts)
        
    def _grade_medium(self, action: PharmaAction, case: Dict[str, Any]) -> Tuple[float, str]:
        reward = 0.0
        feedback_parts = []
        
        pt_correct = (action.meddra_pt and fuzzy_match(case["gt_meddra_pt"], action.meddra_pt))
        soc_correct = (action.meddra_soc and fuzzy_match(case["gt_meddra_soc"], action.meddra_soc))
        
        if pt_correct:
            reward += 0.5
        elif soc_correct:
            reward += 0.25
            feedback_parts.append("SOC is correct, but PT is not the best match.")
        else:
            feedback_parts.append("The MedDRA coding for SOC and PT needs review.")
            
        if action.is_serious is not None and action.is_serious == case["gt_is_serious"]:
            reward += 0.25
        else:
            feedback_parts.append("Re-evaluate the seriousness criteria (hospitalization, life-threatening, etc.).")
            
        return reward, " ".join(feedback_parts)
        
    def _grade_hard(self, action: PharmaAction, case: Dict[str, Any]) -> Tuple[float, str]:
        reward = 0.0
        feedback_parts = []
        
        if action.did_event_follow_drug is not None and action.did_event_follow_drug == case["gt_did_event_follow_drug"]:
            reward += 0.15
        else:
            feedback_parts.append("Carefully check the temporal sequence (did drug precede event?).")
            
        if action.is_there_alternative_cause is not None and action.is_there_alternative_cause == case["gt_is_there_alternative_cause"]:
            reward += 0.15
        else:
            feedback_parts.append("Consider if other medications or patient history provide a better explanation.")
            
        if action.causality_category and fuzzy_match(case["gt_causality_category"], action.causality_category):
            reward += 0.55
        else:
            feedback_parts.append("Review WHO-UMC criteria for certain vs probable/possible.")
            
        return reward, " ".join(feedback_parts)
