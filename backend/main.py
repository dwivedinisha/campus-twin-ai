import sys, os, asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import buildings, rooms, energy, twin

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "digital_twin"))
from engine import run_engine

app = FastAPI(title="CampusTwin AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(buildings.router)
app.include_router(rooms.router)
app.include_router(energy.router)
app.include_router(twin.router)

@app.on_event("startup")
async def start_engine():
    asyncio.create_task(run_engine())

@app.get("/")
def root():
    return {"status": "CampusTwin AI backend running"}