from langchain_openai import ChatOpenAI
from config.config import get_config
from langchain.agents import create_agent
from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime
from langgraph.checkpoint.memory import InMemorySaver
from dataclasses import dataclass
from langchain.agents.structured_output import ToolStrategy
import json
from openai import OpenAI
from langgraph.graph import StateGraph

# define response format
@dataclass
class ResponseFormat:
    """Response schema for the agent."""
    # A punny response (always required)
    punny_response: str
    # Any interesting information about the weather if available
    weather_conditions: str | None = None

# add memory
checkpointer = InMemorySaver()


@tool
def get_weather_for_location(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

@dataclass
class Context:
    """Custom runtime context schema."""
    user_id: str

@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """Retrieve user information based on user ID."""
    user_id = runtime.context.user_id
    return "悉尼" if user_id == "1" else "墨尔本"

def create_weather_agent():
    """Create and return the weather agent."""
    api_config = get_config()

    llm = ChatOpenAI(
        api_key=api_config["api_key"],
        base_url=api_config["base_url"],
        model=api_config["model"],
        max_completion_tokens=500,
        streaming=True,
    )

    SYSTEM_PROMPT = """You are an expert weather forecaster, who speaks in puns.

You have access to two tools:

- get_weather_for_location: use this to get the weather for a specific location
- get_user_location: use this to get the user's location

If a user asks you for the weather, make sure you know the location. If you can tell from the question that they mean wherever they are, use the get_user_location tool to find their location.
You need answer in Chinese."""

    agent = create_agent(
        model=llm,
        system_prompt=SYSTEM_PROMPT,
        tools=[get_user_location, get_weather_for_location],
        context_schema=Context,
        response_format=None,
        checkpointer=checkpointer
    )
    return agent


def invoke_agent(agent, user_message: str, thread_id: str = "1"):
    """Invoke the agent with a user message and return the response."""
    config = {"configurable": {"thread_id": thread_id}}
    response = agent.invoke(
        {"messages": [{"role": "user", "content": user_message}]},
        config=config,
        context=Context(user_id="1")
    )
    return response


def stream_agent(agent, user_message: str, thread_id: str = "1"):
    """Stream the agent response as chunks."""
    config = {"configurable": {"thread_id": thread_id}}
    return agent.stream(
        {"messages": [{"role": "user", "content": user_message}]},
        config=config,
        context=Context(user_id="1"),
        stream_mode="messages",
        version="v2",
    )


def chat():
    """Main entry point for standalone execution."""
    api_config = get_config()
    print(api_config["api_key"][:5] + "*****")

    agent = create_weather_agent()
    config = {"configurable": {"thread_id": "1"}}

    print("STREAM_BEGIN==============================================")
    print("STREAM_END==============================================")

    response2 = invoke_agent(agent, "谢谢！")
    print("INVOKE_BEGIN==============================================")

    ai_msg = response2["messages"]
    for msg in ai_msg:
        msg.pretty_print()

    print("INVOKE_END==============================================")


if __name__ == "__main__":
    chat()

