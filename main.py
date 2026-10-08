from fastapi import FastAPI

from auth import router as auth_router
from venues import router as venues_router
from events import router as events_router

app = FastAPI(title="Компаньон API")

app.include_router(auth_router)
app.include_router(venues_router)
app.include_router(events_router)


@app.get("/")
def read_root():
    return {"message": "Привет от Компаньона!"}


@app.get("/health")
def health():
    return {"status": "ok"}

