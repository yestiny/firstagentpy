from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from agent.agent2 import create_weather_agent, invoke_agent, stream_agent

app = FastAPI()

# Create agent on startup
agent = create_weather_agent()


@app.get("/chat")
def chat(q: str = None):
    if not q:
        return "请提供问题"
    response = invoke_agent(agent, q)
    ai_msg = response["messages"]
    # Return the last AI message content
    for msg in reversed(ai_msg):
        if hasattr(msg, 'type') and msg.type == "ai":
            return msg.content
    return "未找到回答"


@app.get("/stream")
def stream(q: str = None):
    if not q:
        return "请提供问题"

    def generate():
        print("DEBUG: generate() started", flush=True)
        gen = stream_agent(agent, q)
        print(f"DEBUG: got generator: {gen}", flush=True)
        try:
            for i, chunk in enumerate(gen):
                print(f"DEBUG: chunk {i}: {chunk.keys() if isinstance(chunk, dict) else chunk}", flush=True)
                if chunk.get("type") == "messages":
                    token, metadata = chunk.get("data")
                    content_repr = repr(token.content)[:100]
                    print(f"DEBUG: token type: {type(token)}, content: {content_repr}", flush=True)
                    if hasattr(token, 'content_blocks') and token.content_blocks:
                        for block in token.content_blocks:
                            if hasattr(block, 'text') and block.text:
                                print(f"DEBUG: yielding text: {block.text[:50]}", flush=True)
                                yield f"data: {block.text}\n\n".encode()
                    else:
                        print("DEBUG: no content_blocks or empty", flush=True)
                else:
                    print(f"DEBUG: chunk type != messages", flush=True)
        except Exception as e:
            print(f"DEBUG: exception: {e}", flush=True)
            import traceback
            traceback.print_exc()
            yield f"data: [Error: {str(e)}]\n\n".encode()
        print("DEBUG: generate() done", flush=True)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )