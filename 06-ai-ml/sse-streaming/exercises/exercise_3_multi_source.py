"""
Exercise 3: Multi-Source Stream Aggregation

Create an SSE endpoint that aggregates multiple data sources into one stream.

Requirements:
1. Create multiple async data sources (news, weather, stocks)
2. Aggregate them into a single SSE stream
3. Each event should include source identifier
4. Handle source failures gracefully
5. Continue streaming from working sources if one fails

Bonus:
- Add priority levels to sources
- Implement backpressure handling

Hints:
- Use asyncio.Queue for merging sources
- Use asyncio.create_task for parallel source consumption
- Track which sources are still active
"""

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json
import random
from datetime import datetime

app = FastAPI(title="Multi-Source Streaming Exercise")


# TODO: Implement individual data sources

async def news_source():
    """
    Generate mock news updates.

    Yields news items every 1-3 seconds.
    Should yield 5 items then complete.
    """
    # TODO: Implement
    # Yield dictionaries with: source, title, category
    pass


async def weather_source():
    """
    Generate mock weather updates.

    Yields weather data every 2-4 seconds.
    Should yield 3 items then complete.
    """
    # TODO: Implement
    # Yield dictionaries with: source, temperature, condition, location
    pass


async def stocks_source():
    """
    Generate mock stock updates.

    Yields stock data every 0.5-1 second.
    Should yield 10 items then complete.
    Has 20% chance of failure for testing.
    """
    # TODO: Implement
    # Yield dictionaries with: source, symbol, price, change
    # Randomly raise exception to test error handling
    pass


# TODO: Implement the stream aggregator

async def aggregate_sources(*sources):
    """
    Aggregate multiple async sources into one stream.

    Args:
        *sources: Async generator functions to aggregate

    Yields:
        SSE formatted events from all sources
    """
    # TODO: Implement
    # 1. Create a queue for merged events
    # 2. Start a task for each source that puts items in queue
    # 3. Track active sources
    # 4. Yield from queue until all sources complete
    # 5. Handle individual source failures gracefully
    pass


# TODO: Create the aggregated stream endpoint

@app.get("/stream/all")
async def aggregated_stream():
    """
    Stream aggregated data from all sources.

    Returns SSE stream with events from news, weather, and stocks.
    """
    # TODO: Implement
    # 1. Call aggregate_sources with all source functions
    # 2. Return as StreamingResponse
    pass


# Individual source endpoints for testing

@app.get("/stream/news")
async def news_stream():
    """Stream only news updates."""
    async def gen():
        async for item in news_source():
            yield f"data: {json.dumps(item)}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")


@app.get("/stream/weather")
async def weather_stream():
    """Stream only weather updates."""
    async def gen():
        async for item in weather_source():
            yield f"data: {json.dumps(item)}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")


@app.get("/stream/stocks")
async def stocks_stream():
    """Stream only stock updates."""
    async def gen():
        try:
            async for item in stocks_source():
                yield f"data: {json.dumps(item)}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")


@app.get("/")
async def info():
    return {
        "exercise": "Multi-Source Aggregation",
        "endpoints": {
            "/stream/all": "Aggregated stream from all sources",
            "/stream/news": "News only",
            "/stream/weather": "Weather only",
            "/stream/stocks": "Stocks only (may fail)"
        }
    }


# Test your implementation
if __name__ == "__main__":
    import uvicorn

    print("Exercise 3: Multi-Source Stream Aggregation")
    print("=" * 50)
    print("\nTest endpoints:")
    print('  Individual: curl -N "http://localhost:8012/stream/news"')
    print('  Aggregated: curl -N "http://localhost:8012/stream/all"')
    print("\nExpected behavior:")
    print("  - Events from all sources interleaved")
    print("  - Each event has 'source' field")
    print("  - Stream continues if one source fails")
    print("  - [DONE] sent when all sources complete")

    uvicorn.run(app, host="0.0.0.0", port=8012)
