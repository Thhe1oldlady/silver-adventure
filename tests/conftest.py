"""
Test configuration and fixtures
"""

import asyncio
import os
import sys
from pathlib import Path

import pytest

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from silver_adventure.services.churn_service import ChurnService
from silver_adventure.services.email_service import EmailService


@pytest.fixture
def email_service():
    """Create an email service instance for testing"""
    return EmailService()


@pytest.fixture
def churn_service():
    """Create a churn service instance for testing"""
    return ChurnService()


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing"""
    return {
        "customer_id": "TEST_001",
        "tenure_months": 12,
        "monthly_charges": 75.0,
        "total_charges": 900.0,
        "contract_length": 12,
        "payment_method": "Credit Card",
        "internet_service": "Fiber Optic",
        "online_security": "Yes",
        "online_backup": "No",
        "device_protection": "Yes",
        "tech_support": "No",
        "streaming_tv": "Yes",
        "streaming_movies": "Yes",
        "paperless_billing": "Yes",
        "senior_citizen": 0,
        "partner": "Yes",
        "dependents": "No",
        "phone_service": "Yes",
        "multiple_lines": "No",
    }


@pytest.fixture
def sample_email_context():
    """Sample email context for testing"""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "company": "Test Company",
        "custom_message": "This is a test message",
    }


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
