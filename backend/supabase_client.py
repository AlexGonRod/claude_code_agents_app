import os
from dotenv import load_dotenv
from supabase import create_client
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

load_dotenv()

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://adcpdkadrnzjcugumseo.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

client = create_client(SUPABASE_URL, SUPABASE_KEY)


class LineItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    total: float


class InvoiceCreate(BaseModel):
    invoice_number: str
    vendor: str
    invoice_date: date
    nif: Optional[str] = None
    total: float
    line_items: List[LineItem] = []


@router.post("/invoices")
async def create_invoice(invoice: InvoiceCreate):
    try:
        data = {
            "invoice_number": invoice.invoice_number,
            "vendor": invoice.vendor,
            "invoice_date": invoice.invoice_date.isoformat(),
            "nif": invoice.nif,
            "total": invoice.total,
            "line_items": [item.dict() for item in invoice.line_items],
        }
        result = client.table("invoices").insert(data).execute()
        return {"success": True, "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invoices")
async def get_invoices():
    try:
        result = client.table("invoices").select("*").order("created_at", desc=True).execute()
        return {"success": True, "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str):
    try:
        result = client.table("invoices").select("*").eq("id", invoice_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return {"success": True, "data": result.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/invoices")
async def delete_all_invoices():
    try:
        # Get all invoices first to delete
        result = client.table("invoices").select("id").execute()
        ids = [row['id'] for row in result.data]
        
        if ids:
            client.table("invoices").delete().eq("id", ids[0]).execute()
        
        return {"success": True, "deleted": len(ids)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))