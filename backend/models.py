# backend/models.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class LineItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    amount: float

class InvoiceData(BaseModel):
    vendor: str
    date: str  # Using string for simplicity, could be datetime
    amount: float
    tax: float
    line_items: List[LineItem]
    notes: Optional[str] = None

class TokenData(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: datetime

class GoogleOAuthURL(BaseModel):
    auth_url: str

class UserInfo(BaseModel):
    id: str
    email: str
    name: str
    picture: Optional[str] = None

class OCRResponse(BaseModel):
    raw_text: str
    vendor: Optional[str] = None
    date: Optional[str] = None
    amount: Optional[float] = None
    tax: Optional[float] = None
    line_items: Optional[List[LineItem]] = None
    notes: Optional[str] = None