from fastapi import FastAPI
from fastapi.params import Depends
from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi import APIRouter

from database import events_engine, links_engine
from models.events import EventsBase
from models.links import LinksBase

import routes.events
import routes.links

EventsBase.metadata.create_all(bind=events_engine)
LinksBase.metadata.create_all(bind=links_engine)


app = FastAPI()


app.include_router(
    routes.events.router,
    prefix="/events",
    tags=["events"]
)

app.include_router(
    routes.links.router,
    prefix="/links",
    tags=["links"]
)


@app.get("/")
async def root():
    return {"message": "Hello World"}