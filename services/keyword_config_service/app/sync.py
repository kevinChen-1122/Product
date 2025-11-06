import os
from typing import Dict
from datetime import datetime
from .db import get_db
from .providers.google_sheets import GoogleSheetProvider
from .providers.local_json import LocalJsonProvider

PROVIDER_MAP = {
    "gsheets": GoogleSheetProvider,
    "json": LocalJsonProvider,
}

async def run_sync():
    db = get_db()
    priority = [s.strip() for s in os.environ.get("SOURCE_PRIORITY", "gsheets,json").split(",") if s.strip()]

    merged: Dict[str, dict] = {}
    for src in priority:
        cls = PROVIDER_MAP.get(src)
        if not cls:
            continue
        provider = cls()
        items = await provider.load()
        for cfg in items:
            sid = cfg.get("seller_id")
            if not sid:
                continue
            # 後來者覆蓋先前（依 priority 順序）
            merged[sid] = cfg

    # upsert
    now = datetime.utcnow()
    for sid, data in merged.items():
        data["updated_at"] = now
        data.setdefault("created_at", now)
        await db.seller_keywords.update_one(
            {"seller_id": sid},
            {"$set": data, "$setOnInsert": {"created_at": now}},
            upsert=True
        )

    return {"ok": True, "upserted": len(merged), "sources": priority}
