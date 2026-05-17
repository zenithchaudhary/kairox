from fastapi import FastAPI

app = FastAPI(
    title="KAIROX",
    description="AI-powered financial news intelligence platform",
    version="0.1.0"
)

@app.get("/")
def root():
    return{
        "service": "KAIROX API",
        "version": "0.1.0",
        "status" : "online"
    }

@app.get("/health")
def health():
    return{
        "status" : "healthy"
    }
