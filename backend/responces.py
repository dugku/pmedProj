from typing import List, Optional, Dict
from pydantic import BaseModel, HttpUrl

class EventsResponse(BaseModel):
    link: str

class LinksResponse(BaseModel):
    match_id: str
    demo_url: str
