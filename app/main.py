# main.py
from .utils.logging import get_logger
from app.routes import router
from fastapi import FastAPI
import logging

# Replace default uvicorn logger
logging.getLogger("uvicorn.access").handlers.clear()

# Create app
app = FastAPI()

# Set logger
logger = get_logger()

# Register all routes
app.include_router(router)

@app.get("/")
def root():
    logger.info("Health check successful")
    return {"message": "Running"}
