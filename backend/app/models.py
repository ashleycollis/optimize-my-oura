from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import Date, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class DailySleep(Base):
    __tablename__ = "daily_sleep"
    __table_args__ = (UniqueConstraint("day", name="uq_daily_sleep_day"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    day: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_sleep_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    efficiency: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class DailyReadiness(Base):
    __tablename__ = "daily_readiness"
    __table_args__ = (UniqueConstraint("day", name="uq_daily_readiness_day"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    day: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


class DailyActivity(Base):
    __tablename__ = "daily_activity"
    __table_args__ = (UniqueConstraint("day", name="uq_daily_activity_day"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    day: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    steps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    calories_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


