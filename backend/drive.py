# backend/drive.py
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models import JustificacioData
import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

load_dotenv()

router = APIRouter()

SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), "service-account.json")

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)

SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "4-RELACIO_DESPESES_PER_UNITAT")
JUSTIFICACIO_SHEET_NAME = os.getenv("JUSTIFICACIO_SHEET_NAME", "5-JUSTIFICACIO")


class LineItem(BaseModel):
    unit: str
    quantity: float
    unitPrice: float
    total: float


class InvoiceCreate(BaseModel):
    invoiceNumber: str
    vendor: str
    invoiceDate: str
    lineItems: list[LineItem]
    total: float
    nif: str | None = None


class InvoiceResponse(BaseModel):
    success: bool
    rowIndex: int


class JustificacioResponse(BaseModel):
    success: bool
    rowIndex: int


@router.post("/invoices", response_model=InvoiceResponse)
async def create_invoice(invoice: InvoiceCreate):
    logger.info(f"Received invoice data: {invoice}")
    try:
        service = build("sheets", "v4", credentials=credentials)

        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A1:G50"
        ).execute()
        existing_values = result.get("values", [])
        
        next_row = 4

        rows_written = 0
        for i, item in enumerate(invoice.lineItems):
            values = [
                [
                    invoice.invoiceNumber,
                    invoice.vendor,
                    invoice.invoiceDate,
                    item.unit,
                    item.quantity,
                    item.unitPrice,
                    item.total,
                ]
            ]
            
            row_num = next_row + i
            range_to_write = f"{SHEET_NAME}!A{row_num}:G{row_num}"
            
            logger.info(f"Writing line item {i+1} to range: {range_to_write}")
            logger.info(f"Line item values: {values}")

            try:
                result = service.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=range_to_write,
                    valueInputOption="USER_ENTERED",
                    body={"values": values}
                ).execute()
                logger.info(f"Update result: {result}")
                rows_written += 1
            except Exception as update_error:
                logger.error(f"Update error: {update_error}")
                raise

        row_index = next_row

        return InvoiceResponse(success=True, rowIndex=row_index)

    except Exception as e:
        logger.error(f"Error in create_invoice: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to append to sheet: {str(e)}")


@router.post("/justificacio", response_model=JustificacioResponse)
async def create_justificacio(justificacio: JustificacioData):
    logger.info(f"Received justificacio data: {justificacio}")
    try:
        service = build("sheets", "v4", credentials=credentials)

        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{JUSTIFICACIO_SHEET_NAME}!B:B"
        ).execute()
        all_values = result.get("values", [])

        target_ranges = [(17, 36), (57, 76), (97, 116)]
        next_row = None

        for start, end in target_ranges:
            rows_to_check = all_values[start-1:end]

            for idx, row in enumerate(rows_to_check):
                row_num = start + idx
                if not row or not row[0]:
                    next_row = row_num
                    break

            if next_row:
                break

        if not next_row:
            raise HTTPException(status_code=400, detail="Sheet full")

        values = [
            [
                "Factura",
                justificacio.invoiceNumber,
                justificacio.invoiceDate,
                justificacio.vendor,
                justificacio.nif or "",
                "",
                justificacio.total,
                "100%",
                f"=H{next_row}*I{next_row}",
                "alimentació (amanides, tomàquets, pa, tonyina, olives, embotits, botifarres, sardines, oli, all, patates, canapès, postres, cafè, xocolata...), begudes (refrescos, agua, vi, cava, combinats...), parament de taula (plats de diversos tamanys, gots de diversos tamanys, tovallons, forquilles, culleres, ganivets, estovalles,...)"
            ]
        ]

        range_to_write = f"{JUSTIFICACIO_SHEET_NAME}!B{next_row}:K{next_row}"

        range_to_write = f"{JUSTIFICACIO_SHEET_NAME}!B{next_row}:K{next_row}"

        logger.info(f"Writing justificacio to range: {range_to_write}")
        logger.info(f"Justificacio values: {values}")

        try:
            result = service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=range_to_write,
                valueInputOption="USER_ENTERED",
                body={"values": values}
            ).execute()
            logger.info(f"Update result: {result}")
        except Exception as update_error:
            logger.error(f"Update error: {update_error}")
            raise

        row_index = next_row

        return JustificacioResponse(success=True, rowIndex=row_index)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_justificacio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to append to sheet: {str(e)}")