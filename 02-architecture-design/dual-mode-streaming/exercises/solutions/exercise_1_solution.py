"""Exercise 1 Solution: Dual-Mode Weather Endpoint.

This solution demonstrates implementing a dual-mode endpoint that
returns weather forecasts in either streaming or batch mode.
"""

import asyncio
import json
from typing import AsyncGenerator

from fastapi import Depends, FastAPI, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse

from dual_mode_streaming.modes import ResponseMode, detect_response_mode

app = FastAPI(title="Exercise 1 Solution: Dual-Mode Weather API")


async def get_forecasts() -> AsyncGenerator[dict, None]:
    """Generate weather forecast data."""
    forecasts = [
        {"day": "Monday", "temp": 72, "condition": "Sunny"},
        {"day": "Tuesday", "temp": 68, "condition": "Cloudy"},
        {"day": "Wednesday", "temp": 65, "condition": "Rainy"},
        {"day": "Thursday", "temp": 70, "condition": "Partly Cloudy"},
        {"day": "Friday", "temp": 75, "condition": "Sunny"},
    ]

    for forecast in forecasts:
        yield forecast


# Solution: Query parameter-based mode switching
@app.get("/weather")
async def get_weather(stream: bool = Query(default=False)):
    """Weather endpoint with dual-mode response.

    Args:
        stream: If True, return streaming response; otherwise batch.

    Returns:
        Weather forecasts in selected mode.
    """
    if stream:
        # Streaming mode
        async def stream_forecasts() -> AsyncGenerator[str, None]:
            async for forecast in get_forecasts():
                # Format as SSE event
                yield f"data: {json.dumps(forecast)}\n\n"
                # Add delay between items
                await asyncio.sleep(0.5)

        return StreamingResponse(
            stream_forecasts(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"},
        )

    # Batch mode - collect all forecasts
    forecasts = [f async for f in get_forecasts()]
    return JSONResponse({
        "forecasts": forecasts,
        "count": len(forecasts),
        "mode": "batch",
    })


# Bonus: Accept header detection
@app.get("/weather/negotiate")
async def get_weather_negotiate(request: Request):
    """Weather endpoint using Accept header for mode detection.

    Args:
        request: The incoming request for header inspection.

    Returns:
        Weather forecasts in detected mode.
    """
    mode = detect_response_mode(request)

    if mode == ResponseMode.STREAM:
        async def stream_forecasts() -> AsyncGenerator[str, None]:
            async for forecast in get_forecasts():
                yield f"data: {json.dumps(forecast)}\n\n"
                await asyncio.sleep(0.5)

        return StreamingResponse(
            stream_forecasts(),
            media_type="text/event-stream",
        )

    forecasts = [f async for f in get_forecasts()]
    return JSONResponse({
        "forecasts": forecasts,
        "count": len(forecasts),
        "mode": "batch",
    })


# Additional enhancement: Combined negotiation
def negotiate_weather_mode(
    request: Request,
    stream: bool | None = Query(default=None),
) -> ResponseMode:
    """Negotiate response mode with param override.

    Args:
        request: Incoming request.
        stream: Optional explicit stream override.

    Returns:
        Negotiated response mode.
    """
    if stream is not None:
        return ResponseMode.STREAM if stream else ResponseMode.BATCH
    return detect_response_mode(request)


@app.get("/weather/advanced")
async def get_weather_advanced(
    mode: ResponseMode = Depends(negotiate_weather_mode),
):
    """Weather endpoint with full mode negotiation.

    Priority: query param > Accept header > default (batch)

    Args:
        mode: Negotiated response mode.

    Returns:
        Weather forecasts in negotiated mode.
    """
    if mode == ResponseMode.STREAM:
        async def stream_forecasts() -> AsyncGenerator[str, None]:
            # Send start event
            yield f"event: start\ndata: {json.dumps({'message': 'Starting forecast stream'})}\n\n"

            async for forecast in get_forecasts():
                yield f"event: forecast\ndata: {json.dumps(forecast)}\n\n"
                await asyncio.sleep(0.5)

            # Send complete event
            yield f"event: complete\ndata: {json.dumps({'message': 'All forecasts sent'})}\n\n"

        return StreamingResponse(
            stream_forecasts(),
            media_type="text/event-stream",
        )

    forecasts = [f async for f in get_forecasts()]
    return JSONResponse({
        "forecasts": forecasts,
        "count": len(forecasts),
        "mode": mode.value,
    })


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
