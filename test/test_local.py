#!/usr/bin/env python3
"""Phase 2: Test the travel agent locally before deploying.

Runs the agent directly against Amazon Bedrock from your local machine.
No container, no AgentCore Runtime required - just valid AWS credentials
with Bedrock access.

Usage:
    uv run python test/test_local.py
    uv run python test/test_local.py --prompt "Plan a 10-day Greece trip for $5000"
"""

import os
import sys

import click

# Ensure the project root is on the path so `agent/` imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from strands import Agent
from strands.models import BedrockModel

from agent.tools import calculate_budget, get_destination_info, get_travel_preferences

MODEL_ID = "us.anthropic.claude-sonnet-4-6"

SYSTEM_PROMPT = """
You are an AI Travel Companion specializing in planning trips to Greece.
Your expertise includes:
- Budget optimization and allocation across flights, hotels, food, and activities
- Destination information for Athens, Santorini, and Mykonos
- Personalized recommendations based on user travel preferences

Always be helpful, friendly, and provide clear explanations for your recommendations.
"""


def build_agent() -> Agent:
    model = BedrockModel(model_id=MODEL_ID)
    return Agent(
        model=model,
        tools=[get_travel_preferences, calculate_budget, get_destination_info],
        system_prompt=SYSTEM_PROMPT,
    )


@click.command()
@click.option(
    "--prompt",
    "-p",
    default=None,
    help="Single prompt to send. Omit for interactive REPL mode.",
)
def main(prompt: str):
    """Run the travel agent locally for testing."""
    agent = build_agent()

    if prompt:
        print(f"\nYou: {prompt}")
        response = agent(prompt)
        print(f"\nAgent: {response.message['content'][0]['text']}\n")
        return

    # Interactive REPL - agent retains conversation history within the session
    print("Travel Agent - Local Test Mode")
    print("Type 'quit' or 'exit' to stop.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not user_input or user_input.lower() in ("quit", "exit"):
            break

        response = agent(user_input)
        print(f"\nAgent: {response.message['content'][0]['text']}\n")


if __name__ == "__main__":
    main()
