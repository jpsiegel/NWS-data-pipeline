# main.py
from .utils.logging import get_logger
import logging
from fastapi import FastAPI

# Replace default uvicorn logger
logging.getLogger("uvicorn.access").handlers.clear()

app = FastAPI()

logger = get_logger()

@app.get("/")
def root():
    logger.info("Health check successful")
    return {"message": "Running"}
