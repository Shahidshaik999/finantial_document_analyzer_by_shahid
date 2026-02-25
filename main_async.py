"""
Enhanced FastAPI application with background job processing using Redis Queue.
This version supports concurrent document analysis with status tracking.
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
import os
import uuid
import logging
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

# Database imports
from database import init_db, get_db, AnalysisRequest, AnalysisResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Financial Document Analyzer (Async)",
    description="AI-powered financial document analysis with background processing",
    version="2.0.0"
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup"""
    init_db()
    logger.info("Database initialized")

# Try to import Redis Queue components
try:
    from redis import Redis
    from rq import Queue
    
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_conn = Redis.from_url(REDIS_URL)
    task_queue = Queue('default', connection=redis_conn)
    QUEUE_AVAILABLE = True
    logger.info(f"Redis Queue initialized: {REDIS_URL}")
except ImportError:
    QUEUE_AVAILABLE = False
    logger.warning("Redis/RQ not available. Using synchronous processing.")
except Exception as e:
    QUEUE_AVAILABLE = False
    logger.warning(f"Redis connection failed: {str(e)}. Using synchronous processing.")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Financial Document Analyzer API (Async) is running",
        "version": "2.0.0",
        "status": "healthy",
        "queue_enabled": QUEUE_AVAILABLE
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "Financial Document Analyzer",
        "version": "2.0.0",
        "features": {
            "background_processing": QUEUE_AVAILABLE,
            "database": True,
            "agents": ["financial_analyst", "verifier", "investment_advisor", "risk_assessor"]
        }
    }


@app.post("/analyze/async")
async def analyze_document_async(
    file: UploadFile = File(..., description="Financial document in PDF format"),
    query: str = Form(default="Provide a comprehensive financial analysis of this document"),
    db: Session = Depends(get_db)
):
    """
    Submit a financial document for asynchronous analysis.
    Returns immediately with a request_id for status tracking.
    
    Args:
        file: PDF file containing financial document
        query: Specific analysis query
        db: Database session
        
    Returns:
        Request ID and status endpoint for tracking
    """
    
    if not QUEUE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Background processing not available. Use /analyze endpoint instead."
        )
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )
    
    request_id = str(uuid.uuid4())
    file_path = f"data/queue_{request_id}.pdf"
    
    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Save uploaded file
        logger.info(f"Saving file for async processing: {file.filename}")
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        file_size = os.path.getsize(file_path)
        
        if file_size == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        
        # Clean query
        if not query or query.strip() == "":
            query = "Provide a comprehensive financial analysis of this document"
        query = query.strip()
        
        # Create database record
        analysis_request = AnalysisRequest(
            request_id=request_id,
            filename=file.filename,
            file_size_bytes=file_size,
            query=query,
            status="pending"
        )
        db.add(analysis_request)
        db.commit()
        
        # Enqueue background job
        from worker import process_financial_document
        
        job = task_queue.enqueue(
            process_financial_document,
            request_id=request_id,
            file_path=file_path,
            query=query,
            filename=file.filename,
            file_size=file_size,
            job_timeout='30m'  # 30 minute timeout
        )
        
        logger.info(f"Job enqueued: {job.id} for request {request_id}")
        
        return JSONResponse(
            status_code=202,
            content={
                "status": "accepted",
                "request_id": request_id,
                "message": "Document submitted for analysis",
                "status_endpoint": f"/analyze/status/{request_id}",
                "result_endpoint": f"/analyze/result/{request_id}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting analysis: {str(e)}")
        
        # Cleanup on error
        if os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=500,
            detail=f"Error submitting document for analysis: {str(e)}"
        )


@app.get("/analyze/status/{request_id}")
async def get_analysis_status(request_id: str, db: Session = Depends(get_db)):
    """
    Get the status of an analysis request.
    
    Args:
        request_id: Unique request identifier
        db: Database session
        
    Returns:
        Current status and metadata
    """
    
    request = db.query(AnalysisRequest).filter(
        AnalysisRequest.request_id == request_id
    ).first()
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    response = {
        "request_id": request.request_id,
        "status": request.status,
        "filename": request.filename,
        "query": request.query,
        "created_at": request.created_at.isoformat(),
        "started_at": request.started_at.isoformat() if request.started_at else None,
        "completed_at": request.completed_at.isoformat() if request.completed_at else None,
    }
    
    if request.status == "failed":
        response["error"] = request.error_message
    
    if request.status == "completed":
        response["result_endpoint"] = f"/analyze/result/{request_id}"
    
    return response


@app.get("/analyze/result/{request_id}")
async def get_analysis_result(request_id: str, db: Session = Depends(get_db)):
    """
    Get the analysis result for a completed request.
    
    Args:
        request_id: Unique request identifier
        db: Database session
        
    Returns:
        Complete analysis result
    """
    
    # Check request status
    request = db.query(AnalysisRequest).filter(
        AnalysisRequest.request_id == request_id
    ).first()
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if request.status == "pending":
        raise HTTPException(status_code=202, detail="Analysis is pending")
    
    if request.status == "processing":
        raise HTTPException(status_code=202, detail="Analysis is in progress")
    
    if request.status == "failed":
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {request.error_message}"
        )
    
    # Get result
    result = db.query(AnalysisResult).filter(
        AnalysisResult.request_id == request_id
    ).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return {
        "status": "success",
        "request_id": request_id,
        "query": request.query,
        "filename": request.filename,
        "analysis": result.analysis_text,
        "processing_time_seconds": result.processing_time_seconds,
        "completed_at": request.completed_at.isoformat()
    }


@app.post("/analyze")
async def analyze_document_sync(
    file: UploadFile = File(..., description="Financial document in PDF format"),
    query: str = Form(default="Provide a comprehensive financial analysis of this document")
):
    """
    Synchronous analysis endpoint (blocks until complete).
    Use /analyze/async for non-blocking operation.
    """
    
    from main import analyze_document
    return await analyze_document(file=file, query=query)


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Financial Document Analyzer API (Async)...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
