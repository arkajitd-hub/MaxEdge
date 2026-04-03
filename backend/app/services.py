from collections import Counter
from typing import Optional

from openai import OpenAI
from sqlalchemy import func
from sqlalchemy.orm import Session

from .config import OPENAI_API_KEY, OPENAI_MODEL
from .models import Athlete, Sponsor


def analytics_overview(db: Session) -> dict:
    athletes = db.query(Athlete).all()
    total_athletes = len(athletes)
    total_agents = db.query(func.count(func.distinct(Athlete.agent_id))).scalar() or 0
    total_sponsors = db.query(Sponsor).count()
    avg_performance_score = round(
        sum(a.performance_score for a in athletes) / total_athletes if total_athletes else 0, 2
    )
    sport_mix = dict(Counter(a.sport for a in athletes))
    top_athletes = [
        a.full_name
        for a in sorted(
            athletes,
            key=lambda x: (x.performance_score, x.social_followers_m),
            reverse=True,
        )[:5]
    ]
    return {
        "total_athletes": total_athletes,
        "total_agents": total_agents,
        "total_sponsors": total_sponsors,
        "avg_performance_score": avg_performance_score,
        "sport_mix": sport_mix,
        "top_athletes": top_athletes,
    }


def sponsor_fit_suggestions(db: Session, athlete_id: int) -> list[dict]:
    athlete = db.query(Athlete).filter(Athlete.id == athlete_id).first()
    if not athlete:
        return []

    current_sponsor_ids = {s.id for s in athlete.sponsors}
    candidate_sponsors = db.query(Sponsor).all()

    suggestions = []
    for sponsor in candidate_sponsors:
        if sponsor.id in current_sponsor_ids:
            continue
        fit_score = 0.45 * athlete.performance_score + 0.35 * athlete.social_followers_m + 0.2 * sponsor.market.growth_score
        fit_score = round(fit_score, 2)
        suggestions.append(
            {
                "sponsor": sponsor.name,
                "sector": sponsor.sector,
                "market": sponsor.market.name,
                "fit_score": fit_score,
            }
        )

    suggestions.sort(key=lambda x: x["fit_score"], reverse=True)
    return suggestions[:5]


def ask_llm(question: str, context: str) -> Optional[str]:
    if not OPENAI_API_KEY:
        return None

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {
                "role": "system",
                "content": "You are Max AI, an internal strategy assistant for a sports agency. Keep responses concise and actionable.",
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}",
            },
        ],
    )
    return response.output_text
