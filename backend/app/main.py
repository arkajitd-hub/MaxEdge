from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Athlete
from .schemas import AnalyticsOverview, AthleteOut, ChatQuery, ChatResponse, SponsorOut
from .services import analytics_overview, ask_llm, sponsor_fit_suggestions

app = FastAPI(title="Max AI API", version="0.1.0")

Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "max-ai-api"}


@app.get("/athletes", response_model=list[AthleteOut])
def list_athletes(sport: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Athlete)
    if sport:
        query = query.filter(Athlete.sport.ilike(sport))
    athletes = query.order_by(Athlete.performance_score.desc()).all()

    return [
        AthleteOut(
            id=a.id,
            full_name=a.full_name,
            sport=a.sport,
            country=a.country,
            ranking=a.ranking,
            social_followers_m=a.social_followers_m,
            annual_salary_musd=a.annual_salary_musd,
            performance_score=a.performance_score,
            contract_end=a.contract_end,
            agent_name=a.agent.name,
            sponsors=[SponsorOut.model_validate(s) for s in a.sponsors],
        )
        for a in athletes
    ]


@app.get("/athletes/{athlete_id}", response_model=AthleteOut)
def get_athlete(athlete_id: int, db: Session = Depends(get_db)):
    athlete = db.query(Athlete).filter(Athlete.id == athlete_id).first()
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")

    return AthleteOut(
        id=athlete.id,
        full_name=athlete.full_name,
        sport=athlete.sport,
        country=athlete.country,
        ranking=athlete.ranking,
        social_followers_m=athlete.social_followers_m,
        annual_salary_musd=athlete.annual_salary_musd,
        performance_score=athlete.performance_score,
        contract_end=athlete.contract_end,
        agent_name=athlete.agent.name,
        sponsors=[SponsorOut.model_validate(s) for s in athlete.sponsors],
    )


@app.get("/analytics/overview", response_model=AnalyticsOverview)
def get_analytics(db: Session = Depends(get_db)):
    return analytics_overview(db)


@app.get("/suggestions/sponsor-fit")
def get_sponsor_fit(athlete_id: int, db: Session = Depends(get_db)):
    suggestions = sponsor_fit_suggestions(db, athlete_id)
    if not suggestions:
        raise HTTPException(status_code=404, detail="Athlete not found or no suggestions")
    return {"athlete_id": athlete_id, "recommendations": suggestions}


@app.post("/chat/query", response_model=ChatResponse)
def chat_query(payload: ChatQuery, db: Session = Depends(get_db)):
    context_data = analytics_overview(db)
    context = (
        f"Agency total athletes: {context_data['total_athletes']}\n"
        f"Sport mix: {context_data['sport_mix']}\n"
        f"Top athletes: {', '.join(context_data['top_athletes'])}"
    )

    if payload.use_llm:
        llm_answer = ask_llm(payload.question, context)
        if llm_answer:
            return ChatResponse(answer=llm_answer)

    fallback = (
        "Max AI local mode: I can answer with current agency analytics. "
        f"You asked: '{payload.question}'. Based on current data, prioritize sponsor outreach around top performers and high-growth markets."
    )
    return ChatResponse(answer=fallback)
