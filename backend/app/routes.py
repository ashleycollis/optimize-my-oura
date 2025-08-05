from typing import Optional, List, Tuple, Dict, Any
from datetime import date, datetime, timedelta
import re
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from .config import get_settings
from .oura_client import OuraClient
from .db import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import DailySleep, DailyReadiness, DailyActivity
import httpx
import json


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



class QARequest(BaseModel):
    question: str


def _extract_date_range(question_text: str) -> Tuple[Optional[date], Optional[date]]:
    text = question_text.lower()
    # Explicit YYYY-MM-DD dates
    found = re.findall(r"(\d{4}-\d{2}-\d{2})", text)
    if len(found) >= 2:
        try:
            start = date.fromisoformat(found[0])
            end = date.fromisoformat(found[1])
            return (start, end)
        except Exception:
            pass
    if len(found) == 1:
        try:
            single = date.fromisoformat(found[0])
            return (single, single)
        except Exception:
            pass

    # Relative ranges like "last 7 days/weeks/months"
    m = re.search(r"last\s+(\d+)\s*(day|days|week|weeks|month|months)", text)
    if m:
        qty = int(m.group(1))
        unit = m.group(2)
        days = qty
        if unit.startswith("week"):
            days = qty * 7
        elif unit.startswith("month"):
            days = qty * 30
        end_dt = datetime.utcnow().date()
        start_dt = end_dt - timedelta(days=days)
        return (start_dt, end_dt)

    # Phrases like "since 2024-01-01"
    m = re.search(r"since\s+(\d{4}-\d{2}-\d{2})", text)
    if m:
        try:
            start = date.fromisoformat(m.group(1))
            end_dt = datetime.utcnow().date()
            return (start, end_dt)
        except Exception:
            pass

    return (None, None)


def _format_number(value: Optional[float], digits: int = 2) -> str:
    if value is None:
        return "N/A"
    return f"{value:.{digits}f}"


@router.post("/qa")
def answer_question(payload: QARequest, db: Session = Depends(get_db)):
    q = payload.question.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Question is required")

    q_lower = q.lower()
    start_dt, end_dt = _extract_date_range(q_lower)

    # Determine intent
    is_avg = "average" in q_lower or "avg" in q_lower or "mean" in q_lower
    is_best = any(w in q_lower for w in ["best", "highest", "max"])
    is_worst = any(w in q_lower for w in ["worst", "lowest", "min"])
    wants_steps = "steps" in q_lower and ("total" in q_lower or "sum" in q_lower)

    # Which metric
    target_sleep = "sleep" in q_lower
    target_readiness = "readiness" in q_lower
    target_activity = "activity" in q_lower or ("steps" in q_lower)

    # Fallbacks: if no explicit target but mentions score
    if not (target_sleep or target_readiness or target_activity):
        if "steps" in q_lower:
            target_activity = True
        elif "score" in q_lower:
            # Heuristic: prefer readiness if unspecified
            target_readiness = True

    # Apply date filters helpers
    def apply_date_filter(query, model):
        if start_dt:
            query = query.filter(model.day >= start_dt)
        if end_dt:
            query = query.filter(model.day <= end_dt)
        return query

    # Handle intents
    if is_avg and target_sleep:
        query = apply_date_filter(db.query(func.avg(DailySleep.score)), DailySleep)
        avg_val = query.scalar()
        return {"answer": f"Average sleep score is {_format_number(avg_val)}.", "intent": "average_sleep", "start_date": start_dt.isoformat() if start_dt else None, "end_date": end_dt.isoformat() if end_dt else None}

    if is_avg and target_readiness:
        query = apply_date_filter(db.query(func.avg(DailyReadiness.score)), DailyReadiness)
        avg_val = query.scalar()
        return {"answer": f"Average readiness score is {_format_number(avg_val)}.", "intent": "average_readiness", "start_date": start_dt.isoformat() if start_dt else None, "end_date": end_dt.isoformat() if end_dt else None}

    if is_avg and target_activity:
        query = apply_date_filter(db.query(func.avg(DailyActivity.score)), DailyActivity)
        avg_val = query.scalar()
        return {"answer": f"Average activity score is {_format_number(avg_val)}.", "intent": "average_activity", "start_date": start_dt.isoformat() if start_dt else None, "end_date": end_dt.isoformat() if end_dt else None}

    if wants_steps:
        query = apply_date_filter(db.query(func.sum(DailyActivity.steps)), DailyActivity)
        total_steps = query.scalar() or 0
        return {"answer": f"Total steps: {int(total_steps):,}.", "intent": "total_steps", "start_date": start_dt.isoformat() if start_dt else None, "end_date": end_dt.isoformat() if end_dt else None}

    if (is_best or is_worst) and target_sleep:
        order_field = DailySleep.score
        query = db.query(DailySleep)
        query = apply_date_filter(query, DailySleep)
        if is_best:
            row = query.order_by(order_field.desc()).first()
            if row:
                return {"answer": f"Best sleep day was {row.day.isoformat()} with score {row.score}.", "intent": "best_sleep"}
        else:
            row = query.order_by(order_field.asc()).first()
            if row:
                return {"answer": f"Worst sleep day was {row.day.isoformat()} with score {row.score}.", "intent": "worst_sleep"}

    if (is_best or is_worst) and target_readiness:
        order_field = DailyReadiness.score
        query = db.query(DailyReadiness)
        query = apply_date_filter(query, DailyReadiness)
        if is_best:
            row = query.order_by(order_field.desc()).first()
            if row:
                return {"answer": f"Best readiness day was {row.day.isoformat()} with score {row.score}.", "intent": "best_readiness"}
        else:
            row = query.order_by(order_field.asc()).first()
            if row:
                return {"answer": f"Worst readiness day was {row.day.isoformat()} with score {row.score}.", "intent": "worst_readiness"}

    if (is_best or is_worst) and target_activity:
        order_field = DailyActivity.score
        query = db.query(DailyActivity)
        query = apply_date_filter(query, DailyActivity)
        if is_best:
            row = query.order_by(order_field.desc()).first()
            if row:
                return {"answer": f"Best activity day was {row.day.isoformat()} with score {row.score}.", "intent": "best_activity"}
        else:
            row = query.order_by(order_field.asc()).first()
            if row:
                return {"answer": f"Worst activity day was {row.day.isoformat()} with score {row.score}.", "intent": "worst_activity"}

    # Default help
    return {
        "answer": (
            "I can answer questions like 'average sleep score last 30 days', "
            "'total steps from 2024-01-01 to 2024-03-31', 'best readiness day', or 'worst sleep day'."
        ),
        "intent": "help"
    }


class QALLMRequest(BaseModel):
    question: str


def _build_schema_prompt() -> str:
    return (
        "You are a helpful assistant that translates a user's question about Oura data "
        "into a single structured JSON command. Available tables and fields: \n"
        "- daily_sleep(day, score, total_sleep_duration_minutes, efficiency)\n"
        "- daily_activity(day, score, steps, calories_total)\n"
        "- daily_readiness(day, score)\n\n"
        "Supported operations: avg, sum, max, min.\n"
        "Always respond with ONLY a compact JSON object: {\n"
        "  \"operation\": one of [avg,sum,max,min],\n"
        "  \"table\": table name,\n"
        "  \"field\": field name,\n"
        "  \"start_date\": optional YYYY-MM-DD,\n"
        "  \"end_date\": optional YYYY-MM-DD\n"
        "}\n"
        "Examples:\n"
        "Q: average sleep score last 30 days\n"
        "A: {\"operation\":\"avg\",\"table\":\"daily_sleep\",\"field\":\"score\"}\n"
        "Q: total steps from 2024-01-01 to 2024-03-31\n"
        "A: {\"operation\":\"sum\",\"table\":\"daily_activity\",\"field\":\"steps\",\"start_date\":\"2024-01-01\",\"end_date\":\"2024-03-31\"}\n"
        "Q: best readiness day\n"
        "A: {\"operation\":\"max\",\"table\":\"daily_readiness\",\"field\":\"score\"}\n"
        "Q: worst sleep day\n"
        "A: {\"operation\":\"min\",\"table\":\"daily_sleep\",\"field\":\"score\"}"
    )


def _parse_llm_json(text: str) -> Optional[Dict[str, Any]]:
    text = text.strip()
    # Try raw JSON first
    try:
        return json.loads(text)
    except Exception:
        pass
    # Try to extract JSON from code fences or text
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            return None
    return None


def _validate_and_apply_dates(q: Dict[str, Any]) -> Tuple[Optional[date], Optional[date]]:
    start_dt: Optional[date] = None
    end_dt: Optional[date] = None
    if isinstance(q.get("start_date"), str):
        try:
            start_dt = date.fromisoformat(q["start_date"])
        except Exception:
            start_dt = None
    if isinstance(q.get("end_date"), str):
        try:
            end_dt = date.fromisoformat(q["end_date"])
        except Exception:
            end_dt = None
    return start_dt, end_dt


def _model_and_field(table: str, field: str):
    table_map = {
        "daily_sleep": (DailySleep, {"score": DailySleep.score, "total_sleep_duration_minutes": DailySleep.total_sleep_duration_minutes, "efficiency": DailySleep.efficiency}),
        "daily_activity": (DailyActivity, {"score": DailyActivity.score, "steps": DailyActivity.steps, "calories_total": DailyActivity.calories_total}),
        "daily_readiness": (DailyReadiness, {"score": DailyReadiness.score}),
    }
    if table not in table_map:
        return None, None
    model, fields = table_map[table]
    return model, fields.get(field)


@router.post("/qa_llm")
def answer_question_llm(payload: QALLMRequest, db: Session = Depends(get_db)):
    settings = get_settings()
    if not settings.ollama_enabled:
        raise HTTPException(status_code=400, detail="LLM not enabled. Set OLLAMA_ENABLED=true in backend .env and restart.")

    q = payload.question.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Question is required")

    system_prompt = _build_schema_prompt()
    try:
        resp = httpx.post(
            f"{settings.ollama_host}/api/chat",
            json={
                "model": settings.ollama_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": q},
                ],
                "stream": False,
            },
            timeout=30.0,
        )
        resp.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM request failed: {e}")

    data = resp.json()
    content = (
        (data.get("message") or {}).get("content")
        or ((data.get("choices") or [{}])[0].get("message") or {}).get("content")
        or ""
    )
    parsed = _parse_llm_json(content)
    if not parsed:
        return {"answer": "Sorry, I could not understand the request.", "raw": content}

    op = (parsed.get("operation") or "").lower()
    table = (parsed.get("table") or "").lower()
    field = (parsed.get("field") or "").lower()
    model, col = _model_and_field(table, field)
    if not model or not col:
        return {"answer": "Request referenced an unknown table or field.", "parsed": parsed}

    start_dt, end_dt = _validate_and_apply_dates(parsed)

    def apply_date_filter(query):
        if start_dt:
            query = query.filter(model.day >= start_dt)
        if end_dt:
            query = query.filter(model.day <= end_dt)
        return query

    if op in ("avg", "sum"):
        agg = func.avg(col) if op == "avg" else func.sum(col)
        query = apply_date_filter(db.query(agg))
        value = query.scalar()
        if value is None:
            return {"answer": "No data found for that range.", "parsed": parsed}
        label = f"{op} of {table}.{field}"
        return {"answer": f"{label}: {value:.2f}", "parsed": parsed}

    if op in ("max", "min"):
        query = apply_date_filter(db.query(model))
        row = query.order_by(col.desc() if op == "max" else col.asc()).first()
        if not row:
            return {"answer": "No data found for that range.", "parsed": parsed}
        day_val = row.day.isoformat()
        val = getattr(row, field)
        label = "best" if op == "max" else "worst"
        return {"answer": f"{label.capitalize()} {table} by {field} was {day_val} with {val}.", "parsed": parsed}

    return {"answer": "Unsupported operation.", "parsed": parsed}

