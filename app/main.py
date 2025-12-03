from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import auth, tests, listening, reading, speaking, writing, upload

# Create tables with new schema
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

app.include_router(auth.router)
app.include_router(tests.router)
app.include_router(listening.router)
app.include_router(reading.router)
app.include_router(speaking.router)
app.include_router(writing.router)
app.include_router(upload.router)

@app.get("/")
def root():
    return {"message": "IELTS App API is running!"}