from collections import Counter
from typing import Optional

import requests
from sqlalchemy import func
from sqlalchemy.orm import Session

from .config import GEMINI_API_KEY, GEMINI_MODEL
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
    if not GEMINI_API_KEY:
        return None

    prompt = (
        "You are Max AI, an internal strategy assistant for a sports agency. "
        "Keep responses concise and actionable.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}"
    )
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(url, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return None
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            return None
        return parts[0].get("text")
    except (requests.RequestException, ValueError, KeyError, IndexError):
        return None
