from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, HttpUrl, Field
from sqlalchemy.ext.declarative import declarative_base

EventsBase = declarative_base()

class EventsSchema(BaseModel):
    event_name: str
    location: Optional[str] = None
    date: str
    prize: Optional[str] = None
    link: HttpUrl
    id: str

class LinksSchema(BaseModel):
    demo_url: str