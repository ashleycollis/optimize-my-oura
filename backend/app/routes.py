from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from .config import get_settings
from .oura_client import OuraClient


router = APIRouter(prefix="/api", tags=["oura"])


def get_access_token() -> str:
    settings = get_settings()
    if not settings.oura_personal_access_token:
        raise HTTPException(status_code=500, detail="Oura token not configured")
    return settings.oura_personal_access_token


@router.get("/sleep/daily")
async def get_sleep_daily(
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    access_token: str = Depends(get_access_token),
):
    client = OuraClient(access_token)
    try:
        data = await client.daily_sleep(start_date=start_date, end_date=end_date)
        return data
    finally:
        await client.close()


@router.get("/activity/daily")
async def get_activity_daily(
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    access_token: str = Depends(get_access_token),
):
    client = OuraClient(access_token)
    try:
        data = await client.daily_activity(start_date=start_date, end_date=end_date)
        return data
    finally:
        await client.close()


@router.get("/readiness/daily")
async def get_readiness_daily(
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    access_token: str = Depends(get_access_token),
):
    client = OuraClient(access_token)
    try:
        data = await client.daily_readiness(start_date=start_date, end_date=end_date)
        return data
    finally:
        await client.close()


