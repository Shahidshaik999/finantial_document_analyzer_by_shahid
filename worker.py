"""
Background worker for processing financial document analysis tasks.
Uses Redis Queue (RQ) for job management and background processing.
"""

import os
import time
import logging
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import database models
from database import SessionLocal, AnalysisRequest, AnalysisResult

# Import CrewAI components
from crewai import Crew, Process
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from task import (
    analyze_financial_document as analyze_task,
    verification_task,
    investment_analysis_task,
    risk_assessment_task
)


def process_financial_document(
    request_id: str,
    file_path: str,
    query: str,
    filename: str,
    file_size: int
) -> Dict[str, Any]:
    """
    Background job to process financial document analysis.
    
    Args:
        request_id: Unique request identifier
        file_path: Path to the uploaded PDF file
        query: User's analysis query
        filename: Original filename
        file_size: File size in bytes
        
    Returns:
        Dictionary with analysis results
    """
    db = SessionLocal()
    start_time = time.time()
    
    try:
        # Update request status to processing
        request = db.query(AnalysisRequest).filter(
            AnalysisRequest.request_id == request_id
        ).first()
        
        if request:
            request.status = "processing"
            request.started_at = datetime.utcnow()
            db.commit()
        
        logger.info(f"Starting analysis for request {request_id}")
        
        # Create the financial analysis crew
        financial_crew = Crew(
            agents=[financial_analyst, verifier, investment_advisor, risk_assessor],
            tasks=[analyze_task, verification_task, investment_analysis_task, risk_assessment_task],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute the crew
        inputs = {
            'query': query,
            'file_path': file_path
        }
        
        result = financial_crew.kickoff(inputs=inputs)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Store result in database
        analysis_result = AnalysisResult(
            request_id=request_id,
            analysis_text=str(result),
            processing_time_seconds=processing_time
        )
        db.add(analysis_result)
        
        # Update request status
        if request:
            request.status = "completed"
            request.completed_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Analysis completed for request {request_id} in {processing_time:.2f}s")
        
        return {
            "status": "success",
            "request_id": request_id,
            "result": str(result),
            "processing_time": processing_time
        }
        
    except Exception as e:
        logger.error(f"Error processing request {request_id}: {str(e)}")
        
        # Update request with error
        if request:
            request.status = "failed"
            request.error_message = str(e)
            request.completed_at = datetime.utcnow()
            db.commit()
        
        raise
    
    finally:
        # Cleanup temporary file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Cleaned up file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup file: {str(e)}")
        
        db.close()


if __name__ == "__main__":
    """
    Run the RQ worker to process background jobs.
    
    Usage:
        python worker.py
    
    Or with RQ:
        rq worker --with-scheduler
    """
    try:
        from redis import Redis
        from rq import Worker, Queue, Connection
        
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_conn = Redis.from_url(redis_url)
        
        logger.info(f"Starting RQ worker connected to {redis_url}")
        
        with Connection(redis_conn):
            worker = Worker(['default'])
            worker.work()
            
    except ImportError:
        logger.error("Redis and RQ not installed. Install with: pip install redis rq")
        logger.info("Falling back to synchronous processing mode")
