from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Float, JSON, Boolean, column, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

EventsBase = declarative_base()

class Event(EventsBase):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    event_name = Column(String, unique=True, nullable=False)
    location = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    prize = Column(String, nullable=True)
    link = Column(String, nullable=False)
    event_id = Column(String, unique=True, index=True, nullable=False)