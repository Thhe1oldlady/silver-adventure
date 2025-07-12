#!/usr/bin/env python3
"""
Churn Service Test Script

This script tests the churn prediction service functionality, including
model training and prediction capabilities.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from silver_adventure.services.churn_service import ChurnService


async def test_churn_service():
    """Test the churn service functionality"""
    print("🚀 Testing Silver Adventure Churn Service")
    print("=" * 50)
    
    # Initialize service
    service = ChurnService()
    
    # Test health check
    print("\n1. Testing health check...")
    health = service.health_check()
    print(f"   ✅ Health check: {'PASS' if health else 'FAIL'}")
    
    # Test required features
    print("\n2. Testing required features...")
    features = service.get_required_features()
    print(f"   ✅ Required features ({len(features)}): {features[:5]}...")
    
    # Test sample data generation
    print("\n3. Testing sample data generation...")
    try:
        sample_data = service._generate_sample_data()
        print(f"   ✅ Sample data generated: {len(sample_data)} records")
        print(f"   📊 Churn rate: {sample_data['churn'].mean():.2%}")
    except Exception as e:
        print(f"   ❌ Sample data generation failed: {str(e)}")
    
    # Test model training
    print("\n4. Testing model training...")
    try:
        result = await service.train_model("random_forest")
        print(f"   ✅ Model training: {result['status']}")
        print(f"   📈 Accuracy: {result['accuracy']:.3f}")
        print(f"   📊 Precision: {result['precision']:.3f}")
        print(f"   📊 Recall: {result['recall']:.3f}")
        print(f"   📊 F1 Score: {result['f1_score']:.3f}")
    except Exception as e:
        print(f"   ❌ Model training failed: {str(e)}")
    
    # Test pipeline status
    print("\n5. Testing pipeline status...")
    try:
        status = service.get_pipeline_status()
        print(f"   ✅ Pipeline health: {status['pipeline_health']}")
        print(f"   📊 Models loaded: {status['models_loaded']}")
        print(f"   📋 Available models: {status['available_models']}")
    except Exception as e:
        print(f"   ❌ Pipeline status failed: {str(e)}")
    
    # Test churn prediction
    print("\n6. Testing churn prediction...")
    
    # Test cases with different risk levels
    test_cases = [
        {
            "name": "High Risk Customer",
            "customer_id": "HIGH_RISK_001",
            "features": {
                "tenure_months": 2,
                "monthly_charges": 95.0,
                "total_charges": 190.0,
                "contract_length": 1,
                "payment_method": "Electronic Check",
                "internet_service": "Fiber Optic",
                "online_security": "No",
                "online_backup": "No",
                "device_protection": "No",
                "tech_support": "No",
                "streaming_tv": "Yes",
                "streaming_movies": "Yes",
                "paperless_billing": "Yes",
                "senior_citizen": 1,
                "partner": "No",
                "dependents": "No",
                "phone_service": "Yes",
                "multiple_lines": "Yes"
            }
        },
        {
            "name": "Low Risk Customer",
            "customer_id": "LOW_RISK_001",
            "features": {
                "tenure_months": 48,
                "monthly_charges": 45.0,
                "total_charges": 2160.0,
                "contract_length": 24,
                "payment_method": "Credit Card",
                "internet_service": "DSL",
                "online_security": "Yes",
                "online_backup": "Yes",
                "device_protection": "Yes",
                "tech_support": "Yes",
                "streaming_tv": "No",
                "streaming_movies": "No",
                "paperless_billing": "No",
                "senior_citizen": 0,
                "partner": "Yes",
                "dependents": "Yes",
                "phone_service": "Yes",
                "multiple_lines": "No"
            }
        }
    ]
    
    for test_case in test_cases:
        try:
            result = await service.predict_churn(
                customer_id=test_case["customer_id"],
                features=test_case["features"]
            )
            
            print(f"\n   📊 {test_case['name']}:")
            print(f"       Customer ID: {result['customer_id']}")
            print(f"       Churn Probability: {result['churn_probability']:.3f}")
            print(f"       Risk Level: {result['risk_level']}")
            print(f"       Recommendations: {len(result['recommendations'])} items")
            
            # Display first few recommendations
            for i, rec in enumerate(result['recommendations'][:3]):
                print(f"         {i+1}. {rec}")
            
        except Exception as e:
            print(f"   ❌ Prediction failed for {test_case['name']}: {str(e)}")
    
    # Test prediction with missing features
    print("\n7. Testing prediction with missing features...")
    try:
        partial_features = {
            "tenure_months": 12,
            "monthly_charges": 75.0,
            "total_charges": 900.0
        }
        
        result = await service.predict_churn(
            customer_id="PARTIAL_FEATURES",
            features=partial_features
        )
        
        print(f"   ✅ Partial features prediction: {result['risk_level']}")
        print(f"   📊 Churn probability: {result['churn_probability']:.3f}")
        
    except Exception as e:
        print(f"   ❌ Partial features prediction failed: {str(e)}")
    
    # Test recommendation generation
    print("\n8. Testing recommendation generation...")
    test_features = {
        "monthly_charges": 85.0,
        "tenure_months": 3,
        "contract_length": 1,
        "tech_support": "No"
    }
    
    for risk_level in ["High", "Medium", "Low"]:
        recommendations = service._generate_recommendations(risk_level, test_features)
        print(f"   📋 {risk_level} risk recommendations: {len(recommendations)} items")
    
    print("\n" + "=" * 50)
    print("✨ Churn Service Test Complete!")
    print("🎯 Machine learning pipeline is ready for customer insights!")


if __name__ == "__main__":
    asyncio.run(test_churn_service())