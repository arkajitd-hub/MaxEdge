from datetime import date
from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from .database import Base

athlete_sponsor = Table(
    "athlete_sponsor",
    Base.metadata,
    Column("athlete_id", ForeignKey("athletes.id"), primary_key=True),
    Column("sponsor_id", ForeignKey("sponsors.id"), primary_key=True),
)


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    region = Column(String, nullable=False)

    athletes = relationship("Athlete", back_populates="agent")


class Market(Base):
    __tablename__ = "markets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    growth_score = Column(Float, nullable=False)

    sponsors = relationship("Sponsor", back_populates="market")


class Sponsor(Base):
    __tablename__ = "sponsors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    sector = Column(String, nullable=False)
    budget_musd = Column(Float, nullable=False)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=False)

    market = relationship("Market", back_populates="sponsors")
    athletes = relationship("Athlete", secondary=athlete_sponsor, back_populates="sponsors")


class Athlete(Base):
    __tablename__ = "athletes"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    sport = Column(String, nullable=False, index=True)
    country = Column(String, nullable=False)
    ranking = Column(Integer, nullable=False)
    social_followers_m = Column(Float, nullable=False)
    annual_salary_musd = Column(Float, nullable=False)
    performance_score = Column(Float, nullable=False)
    contract_end = Column(Date, nullable=False, default=date.today)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)

    agent = relationship("Agent", back_populates="athletes")
    sponsors = relationship("Sponsor", secondary=athlete_sponsor, back_populates="athletes")
