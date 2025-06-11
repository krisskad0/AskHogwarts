import shutil
import os
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Depends
from typing import List
import uuid
from ..models.document import DocumentResponse, ProcessingStatus, ProcessingResponse
from ..services.pdf_processor import PDFProcessor
from ..services.vector_store import VectorStore
from ..core.config import get_settings, Settings

router = APIRouter()

# Store upload status
processing_status = {}


async def process_document(
    file_path: str,
    doc_id: str,
    pdf_processor: PDFProcessor,
    vector_store: VectorStore
):
    """Background task to process uploaded PDF"""
    try:
        # Update status to processing
        processing_status[doc_id] = ProcessingStatus.PROCESSING
        
        # Process PDF
        chunks = await pdf_processor.process_pdf(file_path)
        
        # Store in vector database
        await vector_store.upsert_documents(chunks)
        
        # Update status to completed
        processing_status[doc_id] = ProcessingStatus.COMPLETED
        
    except Exception as e:
        processing_status[doc_id] = ProcessingStatus.FAILED
        print(f"Error processing document: {str(e)}")
        raise


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings)
):
    """
    Upload and process a PDF document
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Generate unique ID for the document
    doc_id = str(uuid.uuid4())
    
    # Create upload directory if it doesn't exist
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save the uploaded file
    file_path = os.path.join(upload_dir, f"{doc_id}.pdf")
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    # Initialize services
    pdf_processor = PDFProcessor(settings)
    vector_store = VectorStore(settings)
    
    # Add document processing to background tasks
    processing_status[doc_id] = ProcessingStatus.PENDING
    background_tasks.add_task(
        process_document,
        file_path,
        doc_id,
        pdf_processor,
        vector_store
    )
    
    return DocumentResponse(
        id=doc_id,
        status=ProcessingStatus.PENDING,
        document_name=file.filename
    )


@router.get("/status/{doc_id}", response_model=ProcessingResponse)
async def get_processing_status(doc_id: str):
    """
    Get the processing status of a document
    """
    if doc_id not in processing_status:
        raise HTTPException(status_code=404, detail="Document not found")
    
    status = processing_status[doc_id]
    return ProcessingResponse(
        status=status,
        message=f"Document processing {status}"
    )
