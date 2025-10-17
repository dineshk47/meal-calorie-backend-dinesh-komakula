import logging
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.exceptions import (
    exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from api import api_router
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
app = FastAPI(
    title="Xcelpros - Meal Calorie Count Generator",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


log_level = "DEBUG"

logger = logging.getLogger()
logger.setLevel(log_level)

formatter = logging.Formatter(
    "%(asctime)s - %(threadName)s %(filename)s:%(lineno)d - %(funcName)s() - %(levelname)s - %(message)s"
)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# Limiter setup: limit per IP
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Handle rate-limit exception
@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"status": "GE42901", "error": "Too many requests. Please try again later."}
    )

app.include_router(api_router)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, exception_handler)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log incoming requests and response times."""
    start_time = time.time()
    logger.info(f"Incoming request: {request.method} {request.url}")
    
    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    formatted_time = f"{process_time:.2f} ms"
    logger.info(f"Completed {request.method} {request.url} in {formatted_time}")
    return response
