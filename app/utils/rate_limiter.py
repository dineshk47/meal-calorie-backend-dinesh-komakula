import time
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import os
from dotenv import load_dotenv

load_dotenv()
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "15"))
RATE_LIMIT_PERIOD_SECONDS = int(os.getenv("RATE_LIMIT_PERIOD_SECONDS", "60"))

class SimpleRateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.store = {}  # ip -> [timestamps]

    async def dispatch(self, request, call_next):
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = RATE_LIMIT_PERIOD_SECONDS
        allowed = RATE_LIMIT_REQUESTS

        timestamps = self.store.get(ip, [])
        # drop expired
        timestamps = [t for t in timestamps if now - t < window]
        if len(timestamps) >= allowed:
            return JSONResponse({"detail": "Too many requests, slow down."}, status_code=429)
        timestamps.append(now)
        self.store[ip] = timestamps
        response = await call_next(request)
        return response
