# Travel Agent Runtime Demo

A minimal demo of the Amazon Bedrock AgentCore Runtime lifecycle using a Greece travel planning agent. Three phases: build the agent, test it locally, then configure and deploy it.

> Educational demo - not for production use.

## Prerequisites

- Python 3.10+
- `uv` package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- AWS CLI configured with credentials that have access to:
  - Amazon Bedrock (invoke model)
  - IAM, S3, CloudWatch (for deployment)
- Bedrock model access enabled for `claude-sonnet-4-6` in your region

## AWS Authentication

Copy the template and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` — set your region and uncomment one authentication option:

```bash
# .env
AWS_DEFAULT_REGION=us-east-1

# Option 1: SSO profile
AWS_PROFILE=<your-profile-name>

# Option 2: Access keys
# AWS_ACCESS_KEY_ID=...
# AWS_SECRET_ACCESS_KEY=...
# AWS_SESSION_TOKEN=...   # only for temporary credentials
```

If using SSO, log in first:

```bash
aws sso login --profile <your-profile-name>
```

**Verify you're on the right account before doing anything:**

```bash
uv run --env-file .env aws sts get-caller-identity
```

All commands in this project use `--env-file .env` to load credentials automatically — no manual `export` needed.

## Setup

```bash
cd travel-agent-runtime-demo
uv sync
```

---

## Phase 1: The Agent

The agent lives in `agent/` and consists of two files:

**[agent/tools.py](agent/tools.py)** — three travel planning tools:
- `get_travel_preferences()` — returns mock user preferences
- `calculate_budget(total_budget, days)` — allocates budget across flights, hotels, food, activities
- `get_destination_info(destination)` — returns info for Athens, Santorini, Mykonos

**[agent/travel_agent.py](agent/travel_agent.py)** — the runtime entrypoint:
- Wraps the Strands agent in `BedrockAgentCoreApp`
- The `@app.entrypoint` decorator marks the function AgentCore calls per invocation
- This file gets deployed to AgentCore Runtime in Phase 3

---

## Phase 2: Local Testing

Run the agent directly against Bedrock from your local machine — no container or AgentCore Runtime needed.

```bash
# Interactive REPL (agent retains conversation history within the session)
uv run --env-file .env python test/test_local.py

# Single prompt
uv run --env-file .env python test/test_local.py --prompt "Plan a 10-day trip to Greece for \$5000"
uv run --env-file .env python test/test_local.py --prompt "Tell me about Santorini"
uv run --env-file .env python test/test_local.py --prompt "What are my travel preferences?"
```

---

## Phase 3: Configure and Deploy

Phase 3 uses the `agentcore` CLI directly. All commands are run from the project root.

### 3a. Configure

The `agentcore configure` command is **interactive by default** — it walks you through each option with prompts. Run it once before deploying.

```bash
uv run --env-file .env agentcore configure
```

When prompted, enter the following values for this project:

| Prompt | Value |
|---|---|
| Entrypoint | `agent/travel_agent.py` |
| Agent name | `travel_agent_demo` (alphanumeric without hyphens) |
| Requirements file | `requirements.txt` (auto-detected, press Enter) |
| Deployment type | `1` — Direct Code Deploy |
| Python runtime version | `3` — PYTHON_3_12 |
| Execution role | Press Enter to auto-create |
| S3 Bucket | Press Enter to auto-create |
| OAuth authorizer | `no` (use default IAM authorization) |
| Request header allowlist | `no` (use defaults) |
| Memory configuration | `s` to skip |

This generates `.bedrock_agentcore.yaml` in the project root (runtime configuration) and sets the agent as the default.

**List configured agents:**

```bash
uv run --env-file .env agentcore configure list
```

### 3b. Deploy

Deploy the agent to AgentCore Runtime using Direct Code Deploy. Your source code and `requirements.txt` are uploaded to S3 — no Docker or container builds involved.

```bash
uv run --env-file .env agentcore deploy
```

This takes approximately **5-10 minutes**. It provisions:
- S3 bucket for source code
- IAM execution role
- AgentCore Runtime endpoint

**Check status** while deploying (or any time after):

```bash
uv run --env-file .env agentcore status
uv run --env-file .env agentcore status --verbose   # full JSON output
```

**Redeploy an existing agent** (avoids ConflictException):

```bash
uv run --env-file .env agentcore deploy --auto-update-on-conflict
```

### 3c. Invoke

Once status shows `READY`, invoke the deployed agent:

```bash
uv run --env-file .env agentcore invoke '{"prompt": "Plan a 10-day trip to Greece for $5000"}'
```

**Multi-turn conversation** — pass `--session-id` to maintain context across calls:

```bash
SESSION=$(python -c "import uuid; print(uuid.uuid4())")

uv run --env-file .env agentcore invoke '{"prompt": "I want to visit Greece"}' --session-id $SESSION
uv run --env-file .env agentcore invoke '{"prompt": "I have $5000 for 10 days"}' --session-id $SESSION
uv run --env-file .env agentcore invoke '{"prompt": "Tell me about Santorini"}' --session-id $SESSION
```

**Invoke a specific agent by name:**

```bash
uv run --env-file .env agentcore invoke '{"prompt": "Plan a trip"}' --agent travel-agent-demo
```

---

## Cleanup

```bash
# Preview what will be destroyed
uv run --env-file .env agentcore destroy --dry-run

# Destroy all AWS resources (S3 source, IAM role, runtime endpoint)
uv run --env-file .env agentcore destroy

# Remove generated local config
rm -f .bedrock_agentcore.yaml
```

---

## Project Structure

```
travel-agent-runtime-demo/
├── agent/                      # Phase 1: Agent definition
│   ├── tools.py                #   Three travel planning tools
│   └── travel_agent.py         #   BedrockAgentCoreApp + @app.entrypoint
├── test/                       # Phase 2: Local testing
│   └── test_local.py           #   CLI for running the agent locally
├── requirements.txt            #   Runtime deps deployed to AgentCore (minimal)
└── pyproject.toml              #   Full dev deps + uv config
```

## How It Works

1. **`BedrockAgentCoreApp()`** creates the HTTP server that AgentCore Runtime wraps your agent in.
2. **`@app.entrypoint`** marks the function AgentCore calls for each invocation request.
3. **`agentcore configure`** reads your entrypoint, sets up the deployment config (`.bedrock_agentcore.yaml`), and provisions an IAM execution role and S3 bucket.
4. **`agentcore deploy`** uploads your source code and `requirements.txt` to S3 via Direct Code Deploy, then creates the AgentCore Runtime endpoint. No Docker or container builds needed.
5. **`agentcore invoke`** calls the deployed endpoint with your prompt and returns the agent's response.

## CLI Quick Reference

All commands use `uv run --env-file .env` to load credentials from `.env`.

| Command | What it does |
|---|---|
| `uv run --env-file .env agentcore configure` | Interactive setup — generates deployment config |
| `uv run --env-file .env agentcore configure list` | List all configured agents |
| `uv run --env-file .env agentcore deploy` | Deploy to cloud via Direct Code Deploy (no Docker needed) |
| `uv run --env-file .env agentcore status` | Check agent and endpoint status |
| `uv run --env-file .env agentcore invoke '<json>'` | Invoke the deployed agent |
| `uv run --env-file .env agentcore destroy` | Delete all AWS resources (S3 source, IAM role, endpoint) |
| `uv run --env-file .env agentcore destroy --dry-run` | Preview what would be destroyed |
