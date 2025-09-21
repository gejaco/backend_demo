# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI()

# Allow all origins (for testing); in production, specify your real front-end domains.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # Replace ["*"] with a list of your front-end URLs for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    current_time = int(time.time())
    return {
        "message": f"Hello, world! This is my Render back-end. Added CORS middleware. Current time: {current_time} seconds."
    }    
