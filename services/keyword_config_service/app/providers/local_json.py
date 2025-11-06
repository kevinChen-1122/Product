import os, json, glob
from typing import List, Dict, Any
from .base import Provider

class LocalJsonProvider(Provider):
    name = "json"

    def __init__(self):
        # 預設讀取 /app/config/seller_configs/*.json
        self.dir = os.environ.get("LOCAL_JSON_DIR", "/app/config/seller_configs")

    async def load(self) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for path in glob.glob(os.path.join(self.dir, "*.json")):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # 支援單筆或陣列
                    if isinstance(data, dict):
                        data = [data]
                    for item in data:
                        if "seller_id" in item and "keywords" in item:
                            out.append(item)
            except Exception:
                continue
        return out
