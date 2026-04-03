from datetime import date
from typing import List
from pydantic import BaseModel


class SponsorOut(BaseModel):
    id: int
    name: str
    sector: str
    budget_musd: float

    model_config = {"from_attributes": True}


class AthleteOut(BaseModel):
    id: int
    full_name: str
    sport: str
    country: str
    ranking: int
    social_followers_m: float
    annual_salary_musd: float
    performance_score: float
    contract_end: date
    agent_name: str
    sponsors: List[SponsorOut]


class AnalyticsOverview(BaseModel):
    total_athletes: int
    total_agents: int
    total_sponsors: int
    avg_performance_score: float
    sport_mix: dict
    top_athletes: List[str]


class ChatQuery(BaseModel):
    question: str
    use_llm: bool = True


class ChatResponse(BaseModel):
    answer: str
