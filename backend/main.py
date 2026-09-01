from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import buildings, rooms, energy

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

@app.get("/")
def root():
    return {"status": "CampusTwin AI backend running"}