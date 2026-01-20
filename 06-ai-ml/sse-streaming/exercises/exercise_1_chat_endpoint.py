"""
Exercise 1: Build a Chat Endpoint

Create an SSE endpoint that streams chat responses for a simple chatbot.

Requirements:
1. Create a FastAPI endpoint at /chat that accepts a prompt parameter
2. Stream the response token by token
3. Support optional system_prompt parameter
4. Include proper SSE headers
5. Send [DONE] marker when complete

Bonus:
- Add message history support
- Include token count in final event

Hints:
- Use StreamingResponse with async generator
- Format: data: {"content": "token"}\n\n
- Remember double newline at end of each event
"""

from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
import asyncio
import json

app = FastAPI(title="Chat Endpoint Exercise")


# TODO: Implement the chat response generator
async def generate_chat_response(prompt: str, system_prompt: str = None):
    """
    Generate chat response as SSE events.

    Args:
        prompt: User's message
        system_prompt: Optional system prompt for context

    Yields:
        SSE formatted strings with content chunks
    """
    # TODO: Implement streaming response
    # 1. If you have OPENAI_API_KEY, use OpenAI streaming
    # 2. Otherwise, create a mock response
    # 3. Yield events in format: data: {"content": "..."}\n\n
    # 4. End with: data: [DONE]\n\n
    pass


# TODO: Create the chat endpoint
@app.get("/chat")
async def chat_endpoint(
    prompt: str = Query(..., description="User message"),
    system_prompt: str = Query(None, description="Optional system prompt")
):
    """
    Chat endpoint that streams responses.

    Returns SSE stream of chat tokens.
    """
    # TODO: Implement
    # 1. Create StreamingResponse with generate_chat_response
    # 2. Set media_type to "text/event-stream"
    # 3. Include proper headers (Cache-Control, Connection, X-Accel-Buffering)
    pass


@app.get("/")
async def info():
    return {
        "exercise": "Chat Endpoint",
        "endpoints": {"/chat": "Chat streaming endpoint"},
        "example": "/chat?prompt=Hello"
    }


# Test your implementation
if __name__ == "__main__":
    import uvicorn

    print("Exercise 1: Chat Endpoint")
    print("=" * 50)
    print("\nImplement the chat endpoint and test with:")
    print('  curl -N "http://localhost:8010/chat?prompt=Hello"')
    print("\nExpected output:")
    print('  data: {"content": "Hello"}')
    print('  data: {"content": "!"}')
    print('  data: [DONE]')

    uvicorn.run(app, host="0.0.0.0", port=8010)
