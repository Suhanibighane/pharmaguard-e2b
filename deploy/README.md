---
title: PharmaGuard E2B Env
emoji: 💊
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---
# PharmaGuard-E2B OpenEnv

PharmaGuard-E2B is a fully compliant OpenEnv environment designed to train LLM agents as Drug Safety Associates. The agent triages adverse event reports according to ICH E2B(R3) regulatory standards.

## Tasks & Difficulties

1.  **Task 1 (Easy) - The "Signal Detector"**: Identify if a raw patient narrative constitutes a "Valid Case". The agent must extract suspect drugs and adverse events.
2.  **Task 2 (Medium) - The "MedDRA Coder"**: Extract structured data and classify the adverse event using the Medical Dictionary for Regulatory Activities (MedDRA) hierarchy.
3.  **Task 3 (Hard) - The "Causality Architect"**: Perform a WHO-UMC Causality Assessment on complex clinical timelines to determine causality thresholds (Certain, Probable, Possible, Unlikely).

## Action and Observation Spaces

Defined as Pydantic v2 schemas:

**Observations** provide the raw narrative or clinical timeline depending on task difficulty.
**Actions** require strict extraction depending on the task:
- `is_valid_case`, `suspect_drug`, `event_term`
- `meddra_soc`, `meddra_pt`, `is_serious`
- `did_event_follow_drug`, `is_there_alternative_cause`, `causality_category`

## Setup & Running Locally

Ensure you have docker installed.

```bash
# Build the image
docker build -t pharmaguard .

# Run the container
docker run -p 7860:7860 pharmaguard
```

## Baseline Scores

The baseline has been established using `Qwen/Qwen2.5-72B-Instruct` via the Hugging Face Router:

| Task Level | Average Score | Description |
| --- | --- | --- |
| **Easy** | ~0.85 - 0.95 | Models easily identify the valid cases and extract basic information. |
| **Medium** | ~0.60 - 0.70 | MedDRA classification can be tricky without an external ontology lookup, requiring models to rely on internal medical knowledge. |
| **Hard** | ~0.35 - 0.50 | The WHO-UMC Causality Assessment requires complex temporal reasoning (did the adverse event strictly follow the drug ingestion without alternative causes). Frontier models occasionally struggle with strict adherence. |

## Running the Baseline

To run the standard baseline provided in `inference.py`:

```bash
pip install -r requirements.txt
export HF_TOKEN="your-hf-token"
export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"
python inference.py
```

## OpenEnv Manifest Configuration

This environment complies with the OpenEnv specification by including an `openenv.yaml` manifest that defines deployment configuration for Hugging Face Spaces:

```yaml
spec_version: 1
name: pharmaguard-e2b
type: space
runtime: fastapi
app: server.main:app
port: 7860
```
