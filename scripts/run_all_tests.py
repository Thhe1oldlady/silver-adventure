#!/usr/bin/env python3
"""
Complete System Test Runner

This script runs comprehensive tests for the Silver Adventure application,
including all services, API endpoints, and integration tests.
"""

import sys
import os
import asyncio
import subprocess
from pathlib import Path
import time
import requests
import json

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from silver_adventure.services.email_service import EmailService
from silver_adventure.services.churn_service import ChurnService


def run_command(cmd, description, timeout=60):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=project_root
        )
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            if result.stdout:
                print(f"Output: {result.stdout[:500]}...")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {str(e)}")
        return False


def test_api_endpoints():
    """Test API endpoints"""
    print(f"\n{'='*60}")
    print("🌐 Testing API Endpoints")
    print(f"{'='*60}")
    
    base_url = "http://localhost:8000"
    
    # Test endpoints
    endpoints = [
        {"url": "/health", "method": "GET", "description": "Health Check"},
        {"url": "/api/v1/email/templates", "method": "GET", "description": "Email Templates"},
        {"url": "/api/v1/predict/churn/features", "method": "GET", "description": "Churn Features"},
        {"url": "/docs", "method": "GET", "description": "API Documentation"},
        {"url": "/redoc", "method": "GET", "description": "ReDoc Documentation"}
    ]
    
    success_count = 0
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint['url']}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {endpoint['description']} - PASSED")
                success_count += 1
            else:
                print(f"❌ {endpoint['description']} - FAILED (Status: {response.status_code})")
        except Exception as e:
            print(f"💥 {endpoint['description']} - ERROR: {str(e)}")
    
    # Test POST endpoints
    post_tests = [
        {
            "url": "/api/v1/email/send",
            "data": {
                "to_email": "test@example.com",
                "template": "welcome",
                "context": {"name": "Test User"}
            },
            "description": "Send Email"
        },
        {
            "url": "/api/v1/predict/churn",
            "data": {
                "customer_id": "TEST_001",
                "features": {
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
                    "multiple_lines": "No"
                }
            },
            "description": "Churn Prediction"
        }
    ]
    
    for test in post_tests:
        try:
            response = requests.post(
                f"{base_url}{test['url']}", 
                json=test['data'], 
                timeout=30
            )
            if response.status_code == 200:
                print(f"✅ {test['description']} - PASSED")
                success_count += 1
            else:
                print(f"❌ {test['description']} - FAILED (Status: {response.status_code})")
        except Exception as e:
            print(f"💥 {test['description']} - ERROR: {str(e)}")
    
    total_tests = len(endpoints) + len(post_tests)
    print(f"\n📊 API Tests: {success_count}/{total_tests} passed")
    return success_count == total_tests


async def test_services():
    """Test all services"""
    print(f"\n{'='*60}")
    print("🔧 Testing Services")
    print(f"{'='*60}")
    
    success_count = 0
    total_tests = 0
    
    # Test Email Service
    print("\n📧 Testing Email Service...")
    try:
        email_service = EmailService()
        
        # Health check
        if email_service.health_check():
            print("✅ Email Service Health Check - PASSED")
            success_count += 1
        else:
            print("❌ Email Service Health Check - FAILED")
        total_tests += 1
        
        # Templates
        templates = email_service.get_available_templates()
        if len(templates) == 6:
            print(f"✅ Email Templates ({len(templates)}) - PASSED")
            success_count += 1
        else:
            print(f"❌ Email Templates ({len(templates)}) - FAILED")
        total_tests += 1
        
        # Template generation
        test_passed = True
        for template in templates:
            try:
                content = email_service._generate_golden_mood_content(template, {"name": "Test"})
                if not (content.get("html") and content.get("text") and content.get("subject")):
                    test_passed = False
                    break
            except Exception as e:
                print(f"Template {template} failed: {str(e)}")
                test_passed = False
                break
        
        if test_passed:
            print("✅ Email Template Generation - PASSED")
            success_count += 1
        else:
            print("❌ Email Template Generation - FAILED")
        total_tests += 1
        
        # Email sending (development mode)
        result = await email_service.send_golden_mood_email(
            to_email="test@example.com",
            template="welcome",
            context={"name": "Test User"}
        )
        
        if result.get("email_id") and result.get("status"):
            print("✅ Email Sending - PASSED")
            success_count += 1
        else:
            print("❌ Email Sending - FAILED")
        total_tests += 1
        
    except Exception as e:
        print(f"💥 Email Service - ERROR: {str(e)}")
        total_tests += 4
    
    # Test Churn Service
    print("\n🤖 Testing Churn Service...")
    try:
        churn_service = ChurnService()
        
        # Health check
        if churn_service.health_check():
            print("✅ Churn Service Health Check - PASSED")
            success_count += 1
        else:
            print("❌ Churn Service Health Check - FAILED")
        total_tests += 1
        
        # Features
        features = churn_service.get_required_features()
        if len(features) == 18:
            print(f"✅ Churn Features ({len(features)}) - PASSED")
            success_count += 1
        else:
            print(f"❌ Churn Features ({len(features)}) - FAILED")
        total_tests += 1
        
        # Model training
        train_result = await churn_service.train_model()
        if train_result.get("status") == "trained" and train_result.get("accuracy", 0) > 0.5:
            print(f"✅ Model Training (Accuracy: {train_result['accuracy']:.3f}) - PASSED")
            success_count += 1
        else:
            print(f"❌ Model Training - FAILED")
        total_tests += 1
        
        # Prediction
        prediction = await churn_service.predict_churn(
            customer_id="TEST_001",
            features={
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
                "multiple_lines": "No"
            }
        )
        
        if (prediction.get("customer_id") and 
            0 <= prediction.get("churn_probability", -1) <= 1 and
            prediction.get("risk_level") in ["Low", "Medium", "High"]):
            print("✅ Churn Prediction - PASSED")
            success_count += 1
        else:
            print("❌ Churn Prediction - FAILED")
        total_tests += 1
        
    except Exception as e:
        print(f"💥 Churn Service - ERROR: {str(e)}")
        total_tests += 4
    
    print(f"\n📊 Service Tests: {success_count}/{total_tests} passed")
    return success_count == total_tests


def main():
    """Run all tests"""
    print("🚀 Silver Adventure - Complete System Test")
    print("=" * 80)
    
    start_time = time.time()
    
    # Test results
    results = {
        "code_quality": False,
        "unit_tests": False,
        "integration_tests": False,
        "services": False,
        "api_endpoints": False
    }
    
    # 1. Code Quality Checks
    print("\n🔍 Running Code Quality Checks...")
    results["code_quality"] = all([
        run_command("python -m black --check src/ tests/", "Code Formatting Check"),
        run_command("python -m isort --check-only src/ tests/", "Import Sorting Check"),
        run_command("python -m flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503", "Linting Check")
    ])
    
    # 2. Unit Tests
    print("\n🧪 Running Unit Tests...")
    results["unit_tests"] = run_command("python -m pytest tests/unit/ -v", "Unit Tests", timeout=120)
    
    # 3. Integration Tests
    print("\n🔗 Running Integration Tests...")
    results["integration_tests"] = run_command("python -m pytest tests/integration/ -v", "Integration Tests", timeout=120)
    
    # 4. Service Tests
    print("\n🛠️ Running Service Tests...")
    try:
        results["services"] = asyncio.run(test_services())
    except Exception as e:
        print(f"💥 Service Tests - ERROR: {str(e)}")
        results["services"] = False
    
    # 5. API Endpoint Tests (requires server to be running)
    print("\n🌐 Testing API Endpoints...")
    print("Note: This requires the server to be running on localhost:8000")
    try:
        results["api_endpoints"] = test_api_endpoints()
    except Exception as e:
        print(f"💥 API Tests - ERROR: {str(e)}")
        results["api_endpoints"] = False
    
    # Summary
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}")
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n📈 Overall Result: {passed_tests}/{total_tests} test suites passed")
    print(f"⏱️ Total Duration: {duration:.2f} seconds")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Silver Adventure is ready for deployment! 🚀")
        return 0
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test suite(s) failed. Please review and fix issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())