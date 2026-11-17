import datetime
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

def get_system_time() -> str:
    """Returns the current local date and time on the user's Linux Mint machine."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

root_agent = Agent(
    name="gemma_local_agent",
    model=LiteLlm(model="ollama_chat/gemma4:e2b"),
    description="A local assistant running on Gemma 4 via Ollama.",
    instruction=(
        "You are a helpful local AI assistant running on Linux Mint. "
        "Use the get_system_time tool whenever the user asks for the current time or date."
    ),
    tools=[get_system_time],
)