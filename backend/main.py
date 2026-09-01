from fastapi import FastAPI
from routers import buildings, rooms, energy

app = FastAPI(title="CampusTwin AI API")

app.include_router(buildings.router)
app.include_router(rooms.router)
app.include_router(energy.router)

@app.get("/")
def root():
    return {"status": "CampusTwin AI backend running"}