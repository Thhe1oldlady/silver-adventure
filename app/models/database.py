"""
Database models.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.sql import func
from datetime import datetime

from app.db.session import Base


class Customer(Base):
    """
    Customer model.
    """
    __tablename__ = "customers"
    
    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20))
    age = Column(Integer)
    tenure = Column(Integer)  # months
    monthly_charges = Column(Float)
    total_charges = Column(Float)
    contract_type = Column(String(50))
    payment_method = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChurnPrediction(Base):
    """
    Churn prediction model.
    """
    __tablename__ = "churn_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(50), index=True, nullable=False)
    churn_probability = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)
    factors = Column(Text)  # JSON string
    model_version = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ProcessingJob(Base):
    """
    Processing job model.
    """
    __tablename__ = "processing_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(100), unique=True, index=True)
    job_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    input_data = Column(Text)  # JSON string
    output_data = Column(Text)  # JSON string
    error_message = Column(Text)
    processing_time = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))


class ApiLog(Base):
    """
    API log model.
    """
    __tablename__ = "api_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(100), index=True)
    method = Column(String(10), nullable=False)
    endpoint = Column(String(200), nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time = Column(Float)
    client_ip = Column(String(45))
    user_agent = Column(String(500))
    request_size = Column(Integer)
    response_size = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())