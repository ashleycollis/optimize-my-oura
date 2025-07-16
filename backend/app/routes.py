from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from .config import get_settings
from .oura_client import OuraClient
from .db import get_db
from sqlalchemy.orm import Session
from .models import DailySleep, DailyReadiness, DailyActivity


router = APIRouter(prefix="/api", tags=["oura"])


def get_access_token() -> str:
    settings = get_settings()
    if not settings.oura_personal_access_token:
        raise HTTPException(status_code=500, detail="Oura token not configured")
    return settings.oura_personal_access_token


@router.get("/sleep/daily")
def get_sleep_daily(
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(DailySleep)
    if start_date:
        query = query.filter(DailySleep.day >= date.fromisoformat(start_date))
    if end_date:
        query = query.filter(DailySleep.day <= date.fromisoformat(end_date))
    items = query.order_by(DailySleep.day.asc()).all()
    return {"data": [
        {
            "day": i.day.isoformat(),
            "score": i.score,
            "total_sleep_duration": i.total_sleep_duration_minutes,
            "efficiency": i.efficiency,
        }
        for i in items
    ]}


@router.get("/activity/daily")
def get_activity_daily(
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(DailyActivity)
    if start_date:
        query = query.filter(DailyActivity.day >= date.fromisoformat(start_date))
    if end_date:
        query = query.filter(DailyActivity.day <= date.fromisoformat(end_date))
    items = query.order_by(DailyActivity.day.asc()).all()
    return {"data": [
        {
            "day": i.day.isoformat(),
            "score": i.score,
            "steps": i.steps,
            "cal_total": i.calories_total,
        }
        for i in items
    ]}


@router.get("/readiness/daily")
def get_readiness_daily(
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(DailyReadiness)
    if start_date:
        query = query.filter(DailyReadiness.day >= date.fromisoformat(start_date))
    if end_date:
        query = query.filter(DailyReadiness.day <= date.fromisoformat(end_date))
    items = query.order_by(DailyReadiness.day.asc()).all()
    return {"data": [
        {
            "day": i.day.isoformat(),
            "score": i.score,
        }
        for i in items
    ]}


@router.post("/sync")
async def sync_daily_data(
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    access_token: str = Depends(get_access_token),
    db: Session = Depends(get_db),
):
    client = OuraClient(access_token)
    try:
        # Sleep
        sleep_json = await client.daily_sleep(start_date=start_date, end_date=end_date)
        for item in sleep_json.get("data", []):
            day_str = item.get("day")
            if not day_str:
                continue
            day = date.fromisoformat(day_str)
            existing = db.query(DailySleep).filter(DailySleep.day == day).one_or_none()
            if existing is None:
                existing = DailySleep(day=day)
            existing.score = item.get("score")
            existing.total_sleep_duration_minutes = item.get("total_sleep_duration")
            existing.efficiency = item.get("efficiency")
            db.add(existing)

        # Activity
        activity_json = await client.daily_activity(start_date=start_date, end_date=end_date)
        for item in activity_json.get("data", []):
            day_str = item.get("day")
            if not day_str:
                continue
            day = date.fromisoformat(day_str)
            existing = db.query(DailyActivity).filter(DailyActivity.day == day).one_or_none()
            if existing is None:
                existing = DailyActivity(day=day)
            existing.score = item.get("score")
            existing.steps = item.get("steps")
            existing.calories_total = item.get("cal_total") or item.get("total_calories")
            db.add(existing)

        # Readiness
        readiness_json = await client.daily_readiness(start_date=start_date, end_date=end_date)
        for item in readiness_json.get("data", []):
            day_str = item.get("day")
            if not day_str:
                continue
            day = date.fromisoformat(day_str)
            existing = db.query(DailyReadiness).filter(DailyReadiness.day == day).one_or_none()
            if existing is None:
                existing = DailyReadiness(day=day)
            existing.score = item.get("score")
            db.add(existing)

        db.commit()
        return {"status": "ok", "sleep": len(sleep_json.get("data", [])), "activity": len(activity_json.get("data", [])), "readiness": len(readiness_json.get("data", []))}
    finally:
        await client.close()


