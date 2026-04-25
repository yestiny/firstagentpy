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

def chat():

# get api config from the os environment variables
    api_config = get_config()

    print(api_config["api_key"][:5] + "*****")

    """参考百炼文档实现https://bailian.console.aliyun.com/cn-beijing/?spm=5176.12818093_47.overview_recent.1.7fa82cc9Fv7yKk&tab=api#/api/?type=model&url=2833609"""

    llm = ChatOpenAI(
        api_key=api_config["api_key"],
        base_url=api_config["base_url"],
        model=api_config["model"],
        max_completion_tokens=80,
        streaming=True,
    )


    SYSTEM_PROMPT = """You are an expert weather forecaster, who speaks in puns.

You have access to two tools:

- get_weather_for_location: use this to get the weather for a specific location
- get_user_location: use this to get the user's location

If a user asks you for the weather, make sure you know the location. If you can tell from the question that they mean wherever they are, use the get_user_location tool to find their location.
You need answer in Chinese. """

# use langchain api to create an agent
    agent = create_agent(
        model=llm,
        system_prompt=SYSTEM_PROMPT,
        tools=[get_user_location, get_weather_for_location],
        context_schema=Context,
        # aliyun not supported for the formatted output
        # response_format=ToolStrategy(ResponseFormat),
        response_format=None,
        checkpointer=checkpointer

    )

    # `thread_id` is a unique identifier for a given conversation.
    config = {"configurable": {"thread_id": "1"}}


    response1 = agent.stream(
        {"messages": [{"role": "user", "content": "外面天气如何?"}]},
        config=config,
        context=Context(user_id="1"),
        stream_mode="messages"
    )
    print("==============================================")

    for msg_chunk, metadata in response1:
        print(msg_chunk.model_dump_json(), flush=True)


    print("==============================================")


    # Note that we can continue the conversation using the same `thread_id`.
    response2 = agent.invoke(
        {"messages": [{"role": "user", "content": "谢谢！"}]},
        config=config,
        context=Context(user_id="1")
    )

    ai_msg = response2["messages"][-1]
    print(ai_msg.content)

    print("==============================================")

    
    

if __name__ == "__main__":
    chat()

