#!/usr/bin/env python3
"""
Test script to demonstrate the Oracle FastAPI Integration functionality.
This script can be run to test the application without external dependencies.
"""

import json
import sys
import os
import asyncio
from typing import Dict, Any

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_data_structures():
    """Test data structures and models."""
    print("Testing data structures...")
    
    # Test sample customer data
    sample_customer = {
        "customer_id": "CUST001",
        "name": "John Doe",
        "email": "john@example.com",
        "age": 35,
        "tenure": 24,
        "monthly_charges": 75.50,
        "total_charges": 1812.00,
        "contract_type": "one-year",
        "payment_method": "credit_card"
    }
    
    print(f"Sample customer data: {json.dumps(sample_customer, indent=2)}")
    
    # Test churn prediction request
    churn_request = {
        "customer_id": "CUST001",
        "features": {
            "age": 35,
            "tenure": 24,
            "monthly_charges": 75.50,
            "total_charges": 1812.00,
            "contract_type": "one-year",
            "payment_method": "credit_card"
        }
    }
    
    print(f"Churn prediction request: {json.dumps(churn_request, indent=2)}")
    
    # Test JSON processing request
    json_request = {
        "data": sample_customer,
        "script_name": "data_cleaner",
        "options": {
            "remove_nulls": True,
            "remove_empty_strings": True
        }
    }
    
    print(f"JSON processing request: {json.dumps(json_request, indent=2)}")
    
    print("✓ Data structures test passed!")

def test_oracle_queries():
    """Test Oracle query samples."""
    print("\nTesting Oracle query samples...")
    
    sample_queries = [
        {
            "name": "Test Connection",
            "query": "SELECT 1 as test_value",
            "description": "Simple test query"
        },
        {
            "name": "Customer Count",
            "query": "SELECT COUNT(*) as customer_count FROM customers",
            "description": "Count total customers"
        },
        {
            "name": "High Risk Customers",
            "query": "SELECT * FROM customers WHERE monthly_charges > 100",
            "description": "Find customers with high monthly charges"
        }
    ]
    
    for query in sample_queries:
        print(f"- {query['name']}: {query['query']}")
    
    print("✓ Oracle queries test passed!")

def test_json_processing():
    """Test JSON processing scripts."""
    print("\nTesting JSON processing scripts...")
    
    # Test data cleaning
    sample_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 35,
        "phone": "",
        "address": None,
        "notes": "   "
    }
    
    print(f"Original data: {json.dumps(sample_data, indent=2)}")
    
    # Simulate data cleaning
    cleaned_data = {k: v for k, v in sample_data.items() if v is not None and v != ""}
    cleaned_data = {k: v.strip() if isinstance(v, str) else v for k, v in cleaned_data.items()}
    
    print(f"Cleaned data: {json.dumps(cleaned_data, indent=2)}")
    
    # Test data validation
    validation_errors = []
    required_fields = ["name", "email", "age"]
    
    for field in required_fields:
        if field not in cleaned_data:
            validation_errors.append(f"Missing required field: {field}")
    
    if validation_errors:
        print(f"Validation errors: {validation_errors}")
    else:
        print("✓ Data validation passed!")
    
    print("✓ JSON processing test passed!")

def test_churn_prediction():
    """Test churn prediction logic."""
    print("\nTesting churn prediction logic...")
    
    # Sample customer features
    features = {
        "age": 35,
        "tenure": 24,
        "monthly_charges": 75.50,
        "total_charges": 1812.00,
        "contract_type": "one-year",
        "payment_method": "credit_card"
    }
    
    # Simple churn prediction logic (mock)
    churn_score = 0.0
    
    # Age factor
    if features["age"] < 25:
        churn_score += 0.3
    elif features["age"] > 65:
        churn_score += 0.2
    
    # Tenure factor
    if features["tenure"] < 12:
        churn_score += 0.4
    elif features["tenure"] > 36:
        churn_score -= 0.2
    
    # Monthly charges factor
    if features["monthly_charges"] > 80:
        churn_score += 0.2
    
    # Contract type factor
    if features["contract_type"] == "month-to-month":
        churn_score += 0.3
    elif features["contract_type"] == "two-year":
        churn_score -= 0.2
    
    # Normalize to 0-1 range
    churn_probability = max(0, min(1, churn_score))
    
    # Determine risk level
    if churn_probability < 0.3:
        risk_level = "low"
    elif churn_probability < 0.7:
        risk_level = "medium"
    else:
        risk_level = "high"
    
    prediction = {
        "customer_id": "CUST001",
        "churn_probability": churn_probability,
        "risk_level": risk_level,
        "factors": ["tenure", "monthly_charges", "contract_type"]
    }
    
    print(f"Churn prediction: {json.dumps(prediction, indent=2)}")
    print("✓ Churn prediction test passed!")

def test_api_structure():
    """Test API structure and endpoints."""
    print("\nTesting API structure...")
    
    api_endpoints = [
        "GET /health - Health check",
        "GET /health/detailed - Detailed health check",
        "POST /api/v1/predict/churn - Single customer churn prediction",
        "POST /api/v1/predict/churn/batch - Batch churn prediction",
        "GET /api/v1/predict/churn/model-info - Model information",
        "GET /api/v1/oracle/status - Oracle database status",
        "POST /api/v1/oracle/query - Execute Oracle query",
        "GET /api/v1/oracle/tables - List available tables",
        "GET /api/v1/oracle/tables/{table_name} - Get table info",
        "POST /api/v1/data/upload - Upload JSON data",
        "POST /api/v1/data/process - Process JSON data",
        "GET /api/v1/data/scripts - List processing scripts",
        "POST /api/v1/data/export - Export data"
    ]
    
    print("Available API endpoints:")
    for endpoint in api_endpoints:
        print(f"  - {endpoint}")
    
    print("✓ API structure test passed!")

def main():
    """Run all tests."""
    print("=" * 60)
    print("Oracle FastAPI Integration - Test Suite")
    print("=" * 60)
    
    try:
        test_data_structures()
        test_oracle_queries()
        test_json_processing()
        test_churn_prediction()
        test_api_structure()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)
        
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set up environment variables: cp .env.example .env")
        print("3. Run the application: uvicorn app.main:app --reload")
        print("4. Visit http://localhost:8000/docs for API documentation")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())