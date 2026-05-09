# Google Sheets Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create backend endpoint to save invoice data to Google Sheets via OAuth-authenticated API call

**Architecture:** Frontend calls backend API → backend uses OAuth token → backend appends row to Google Sheets

**Tech Stack:** FastAPI (backend), Google Sheets API v4, existing OAuth from auth.py

---

## Context

**Backend:** `/Users/alexgonzalez/Documents/projects/claude_code_agents_app/backend`
- FastAPI app in `main.py`
- Existing OAuth in `auth.py` (provides access_token)
- Needs new: `drive.py` with Google Sheets endpoint

**Frontend:** `/Users/alexgonzalez/Documents/projects/claude_code_agents_app/frontend`
- Calls backend API: `POST /drive/invoices`
- Current: `sheets.js` with mock return

**Invoice data model:**
```python
InvoiceCreate = {
    invoiceNumber: str,       # num de document
    vendor: str,          # Proveïdor
    invoiceDate: str,     # Data (YYYY-MM-DD)
    unit: str,          # Unitat
    quantity: int,       # Quantitat
    unitPrice: float,    # Preu unitari
    total: float       # Total
}
```

**Configuration:**
- SHEET_ID: Google Sheets spreadsheet ID
- SHEET_NAME: "Facturas"

---

## Task 1: Create drive.py with Sheets endpoint

**Files:**
- Create: `backend/drive.py`

```
- [ ] Step 1: Create drive.py with FastAPI router and POST /invoices endpoint

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from googleapiclient.discovery import build
from typing import Optional

router = APIRouter()

class InvoiceCreate(BaseModel):
    invoiceNumber: str
    vendor: str
    invoiceDate: str
    unit: str
    quantity: int
    unitPrice: float
    total: float

SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
SHEET_NAME = "Facturas"

@router.post("/invoices")
async def create_invoice(invoice: InvoiceCreate, access_token: str):
    """Append invoice to Google Sheets"""
    # Build Google Sheets service
    # Append row
    # Return success
```

- [ ] Step 2: Add to main.py imports

- [ ] Step 3: Commit

---

## Task 2: Update frontend to call backend API

**Files:**
- Modify: `frontend/src/lib/sheets.js`

- [ ] Step 1: Replace mock with fetch to backend

```javascript
export async function appendInvoiceToSheet(invoiceData, token) {
  const response = await fetch('http://localhost:8000/drive/invoices', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(invoiceData)
  });
  return response.json();
}
```

- [ ] Step 2: Commit

---

## Task 3: Wire up auth token

**Files:**
- Modify: `frontend/src/lib/sheets.js`
- Read token from authStore

- [ ] Step 1: Update to use auth token

- [ ] Step 2: Test build

- [ ] Step 3: Commit