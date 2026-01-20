"""Exercise 1: Implement Basic Dual-Mode Endpoint.

In this exercise, you'll create an endpoint that returns weather data
in either streaming or batch mode based on a query parameter.

Requirements:
1. Create a FastAPI endpoint at GET /weather
2. Accept a 'stream' query parameter (default False)
3. In batch mode: return all forecasts as JSON
4. In stream mode: yield forecasts as SSE events
5. Include a 0.5 second delay between streamed items

The weather data should be generated using the provided function.

Run your solution with:
    uvicorn exercises.exercise_1_dual_mode:app --reload

Test with:
    curl "localhost:8000/weather"              # Batch mode
    curl "localhost:8000/weather?stream=true"  # Stream mode
"""

import asyncio
from typing import AsyncGenerator

from fastapi import FastAPI

app = FastAPI(title="Exercise 1: Dual-Mode Weather API")


async def get_forecasts() -> AsyncGenerator[dict, None]:
    """Generate weather forecast data.

    This function simulates fetching weather forecasts.
    Each call yields a forecast for a different day.

    Yields:
        Dictionary with day and forecast information.
    """
    forecasts = [
        {"day": "Monday", "temp": 72, "condition": "Sunny"},
        {"day": "Tuesday", "temp": 68, "condition": "Cloudy"},
        {"day": "Wednesday", "temp": 65, "condition": "Rainy"},
        {"day": "Thursday", "temp": 70, "condition": "Partly Cloudy"},
        {"day": "Friday", "temp": 75, "condition": "Sunny"},
    ]

    for forecast in forecasts:
        yield forecast


# TODO: Implement the /weather endpoint
#
# Hints:
# - Use FastAPI's Query() to define the stream parameter
# - For streaming, use StreamingResponse with media_type="text/event-stream"
# - Format SSE data as: f"data: {json.dumps(data)}\n\n"
# - Use asyncio.sleep(0.5) between streamed items
# - For batch mode, collect all items and return as JSONResponse

@app.get("/weather")
async def get_weather():
    """Weather endpoint - implement dual-mode response."""
    # Your implementation here
    raise NotImplementedError("Implement this endpoint")


# Bonus: Add a /weather/negotiate endpoint that uses Accept header detection
# instead of query parameter


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
