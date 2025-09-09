from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import Base, engine
from router import reading, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="IELTS App API",
    description="API for IELTS Reading, Writing, Listening, and Speaking practice",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(reading.router, prefix="/api/reading", tags=["Reading"])

@app.get("/")
def root():
    return {"message": "IELTS App API is running!"}