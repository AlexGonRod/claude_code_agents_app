# backend/ocr.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import logging
import json
from models import OCRResponse
from prompts import PROMPTS
from worker import image_queue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

GEMINI_API_KEY = "AIzaSyAEgwqIXl6IL4OkmaQ_tAKbUHaluUOtB_I"
GEMINI_MODEL = "gemini-3-flash-preview"


class OCRRequest(BaseModel):
    image: str


class AsyncResponse(BaseModel):
    task_id: str


class TaskStatusResponse(BaseModel):
    status: str
    result: str = None
    error: str = None


async def process_image_content(image_data: str) -> str:
    if "," in image_data:
        image_data = image_data.split(",")[1]
    logger.info(f"Image data length: {len(image_data)}")

    system_prompt = PROMPTS.get('SYSTEM_PROMTP', '')
    user_prompt = PROMPTS.get('USER_PROMPT', '')
    
    logger.info("Calling Gemini API...")

    system_prompt = PROMPTS.get('SYSTEM_PROMTP', '')
    user_prompt = PROMPTS.get('USER_PROMPT', '')

    contents = [
        {
            "parts": [
                {"text": system_prompt + "\n\n" + user_prompt},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": image_data
                    }
                }
            ]
        }
    ]

    response = await httpx.AsyncClient().post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}",
        json={"contents": contents},
        timeout=60.0
    )
    
    logger.info(f"Response status: {response.status_code}")
    response.raise_for_status()
    result = response.json()

    text = result["candidates"][0]["content"]["parts"][0]["text"]
    
    logger.info(f"Gemini response: {text[:500]}")

    return text


@router.post("/process", response_model=OCRResponse)
async def process_image(request: OCRRequest):
    try:
        logger.info("Processing image...")
        image_data = request.image
        text = await process_image_content(image_data)
        return OCRResponse(raw_text=text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@router.post("/process/async", response_model=AsyncResponse)
async def process_image_async(request: OCRRequest):
    task_id = await image_queue.add(request.image)
    return AsyncResponse(task_id=task_id)


@router.get("/process/{task_id}", response_model=TaskStatusResponse)
async def get_result(task_id: str):
    result = await image_queue.get_result(task_id)
    if result["status"] == "not_found":
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskStatusResponse(
        status=result["status"],
        result=result.get("result"),
        error=result.get("error")
    )