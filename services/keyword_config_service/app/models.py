from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Literal, Dict, Any

class Contact(BaseModel):
    email: Optional[EmailStr] = None
    line_id: Optional[str] = None

class Filters(BaseModel):
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    regions: Optional[List[str]] = None
    platforms: Optional[List[Literal["carousell", "shopee"]]] = None

class KeywordConfigUpsert(BaseModel):
    keywords: List[str]
    filters: Optional[Filters] = None