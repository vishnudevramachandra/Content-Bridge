import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
import httpx

from pydantic import BaseModel
from contentbridge.agents.discovery.discovery_agent import run_agent

_INSTRUCTIONS = (
    "You are an Orchestrator Agent that ......\n"
)

provider = OpenAIProvider(
    base_url=get_env("OPENAI_API_BASE"),
    api_key=get_env("OPENAI_API_KEY"),
)

model = OpenAIResponsesModel(
    model_name=get_env("MODEL"),
    provider=provider,
)

orchestrator_agent = Agent[AgentDeps](
    model=model,
    instructions=_INSTRUCTIONS,
    capabilities=[
        file_operations(),
        run_discovery_agent(),
        ...
    ],
    deps_type=AgentDeps,
)

app = FastAPI(title="Content-bridge Backend")

event_queue: asyncio.Queue = asyncio.Queue()

session_state = {
    "latest_agent_response": "System initializing... Please type an instruction.",
    "message_history": []
}

class UserPromptRequest(BaseModel):
    message: str


@app.post("/api/chat")
async def receive_user_msg(payload: UserPromptRequest):
    text = payload.message.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    await event_queue.put(("user", f"User Input: {text}"))

    return {"status": "queued", "message": "User input has been fed to the agent loop."}


@app.get("/api/status")
async def get_agent_status():
    return {
        "agent_response": session_state["latest_agent_response"],
        "history_length": len(session_state["message_history"])
    }


async def periodic_timer_worker() -> None:
    """Triggers system events natively every 5s without human input."""
    while True:
        await asyncio.sleep(5) 
        periodic_msg = "SYSTEM ALERT: Periodic 5-second health check triggered."
        await event_queue.put(("system", periodic_msg))


async def central_orchestrator():
    """
    Background task that runs for the lifespan of the server.
    Listens to the event_queue, invokes PydanticAI, and mutates state.
    """
    async with httpx.AsyncClient() as http_client:
        deps = AgentDeps(
            event_queue=event_queue,
            http_client=http_client,
            search_api_key=get_env("SEARCH_API_KEY"),
        )
        
        # Initialize with a startup prompt
        next_prompt = None
        
        print("\n[Worker] Agent Coordinator Loop Activated.")
        
        while True:
            if next_prompt:
                print(f"\n[Worker Running AI Task] -> {next_prompt[:60]}...")
                
                # Execute Agent A with history context preserved
                result = await orchestrator_agent.run(
                    next_prompt, 
                    deps=deps,
                    message_history=session_state["message_history"]
                )
                
                # Persist token tracking data and store latest answer string
                session_state["latest_agent_response"] = result.data
                session_state["message_history"] = result.all_messages()
                
                print(f"[Worker AI Result] -> {result.data}")
                next_prompt = None
                
            # Wakes up when /api/chat receives a request or the timer worker fires.
            source, event_text = await event_queue.get()
            next_prompt = event_text


@app.on_event("startup")
async def startup_event():
    """Spins up the non-blocking background workers when FastAPI starts."""
    asyncio.create_task(central_orchestrator())
    asyncio.create_task(periodic_timer_worker())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
