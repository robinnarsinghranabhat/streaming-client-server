## Build a async llm-like server
## It should be able to serve Multiple clients simultaneously

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio
import itertools

app = FastAPI()

@app.get("/stream_updates")
async def stream_updates(request: Request):
    async def event_generator():
        # Simulate a real-time stream of data
        # for i, c in enumerate(itertools.cycle('|/-')):
        for i, c in enumerate([1,2,3]):
            yield f"data: {c} i loke to move it move it {i}"
            await asyncio.sleep(1) # artificial delay
    return StreamingResponse(event_generator(), media_type="text/event-stream")


# Simulate a long-running I/O-bound task
async def fake_db_query():
    await asyncio.sleep(1)  # Simulate a delay (e.g., database query)
    return {"message": "Data fetched from the database"}

@app.get("/data")
async def get_data():
    data = await fake_db_query()  # Wait for the fake DB query to finish
    return data


    