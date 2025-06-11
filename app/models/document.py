from pydantic import BaseModel
from enum import Enum
from typing import Optional


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentResponse(BaseModel):
    id: str
    status: ProcessingStatus
    message: Optional[str] = None
    document_name: str


class ProcessingResponse(BaseModel):
    status: ProcessingStatus
    documents_processed: Optional[int] = None
    message: Optional[str] = None
