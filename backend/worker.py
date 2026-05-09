import asyncio
import uuid
from typing import Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class OCRTask:
    id: str
    status: TaskStatus
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime = None


class ImageQueue:
    def __init__(self, max_concurrent=5):
        self.max_concurrent = max_concurrent
        self.queue: asyncio.Queue = asyncio.Queue()
        self.tasks: dict[str, OCRTask] = {}
        self.processing = 0
        self._worker_task = None

    async def add(self, image_data: str) -> str:
        task_id = str(uuid.uuid4())[:8]
        self.tasks[task_id] = OCRTask(
            id=task_id,
            status=TaskStatus.PENDING,
            created_at=datetime.now()
        )
        await self.queue.put((task_id, image_data))

        if not self._worker_task or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._process_queue())

        return task_id

    async def get_result(self, task_id: str) -> dict:
        task = self.tasks.get(task_id)
        if not task:
            return {"status": "not_found"}

        return {
            "status": task.status.value,
            "result": task.result,
            "error": task.error
        }

    async def _process_queue(self):
        while not self.queue.empty():
            if self.processing >= self.max_concurrent:
                await asyncio.sleep(0.5)
                continue

            try:
                task_id, image_data = await asyncio.wait_for(
                    self.queue.get(), timeout=1.0
                )
            except asyncio.TimeoutError:
                continue

            self.processing += 1
            task = self.tasks[task_id]
            task.status = TaskStatus.PROCESSING

            try:
                from ocr import process_image_content
                result = await process_image_content(image_data)
                task.result = result
                task.status = TaskStatus.COMPLETED
            except Exception as e:
                task.error = str(e)
                task.status = TaskStatus.FAILED
            finally:
                self.processing -= 1


image_queue = ImageQueue(max_concurrent=5)