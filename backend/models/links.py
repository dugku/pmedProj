from datetime import datetime

from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Float, JSON, Boolean, column, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

LinksBase = declarative_base()

class Links(LinksBase):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True)
    demo_url = Column(String, unique=True, nullable=False)
    match_id = Column(String, unique=True, nullable=False)
    parsed = Column(Boolean, default=False)
    file_path = Column(String)
    added_at = Column(DateTime, server_default=func.now())
    parsed_at = Column(DateTime, onupdate=func.now())
