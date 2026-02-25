## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

from crewai_tools import SerperDevTool
from pypdf import PdfReader

## Creating search tool
search_tool = SerperDevTool()

## Creating custom pdf reader tool as a simple function
def read_financial_document(path: str = 'data/sample.pdf', max_chars: int = 30000) -> str:
    """Read and extract text content from a financial PDF document.
    
    Args:
        path: Path to the PDF file to read
        max_chars: Maximum characters to extract (to avoid token limits)
        
    Returns:
        Extracted text content from the PDF (truncated if needed)
    """
    try:
        if not os.path.exists(path):
            return f"Error: File not found at {path}"
        
        reader = PdfReader(path)
        full_report = ""
        
        for page in reader.pages:
            content = page.extract_text()
            if content:
                # Remove excessive whitespace
                content = content.replace("\n\n", "\n")
                full_report += content + "\n"
            
            # Stop if we've reached the character limit
            if len(full_report) >= max_chars:
                break
        
        # Truncate if needed and add notice
        if len(full_report) > max_chars:
            full_report = full_report[:max_chars]
            full_report += "\n\n[Note: Document truncated to fit token limits. Analysis based on first portion of document.]"
        
        return full_report if full_report else "Error: No text content extracted from PDF"
    
    except Exception as e:
        return f"Error reading PDF: {str(e)}"
