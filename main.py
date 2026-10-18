
import time
import uuid

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

app = FastAPI()

ALLOWED_ORIGIN = "https://dash-0afntn.example.com"
EMAIL = "YOUR_ACTUAL_REGISTERED_EMAIL"


@app.middleware("http")
async def add_required_headers(request: Request, call_next):
    start = time.perf_counter()
    request_id = str(uuid.uuid4())

    try:
        response = await call_next(request)
    except Exception:
        response = Response("Internal Server Error", status_code=500)

    elapsed = time.perf_counter() - start
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{elapsed:.6f}"
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/stats")
def stats(values: str = Query(...)):
    try:
        numbers = [int(x.strip()) for x in values.split(",")]
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail="Values must be comma-separated integers")

    if not numbers:
        raise HTTPException(status_code=400, detail="At least one integer is required")

    return {
        "email": EMAIL,
        "count": len(numbers),
        "sum": sum(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "mean": sum(numbers) / len(numbers),
    }
