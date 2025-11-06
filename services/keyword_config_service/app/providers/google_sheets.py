import os
import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any

from .base import Provider

class GoogleSheetProvider(Provider):
    name = "gsheets"

    def __init__(self):
        self.sheet_id = os.environ.get("GSHEETS_SHEET_ID")
        self.worksheet = os.environ.get("GSHEETS_WORKSHEET", "Sheet1")
        self.columns = {
            "seller_id": os.environ.get("GSHEETS_COL_SELLER_ID", "seller_id"),
            "keywords": os.environ.get("GSHEETS_COL_KEYWORDS", "keywords"),
            "min_price": os.environ.get("GSHEETS_COL_MIN_PRICE", "min_price"),
            "max_price": os.environ.get("GSHEETS_COL_MAX_PRICE", "max_price"),
            "platforms": os.environ.get("GSHEETS_COL_PLATFORMS", "platforms"),
            "regions": os.environ.get("GSHEETS_COL_REGIONS", "regions"),
            "channels": os.environ.get("GSHEETS_COL_CHANNELS", "channels"),
            "cooldown": os.environ.get("GSHEETS_COL_COOLDOWN", "cooldown_minutes"),
        }

        # 驗證：用服務帳戶 JSON 檔或 base64
        creds_json_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        creds_b64 = os.environ.get("GOOGLE_CREDENTIALS_B64")
        if creds_b64 and not creds_json_path:
            import base64, json, tempfile
            data = base64.b64decode(creds_b64)
            obj = json.loads(data)
            tf = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
            import pathlib; pathlib.Path(tf.name).write_text(json.dumps(obj))
            creds_json_path = tf.name

        scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
        self.creds = Credentials.from_service_account_file(creds_json_path, scopes=scopes)
        self.gc = gspread.authorize(self.creds)

    async def load(self) -> List[Dict[str, Any]]:
        sh = self.gc.open_by_key(self.sheet_id)
        ws = sh.worksheet(self.worksheet)
        rows = ws.get_all_records()  # 以欄名為 key
        out: List[Dict[str, Any]] = []

        for r in rows:
            seller_id = str(r.get(self.columns["seller_id"], "")).strip()
            if not seller_id:
                continue
            keywords_raw = r.get(self.columns["keywords"], "")
            keywords = [s.strip() for s in str(keywords_raw).split(",") if str(s).strip()]

            def to_int(v):
                try:
                    return int(float(str(v).strip()))
                except:
                    return None

            min_price = to_int(r.get(self.columns["min_price"]))
            max_price = to_int(r.get(self.columns["max_price"]))
            platforms = [s.strip().lower() for s in str(r.get(self.columns["platforms"], "")).split(",") if s.strip()]
            regions = [s.strip().lower() for s in str(r.get(self.columns["regions"], "")).split(",") if s.strip()]
            channels = [s.strip().lower() for s in str(r.get(self.columns["channels"], "email")).split(",") if s.strip()]
            cooldown = to_int(r.get(self.columns["cooldown"])) or 30

            out.append({
                "seller_id": seller_id,
                "keywords": keywords,
                "filters": {
                    "min_price": min_price,
                    "max_price": max_price,
                    "regions": regions or None,
                    "platforms": platforms or None,
                },
                "notification": {
                    "channels": channels or ["email"],
                    "cooldown_minutes": cooldown,
                },
            })
        return out
