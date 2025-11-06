from fastapi import APIRouter, HTTPException, Depends, Query, Header
from .db import get_db
from .models import KeywordConfigUpsert
from datetime import datetime

router = APIRouter()

def _now():
    return datetime.utcnow()

@router.post("/keywords")
async def upsert_keywords(payload: KeywordConfigUpsert):
    db = get_db()
    data = payload.dict()
    data["updated_at"] = _now()
    data.setdefault("created_at", _now())
    await db.seller_keywords.update_one(
        {"$set": data, "$setOnInsert": {"created_at": _now()}},
        upsert=True
    )
    return {"ok": True}

@router.get("/keywords")
async def get_keywords():
    db = get_db()
    doc = await db.seller_keywords.find_one({"_id": 0})
    if not doc:
        return {"keywords": []}
    return doc

# 內部服務用：批次取
@router.get("/internal/keywords")
async def internal_fetch_keywords():
    db = get_db()
    doc = await db.seller_keywords.find_one({"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="not found or disabled")
    return doc
