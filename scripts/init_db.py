import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import random
from datetime import date, timedelta

from backend.app.database import Base, SessionLocal, engine
from backend.app.models import Agent, Athlete, Market, Sponsor

random.seed(42)

SPORTS = ["football", "tennis", "f1", "indy", "basketball"]
COUNTRIES = ["USA", "UK", "Spain", "France", "Italy", "Brazil", "Germany", "Australia", "Japan", "Canada"]
SECTORS = ["Apparel", "Automotive", "Tech", "Fintech", "Energy", "Telecom", "Beverage", "Luxury", "Travel", "Health"]
MARKETS = [
    "North America",
    "Western Europe",
    "Middle East",
    "South America",
    "Southeast Asia",
    "India",
    "Japan",
    "Australia",
    "Africa",
    "Nordics",
]
FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Cameron", "Parker", "Reese", "Jesse", "Quinn"
]
LAST_NAMES = [
    "Carter", "Lopez", "Miller", "Singh", "Silva", "Khan", "Moreau", "Rossi", "Nakamura", "Brown", "Clark", "Davis"
]


def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        agents = []
        for i in range(1, 19):
            agent = Agent(name=f"Agent {i:02}", region=random.choice(["US", "EU", "LATAM", "APAC", "MENA"]))
            db.add(agent)
            agents.append(agent)
        db.flush()

        markets = []
        for m in MARKETS:
            market = Market(name=m, growth_score=round(random.uniform(6.0, 10.0), 2))
            db.add(market)
            markets.append(market)
        db.flush()

        sponsors = []
        for i in range(1, 41):
            sponsor = Sponsor(
                name=f"Sponsor {i:02}",
                sector=random.choice(SECTORS),
                budget_musd=round(random.uniform(3.0, 75.0), 2),
                market_id=random.choice(markets).id,
            )
            db.add(sponsor)
            sponsors.append(sponsor)
        db.flush()

        for i in range(1, 121):
            sport = SPORTS[(i - 1) % len(SPORTS)]
            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)} {i:03}"
            athlete = Athlete(
                full_name=name,
                sport=sport,
                country=random.choice(COUNTRIES),
                ranking=random.randint(1, 250),
                social_followers_m=round(random.uniform(0.2, 65.0), 2),
                annual_salary_musd=round(random.uniform(0.4, 85.0), 2),
                performance_score=round(random.uniform(60.0, 99.8), 2),
                contract_end=date.today() + timedelta(days=random.randint(200, 1800)),
                agent_id=random.choice(agents).id,
            )
            athlete.sponsors = random.sample(sponsors, random.randint(1, 4))
            db.add(athlete)

        db.commit()
        print("Database initialized with 120 athletes, 18 agents, 40 sponsors, and 10 markets.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
