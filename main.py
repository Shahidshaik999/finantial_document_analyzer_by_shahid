from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
import logging
import time
from typing import Optional

from crewai import Crew, Process
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from task import (
    analyze_financial_document as analyze_task,
    verification_task,
    investment_analysis_task,
    risk_assessment_task
)
from tools import read_financial_document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Financial Document Analyzer",
    description="AI-powered financial document analysis system using CrewAI with Groq",
    version="1.0.0"
)

def run_financial_crew_with_retry(query: str, file_path: str, max_retries: int = 3) -> dict:
    """
    Execute the financial analysis crew with automatic retry on rate limits.
    
    Args:
        query: User's analysis query
        file_path: Path to the financial document
        max_retries: Maximum number of retry attempts
        
    Returns:
        Dictionary containing analysis results
    """
    for attempt in range(max_retries):
        try:
            # Read the document content (truncated for Groq free tier)
            document_content = read_financial_document(file_path, max_chars=5000)
            
            # Create the financial analysis crew
            financial_crew = Crew(
                agents=[financial_analyst, verifier, investment_advisor, risk_assessor],
                tasks=[analyze_task, verification_task, investment_analysis_task, risk_assessment_task],
                process=Process.sequential,
                verbose=True
            )
            
            # Execute the crew with inputs
            inputs = {
                'query': query,
                'file_path': file_path,
                'document_content': document_content
            }
            
            result = financial_crew.kickoff(inputs=inputs)
            
            return {
                "status": "success",
                "result": str(result)
            }
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check if it's a rate limit error
            if "rate_limit" in error_msg or "rate limit" in error_msg:
                if attempt < max_retries - 1:
                    wait_time = 15 * (attempt + 1)  # Exponential backoff: 15s, 30s, 45s
                    logger.warning(f"Rate limit hit. Waiting {wait_time}s before retry {attempt + 2}/{max_retries}...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error("Rate limit exceeded after all retries")
                    raise HTTPException(
                        status_code=429,
                        detail=f"Rate limit exceeded. Please wait 60 seconds and try again. Groq free tier has strict limits."
                    )
            else:
                # Non-rate-limit error, raise immediately
                logger.error(f"Crew execution error: {str(e)}")
                raise
    
    # Should never reach here, but just in case
    raise HTTPException(status_code=500, detail="Analysis failed after all retries")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Financial Document Analyzer API is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "Financial Document Analyzer",
        "agents": ["financial_analyst", "verifier", "investment_advisor", "risk_assessor"]
    }

@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(..., description="Financial document in PDF format"),
    query: str = Form(default="Provide a comprehensive financial analysis of this document")
):
    """
    Analyze a financial document and provide comprehensive investment recommendations.
    
    Args:
        file: PDF file containing financial document
        query: Specific analysis query or question
        
    Returns:
        Comprehensive financial analysis including:
        - Financial metrics and trends
        - Investment recommendations
        - Risk assessment
        - Document verification
    """
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported. Please upload a PDF document."
        )
    
    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"
    
    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Save uploaded file
        logger.info(f"Saving uploaded file: {file.filename}")
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Validate file size
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        
        logger.info(f"File saved successfully: {file_size} bytes")
        
        # Validate and clean query
        if not query or query.strip() == "":
            query = "Provide a comprehensive financial analysis of this document"
        
        query = query.strip()
        logger.info(f"Processing query: {query}")
        
        # Process the financial document with all analysts
        logger.info("Starting financial analysis crew...")
        result = run_financial_crew_with_retry(query=query, file_path=file_path)
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "query": query,
                "analysis": result["result"],
                "file_processed": file.filename,
                "file_size_bytes": file_size
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing financial document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing financial document: {str(e)}"
        )
    
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup file {file_path}: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Financial Document Analyzer API...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
