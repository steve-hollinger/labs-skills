"""
Solution 3: Multi-Source Stream Aggregation

Complete implementation of multi-source stream aggregation.
"""

import json
import asyncio
import random
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI(title="Multi-Source Streaming Solution")


async def news_source():
    """Generate mock news updates."""
    headlines = [
        ("Tech", "New AI Breakthrough Announced"),
        ("Sports", "Championship Game Results"),
        ("Business", "Market Hits Record High"),
        ("Science", "Mars Mission Update"),
        ("Entertainment", "Award Show Highlights"),
    ]

    for category, title in headlines:
        yield {
            "source": "news",
            "category": category,
            "title": title,
            "timestamp": datetime.now().isoformat()
        }
        await asyncio.sleep(random.uniform(1, 3))


async def weather_source():
    """Generate mock weather updates."""
    locations = [
        ("New York", 72, "Sunny"),
        ("London", 58, "Cloudy"),
        ("Tokyo", 68, "Clear"),
    ]

    for location, temp, condition in locations:
        yield {
            "source": "weather",
            "location": location,
            "temperature": temp,
            "condition": condition,
            "unit": "F",
            "timestamp": datetime.now().isoformat()
        }
        await asyncio.sleep(random.uniform(2, 4))


async def stocks_source():
    """Generate mock stock updates with possible failure."""
    symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "META",
               "TSLA", "NVDA", "JPM", "V", "JNJ"]

    for i, symbol in enumerate(symbols):
        # 20% chance of failure for testing
        if random.random() < 0.2:
            raise Exception(f"Stock feed error at {symbol}")

        price = random.uniform(100, 500)
        change = random.uniform(-5, 5)

        yield {
            "source": "stocks",
            "symbol": symbol,
            "price": round(price, 2),
            "change": round(change, 2),
            "change_percent": round(change / price * 100, 2),
            "timestamp": datetime.now().isoformat()
        }
        await asyncio.sleep(random.uniform(0.5, 1))


async def aggregate_sources(*sources):
    """Aggregate multiple async sources into one stream."""
    queue = asyncio.Queue()
    active_sources = len(sources)
    source_errors = []

    async def source_worker(source_func, source_name):
        """Worker that consumes a source and puts items in queue."""
        nonlocal active_sources
        try:
            async for item in source_func():
                await queue.put(("data", item))
        except Exception as e:
            error = {
                "source": source_name,
                "error": str(e),
                "type": "source_error"
            }
            await queue.put(("error", error))
            source_errors.append(source_name)
        finally:
            await queue.put(("done", source_name))

    # Start all source workers
    source_names = ["news", "weather", "stocks"]
    tasks = []
    for i, source_func in enumerate(sources):
        name = source_names[i] if i < len(source_names) else f"source_{i}"
        task = asyncio.create_task(source_worker(source_func, name))
        tasks.append(task)

    completed_sources = 0

    # Process queue until all sources complete
    while completed_sources < len(sources):
        try:
            event_type, data = await asyncio.wait_for(queue.get(), timeout=30)

            if event_type == "data":
                yield f"data: {json.dumps(data)}\n\n"

            elif event_type == "error":
                yield f"event: source_error\ndata: {json.dumps(data)}\n\n"

            elif event_type == "done":
                completed_sources += 1
                status = {
                    "type": "source_complete",
                    "source": data,
                    "remaining": len(sources) - completed_sources
                }
                yield f"event: status\ndata: {json.dumps(status)}\n\n"

        except asyncio.TimeoutError:
            yield ": keepalive\n\n"

    # Final summary
    summary = {
        "type": "complete",
        "total_sources": len(sources),
        "errors": source_errors
    }
    yield f"event: complete\ndata: {json.dumps(summary)}\n\n"
    yield "data: [DONE]\n\n"

    # Clean up tasks
    for task in tasks:
        if not task.done():
            task.cancel()


@app.get("/stream/all")
async def aggregated_stream():
    """Stream aggregated data from all sources."""
    return StreamingResponse(
        aggregate_sources(news_source, weather_source, stocks_source),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


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
        "solution": "Multi-Source Aggregation",
        "endpoints": {
            "/stream/all": "Aggregated stream from all sources",
            "/stream/news": "News only",
            "/stream/weather": "Weather only",
            "/stream/stocks": "Stocks only (may fail)"
        }
    }


if __name__ == "__main__":
    import uvicorn
    print("Solution 3: Multi-Source Stream Aggregation")
    print("=" * 50)
    print('Test: curl -N "http://localhost:8012/stream/all"')
    uvicorn.run(app, host="0.0.0.0", port=8012)
