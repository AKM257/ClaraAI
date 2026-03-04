# Clara AI Pipeline

## Overview
An automation pipeline that converts call transcripts into deployable AI voice agent configurations for Clara Answers. Built for service trade businesses (fire protection, electrical, HVAC, etc.).

## Architecture
```
Transcript (.txt)
     ↓
extract_memo.py        → account_memo.json (v1)
     ↓
generate_agent_spec.py → agent_spec.json (v1)
     ↓
apply_onboarding.py    → account_memo.json (v2) + changes.md
     ↓
generate_agent_spec.py → agent_spec.json (v2)
```

## Tech Stack (All Free, Zero Cost)
- **LLM**: Groq API (llama-3.3-70b-versatile) - free tier, no credit card
- **Automation**: n8n self-hosted via Docker
- **API Server**: Flask (bridges n8n to Python scripts)
- **Storage**: GitHub + JSON files
- **Language**: Python 3.11

## Setup

### 1. Clone the repo
```
git clone https://github.com/AKM257/ClaraAI.git
cd ClaraAI
```

### 2. Install dependencies
```
pip install groq python-dotenv requests flask
```

### 3. Set up environment variables
```
cp .env.example .env
```
Fill in your Groq API key in `.env`:
```
GROQ_API_KEY=your_groq_api_key_here
```
Get a free key at: https://console.groq.com

### 4. Add transcript files
- Place demo call transcripts in `dataset/demo_calls/`
- Place onboarding call transcripts in `dataset/onboarding_calls/`
- Files must be `.txt` format

## How to Run

### Option A - Run Python directly
```
cd scripts
python run_pipeline.py
```

### Option B - Run via n8n (visual workflow)
Start the Flask API server:
```
python scripts/api_server.py
```
Start n8n:
```
docker run -it --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n
```
Open http://localhost:5678, import `workflows/pipeline_a.json`, and click Execute Workflow.

## Output Structure
```
outputs/accounts/<account_id>/
├── v1/
│   ├── account_memo.json    ← extracted from demo call
│   └── agent_spec.json      ← generated agent configuration
├── v2/
│   ├── account_memo.json    ← updated after onboarding
│   ├── agent_spec.json      ← updated agent configuration
│   └── changes.md           ← what changed and why
└── onboarding_temp/
    └── account_memo.json    ← intermediate onboarding extraction
```

## Pipeline Behavior
- **Idempotent**: Running twice skips already-processed files
- **Logged**: Every run creates a timestamped log in `logs/`
- **Batch-capable**: Processes all files in dataset folders automatically
- **Safe**: Missing data flagged in `questions_or_unknowns`, never hallucinated

## Known Limitations
- Requires text transcripts (not raw audio)
- Tested on 1 sample transcript (pipeline designed for batch processing)
- Groq free tier has rate limits - add delays if processing many files at once

## What I Would Improve with Production Access
- Real Retell API calls to auto-deploy agents
- Whisper transcription for audio files
- Webhook triggers for automatic processing
- Dedicated onboarding form parser
- Dashboard to view all accounts and their status