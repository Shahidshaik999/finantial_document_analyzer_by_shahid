"""
Database models and configuration for Financial Document Analyzer.
Supports SQLite for lightweight deployment and PostgreSQL for production.
"""

import os
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./financial_analyzer.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class AnalysisRequest(Base):
    """Model for tracking analysis requests"""
    __tablename__ = "analysis_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(36), unique=True, index=True, nullable=False)
    filename = Column(String(255), nullable=False)
    file_size_bytes = Column(Integer)
    query = Column(Text, nullable=False)
    status = Column(String(50), default="pending", index=True)  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<AnalysisRequest(id={self.id}, request_id={self.request_id}, status={self.status})>"


class AnalysisResult(Base):
    """Model for storing analysis results"""
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(36), unique=True, index=True, nullable=False)
    analysis_text = Column(Text, nullable=False)
    processing_time_seconds = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, request_id={self.request_id})>"


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    # Initialize database when run directly
    print(f"Initializing database: {DATABASE_URL}")
    init_db()
    print("Database initialized successfully!")
