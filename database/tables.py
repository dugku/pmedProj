from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, BigInteger, Float,
    String, DateTime, Enum, ForeignKey, CHAR, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class Match(Base):
    __tablename__ = "matches"
    match_id = Column(Integer, primary_key=True, autoincrement=True)
    date     = Column(DateTime, default=datetime.utcnow, nullable=False)
    map_name = Column(String, nullable=True)
    rounds = relationship("Round", back_populates="match")


class Round(Base):
    __tablename__ = "rounds"
    round_id     = Column(Integer, primary_key=True, autoincrement=True)
    match_id     = Column(Integer, ForeignKey("matches.match_id"), nullable=False)
    round_number = Column(Integer, nullable=False)

    match = relationship("Match", back_populates="rounds")
    econ_snapshots = relationship("EconSnapshot", back_populates="round")
    kills          = relationship("KillEvent", back_populates="round")
    events         = relationship("Event", back_populates="round")


class Player(Base):
    __tablename__ = "players"
    steamid = Column(Integer, primary_key=True)
    name    = Column(String, nullable=True)


class EconSnapshot(Base):
    __tablename__ = "econ_snapshots"
    snsnapshot_id = Column(Integer, primary_key=True, autoincrement=True)
    round_id         = Column(Integer, ForeignKey("rounds.round_id"), nullable=False)
    event_type       = Column(
        Enum("freeze_start", "freeze_end", name="econ_event_type"),
        nullable=False
    )
    steamid          = Column(BigInteger, ForeignKey("players.steamid"), nullable=False)
    side             = Column(CHAR(2), CheckConstraint("side IN ('t','ct')"), nullable=False)
    total_cash_spent = Column(Integer)
    cash_this_round  = Column(Integer)
    balance          = Column(Integer)
    ct_losing_streak = Column(Integer)
    t_losing_streak  = Column(Integer)
    equip_value      = Column(Float )

    round  = relationship("Round",   back_populates="econ_snapshots")
    player = relationship("Player")


class KillEvent(Base):
    __tablename__ = "kill_events"
    kill_id      = Column(Integer, primary_key=True, autoincrement=True)
    round_id     = Column(Integer,    ForeignKey("rounds.round_id"), nullable=False)
    attacker_id  = Column(BigInteger, ForeignKey("players.steamid"), nullable=False)
    victim_id    = Column(BigInteger, ForeignKey("players.steamid"), nullable=False)
    attacker_side= Column(CHAR(2),    CheckConstraint("attacker_side IN ('t','ct')"), nullable=False)
    attacker_x   = Column(Float,      nullable=False)
    attacker_y   = Column(Float,      nullable=False)
    victim_x     = Column(Float,      nullable=False)
    victim_y     = Column(Float,      nullable=False)
    victim_side  = Column(CHAR(2),    CheckConstraint("victim_side IN ('t','ct')"), nullable=False)

    round    = relationship("Round",  back_populates="kills")
    attacker = relationship("Player", foreign_keys=[attacker_id])
    victim   = relationship("Player", foreign_keys=[victim_id])


class Event(Base):
    __tablename__ = "events"
    event_id   = Column(Integer, primary_key=True, autoincrement=True)
    round_id   = Column(Integer,    ForeignKey("rounds.round_id"), nullable=False)
    steamid    = Column(BigInteger, ForeignKey("players.steamid"), nullable=False)
    event_type = Column(
        Enum("smoke","inferno","he","flash","pl_h","pl_fired", name="event_type"),
        nullable=False
    )
    x          = Column(Float,      nullable=False)
    y          = Column(Float,      nullable=False)

    round  = relationship("Round",  back_populates="events")
    player = relationship("Player")


def create_database(engine_url):
    engine = create_engine(engine_url)
    Base.metadata.create_all(engine)
    return engine

def get_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    return session