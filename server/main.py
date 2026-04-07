from fastapi import FastAPI, Request
from server.models import ResetRequest, StepRequest, StepResponse, PharmaObservation
from server.env import PharmaEnv
from pydantic import BaseModel

class ResetResponse(BaseModel):
    observation: PharmaObservation

app = FastAPI(title="PharmaGuard-E2B OpenEnv")
env = PharmaEnv()

@app.post("/reset", response_model=ResetResponse)
async def reset(request: Request):
    # Support empty body or populated body
    body = await request.json() if await request.body() else {}
    req = ResetRequest(**body)
    
    task_id = req.task_id
    case_index = req.case_index
    seed = req.seed
    
    obs = env.reset(task_id=task_id, case_index=case_index, seed=seed)
    return ResetResponse(observation=obs)

@app.post("/step", response_model=StepResponse)
async def step(request: StepRequest):
    obs, reward, done, info = env.step(request.action)
    return StepResponse(observation=obs, reward=reward, done=done, info=info)

@app.get("/state")
async def state():
    return {
        "task_level": env.current_task_level,
        "case_index": env.current_case_index,
        "done": env.done
    }

@app.get("/")
async def read_root():
    return {"status": "ok", "app": "PharmaGuard-E2B OpenEnv"}
