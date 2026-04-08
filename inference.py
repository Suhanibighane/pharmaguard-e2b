import os
import textwrap
import json
import asyncio
import re
from typing import List, Optional, Any, Dict
from openai import OpenAI
import httpx

# --- OpenEnv Compliance Configuration ---
# Defaults are set only for API_BASE_URL and MODEL_NAME (not HF_TOKEN)
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

# Environment URL (defaulting to localhost for local testing)
ENV_URL = os.getenv("ENV_URL", "http://localhost:7860")

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    # Normalize action to one line for strict logging
    action_log = str(action).replace('\n', ' ')
    print(f"[STEP] step={step} action={action_log} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

def get_model_action(client: OpenAI, task_level: str, obs_dict: Dict[str, Any]) -> str:
    system_prompt = textwrap.dedent("""
    You are an AI acting as a Pharmacovigilance (PV) Drug Safety Associate. 
    Your goal is to triage and code adverse event reports accurately.
    
    If you receive "feedback" in the observation, use it to correct your previous mistake.
    
    If task=easy: 
    Output JSON with: "is_valid_case" (bool), "suspect_drug" (string), "event_term" (string).
    
    If task=medium:
    Output JSON with: "meddra_soc" (string), "meddra_pt" (string), "is_serious" (bool).
    
    If task=hard:
    Output JSON with: "did_event_follow_drug" (bool), "is_there_alternative_cause" (bool), "causality_category" (string).
    WHO-UMC Causality Guide:
    - certain: Logical timing, no other causes, positive rechallenge.
    - probable: Logical timing, no other causes, but no rechallenge data.
    - possible: Logical timing, BUT there is an alternative cause (e.g. alcohol, history).
    - unlikely: Timing is bad or the alternative cause is clearly the primary driver.
    """).strip()

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Task: {task_level}\nObservation: {json.dumps(obs_dict)}"},
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        return completion.choices[0].message.content.strip()
    except Exception as exc:
        return f'{{"error": "{str(exc)}"}}'

async def run_task(client: OpenAI, task_level: str, seed: int):
    log_start(task=task_level, env="pharmaguard-e2b", model=MODEL_NAME)
    
    rewards: List[float] = []
    max_steps = 3
    total_score = 0.005 # Ensure start score satisfies (0,1) range
    success = False
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as http:
            # 1. Reset
            reset_req = {"task_id": task_level, "seed": seed}
            resp = await http.post(f"{ENV_URL}/reset", json=reset_req)
            resp.raise_for_status()
            
            obs = resp.json().get("observation", {})
            done = False
            step = 1
            
            # Multi-step interaction loop
            while not done and step <= max_steps:
                action_text = get_model_action(client, task_level, obs)
                
                try:
                    # Robust Extraction: Find first { and last }
                    match = re.search(r"(\{.*\})", action_text, re.DOTALL)
                    if match:
                        cleaned_text = match.group(1)
                        action_json = json.loads(cleaned_text)
                    else:
                        # Fallback to previous cleanup
                        cleaned_text = action_text.strip()
                        if cleaned_text.startswith("```json"): cleaned_text = cleaned_text[7:]
                        if cleaned_text.startswith("```"): cleaned_text = cleaned_text[3:]
                        if cleaned_text.endswith("```"): cleaned_text = cleaned_text[:-3]
                        action_json = json.loads(cleaned_text.strip())
                except Exception as e:
                    print(f"[DEBUG] json parse failed: {e}")
                    cleaned_text = action_text # use raw for logging if parsing failed
                    action_json = {"error": "Invalid JSON mapping"}
                
                # 2. Step
                step_req = {"action": action_json}
                step_resp = await http.post(f"{ENV_URL}/step", json=step_req)
                step_resp.raise_for_status()
                
                step_data = step_resp.json()
                obs = step_data.get("observation", {})
                reward = step_data.get("reward", 0.005)
                done = step_data.get("done", True)
                error = step_data.get("info", {}).get("error", None)
                
                rewards.append(reward)
                log_step(step=step, action=cleaned_text, reward=reward, done=done, error=error)
                
                total_score = float(reward) # Capture last reward even if not done
                if done:
                    success = total_score >= 0.7
                
                step += 1
                
    except Exception as e:
        print(f"[DEBUG] Error during trajectory: {e}", flush=True)
        total_score = 0.005

    # Final safety clamp for OpenEnv range (0, 1)
    total_score = max(min(total_score, 0.995), 0.005)
    
    log_end(success=success, steps=len(rewards), score=total_score, rewards=rewards)
    return total_score

async def main() -> None:
    if not HF_TOKEN:
        print("Error: HF_TOKEN environment variable not set.")
        return
        
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
    
    # Run through the 3 difficulty tasks
    tasks = ["easy", "medium", "hard"]
    for i, t in enumerate(tasks):
        print(f"\n--- Testing Level: {t.upper()} ---")
        await run_task(client, t, seed=100 + i)
        
if __name__ == "__main__":
    asyncio.run(main())
