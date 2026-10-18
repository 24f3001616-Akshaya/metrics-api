
import time
import uuid

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware


api = FastAPI()

# Allow only the origin assigned in your question.
api.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dash-0afntn.example.com"
    ],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@api.get("/stats")
def get_stats(values: str = Query(...)):
    # Convert "10,20,30" into [10, 20, 30].
    numbers = [int(value.strip()) for value in values.split(",")]

    # Reject an empty list.
    if not numbers:
        return {"error": "At least one integer is required"}

    return {
        "email": "YOUR_ACTUAL_REGISTERED_EMAIL",
        "count": len(numbers),
        "sum": sum(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "mean": sum(numbers) / len(numbers),
    }


# Add headers to successful responses and error responses,
# including CORS preflight responses.
class RequestHeadersMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.perf_counter()
        request_id = str(uuid.uuid4())

        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                elapsed = time.perf_counter() - start_time

                headers = list(message.get("headers", []))
                headers.extend([
                    (b"x-request-id", request_id.encode("ascii")),
                    (
                        b"x-process-time",
                        f"{elapsed:.6f}".encode("ascii"),
                    ),
                ])

                message["headers"] = headers

            await send(message)

        await self.app(scope, receive, send_with_headers)


# This outer middleware also adds headers to CORS preflight responses.
app = RequestHeadersMiddleware(api)
