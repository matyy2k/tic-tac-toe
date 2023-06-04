import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Column, DateTime, Integer, String

from db import Base


class UserStats(Base):
    __tablename__ = "statistics"

    id = Column(Integer, primary_key=True)
    created_at = Column(
        DateTime, default=datetime.datetime.now(tz=ZoneInfo(key="Europe/Warsaw"))
    )
    user_name = Column(String)
    wins = Column(Integer)
    losses = Column(Integer)
    draws = Column(Integer)
    user_id = Column(String)
    start_game = Column(DateTime)
    end_game = Column(DateTime)
