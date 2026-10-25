
from fastapi import FastAPI

app = FastAPI(
    title="Scholarly Insight API",
    description="Backend for scholarly article search",
    version="0.1.0"
)

@app.get("/")
def home():
    return {"message": "Welcome to Scholarly Insight"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
