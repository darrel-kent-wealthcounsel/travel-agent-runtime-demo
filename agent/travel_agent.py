"""AgentCore Runtime entrypoint for the travel agent.

Deployed to AgentCore Runtime via Direct Code Deploy.
Run locally with: python agent/travel_agent.py
"""

import logging
import os

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel

from agent.tools import calculate_budget, get_destination_info, get_travel_preferences

os.environ.setdefault("STRANDS_TOOL_CONSOLE_MODE", "enabled")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- AgentCore app ---
app = BedrockAgentCoreApp()

# --- Model & agent (module-level: instantiated once at runtime start) ---
MODEL_ID = "us.anthropic.claude-sonnet-4-6"

SYSTEM_PROMPT = """
You are an AI Travel Companion specializing in planning trips to Greece.
Your expertise includes:
- Budget optimization and allocation across flights, hotels, food, and activities
- Destination information for Athens, Santorini, and Mykonos
- Personalized recommendations based on user travel preferences

Always be helpful, friendly, and provide clear explanations for your recommendations.
If the user asks about a destination you don't have data for, let them know which
destinations you can help with.
"""

model = BedrockModel(model_id=MODEL_ID)

travel_agent = Agent(
    model=model,
    tools=[get_travel_preferences, calculate_budget, get_destination_info],
    system_prompt=SYSTEM_PROMPT,
)


@app.entrypoint
def invoke(payload):
    """AgentCore Runtime entrypoint.

    Called by AgentCore for each invocation.
    Expected payload: {"prompt": "..."}
    Returns: str response from the agent
    """
    user_input = payload.get("prompt", "")
    logger.info("Received prompt: %s", user_input)

    response = travel_agent(user_input)
    return response.message["content"][0]["text"]


if __name__ == "__main__":
    # Allows local testing via: python agent/travel_agent.py
    app.run()
