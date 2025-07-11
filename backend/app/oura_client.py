from __future__ import annotations

from typing import Any, Dict, Optional
import httpx


class OuraClient:
    BASE_URL = "https://api.ouraring.com/v2"

    def __init__(self, access_token: str):
        self._access_token = access_token
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
            timeout=30.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        response = await self._client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    async def daily_sleep(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return await self.get("/usercollection/daily_sleep", params)

    async def daily_activity(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return await self.get("/usercollection/daily_activity", params)

    async def daily_readiness(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return await self.get("/usercollection/daily_readiness", params)


