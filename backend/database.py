from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


EVENTS_DB_URL = "sqlite:///./events.db"
LINKS_DB_URL = "sqlite:///./links.db"

events_engine = create_engine(EVENTS_DB_URL, connect_args={"check_same_thread": False})
links_engine = create_engine(LINKS_DB_URL, connect_args={"check_same_thread": False})

EventsSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=events_engine)
LinksSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=links_engine)

def get_events_db():
    db = EventsSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_links_db():
    db = LinksSessionLocal()
    try:
        yield db
    finally:
        db.close()