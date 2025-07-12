"""Sample script demonstrating API client usage."""

import asyncio
import httpx
import json
from typing import Dict, Any

# API base URL
API_BASE_URL = "http://localhost:8000/api/v1"

async def main():
    """Main function demonstrating API usage."""
    print("Silver Adventure - API Client Sample")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Health check
        await check_health(client)
        
        # List pipelines
        await list_pipelines(client)
        
        # Execute pipeline
        await execute_pipeline(client)
        
        # Churn prediction
        await churn_prediction(client)
        
        # Batch churn prediction
        await batch_churn_prediction(client)
        
        # Get metrics
        await get_metrics(client)


async def check_health(client: httpx.AsyncClient):
    """Check API health."""
    print("\n1. Health Check")
    print("-" * 20)
    
    try:
        response = await client.get(f"{API_BASE_URL}/../health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✓ API is healthy")
            print(f"  Version: {health_data.get('version', 'unknown')}")
            print(f"  Uptime: {health_data.get('uptime', 0):.2f}s")
        else:
            print(f"✗ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Health check failed: {str(e)}")


async def list_pipelines(client: httpx.AsyncClient):
    """List available pipelines."""
    print("\n2. List Pipelines")
    print("-" * 20)
    
    try:
        response = await client.get(f"{API_BASE_URL}/pipelines/list")
        if response.status_code == 200:
            data = response.json()
            pipelines = data.get('pipelines', [])
            print(f"✓ Found {len(pipelines)} pipelines:")
            for pipeline in pipelines:
                print(f"  - {pipeline}")
        else:
            print(f"✗ Failed to list pipelines: {response.status_code}")
    except Exception as e:
        print(f"✗ Failed to list pipelines: {str(e)}")


async def execute_pipeline(client: httpx.AsyncClient):
    """Execute a pipeline."""
    print("\n3. Execute Pipeline")
    print("-" * 20)
    
    # Sample data
    sample_data = {
        "customers": [
            {"id": 1, "name": "John Doe", "age": 30},
            {"id": 2, "name": "Jane Smith", "age": 25},
            {"id": 3, "name": "Bob Johnson", "age": 35}
        ]
    }
    
    request_data = {
        "pipeline_name": "data_processing",
        "data": sample_data,
        "config": {"batch_size": 100},
        "async_execution": False
    }
    
    try:
        response = await client.post(f"{API_BASE_URL}/pipelines/execute", json=request_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Pipeline executed successfully")
            print(f"  Execution ID: {result.get('execution_id')}")
            print(f"  Status: {result.get('status')}")
            print(f"  Duration: {result.get('duration', 0):.2f}s")
            
            if result.get('errors'):
                print(f"  Errors: {result.get('errors')}")
        else:
            print(f"✗ Pipeline execution failed: {response.status_code}")
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ Pipeline execution failed: {str(e)}")


async def churn_prediction(client: httpx.AsyncClient):
    """Make churn prediction."""
    print("\n4. Churn Prediction")
    print("-" * 20)
    
    # Sample customer data
    customer_data = {
        "customer_id": "CUST_001",
        "features": {
            "tenure": 12,
            "monthly_charges": 79.99,
            "total_charges": 959.88,
            "contract_type": "Month-to-month",
            "payment_method": "Credit card",
            "internet_service": "Fiber optic",
            "phone_service": "Yes"
        },
        "model_version": "v1.0"
    }
    
    try:
        response = await client.post(f"{API_BASE_URL}/ml/churn/predict", json=customer_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Churn prediction successful")
            print(f"  Customer: {result.get('customer_id')}")
            print(f"  Churn Probability: {result.get('churn_probability', 0):.3f}")
            print(f"  Churn Prediction: {result.get('churn_prediction')}")
            print(f"  Risk Level: {result.get('risk_level')}")
        else:
            print(f"✗ Churn prediction failed: {response.status_code}")
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ Churn prediction failed: {str(e)}")


async def batch_churn_prediction(client: httpx.AsyncClient):
    """Make batch churn prediction."""
    print("\n5. Batch Churn Prediction")
    print("-" * 20)
    
    # Sample batch data
    batch_data = {
        "customers": [
            {
                "customer_id": "CUST_001",
                "tenure": 12,
                "monthly_charges": 79.99,
                "total_charges": 959.88,
                "contract_type": "Month-to-month",
                "payment_method": "Credit card",
                "internet_service": "Fiber optic",
                "phone_service": "Yes"
            },
            {
                "customer_id": "CUST_002",
                "tenure": 24,
                "monthly_charges": 45.50,
                "total_charges": 1092.00,
                "contract_type": "One year",
                "payment_method": "Bank transfer",
                "internet_service": "DSL",
                "phone_service": "No"
            }
        ],
        "model_version": "v1.0",
        "return_probabilities": True
    }
    
    try:
        response = await client.post(f"{API_BASE_URL}/ml/churn/predict/batch", json=batch_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Batch prediction successful")
            print(f"  Batch ID: {result.get('batch_id')}")
            print(f"  Processed: {result.get('processed_count')} customers")
            print(f"  Errors: {result.get('error_count')}")
            
            predictions = result.get('predictions', [])
            print(f"  Predictions:")
            for pred in predictions:
                print(f"    {pred.get('customer_id')}: {pred.get('churn_probability', 0):.3f} ({pred.get('risk_level')})")
        else:
            print(f"✗ Batch prediction failed: {response.status_code}")
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ Batch prediction failed: {str(e)}")


async def get_metrics(client: httpx.AsyncClient):
    """Get system metrics."""
    print("\n6. System Metrics")
    print("-" * 20)
    
    try:
        response = await client.get(f"{API_BASE_URL}/monitoring/metrics")
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Metrics retrieved successfully")
            print(f"  Timestamp: {result.get('timestamp')}")
            
            metrics = result.get('metrics', {})
            print(f"  Metrics:")
            for metric, value in metrics.items():
                print(f"    {metric}: {value}")
        else:
            print(f"✗ Failed to get metrics: {response.status_code}")
    except Exception as e:
        print(f"✗ Failed to get metrics: {str(e)}")


if __name__ == "__main__":
    print("Starting API client sample...")
    print("Note: Make sure the Silver Adventure API server is running on localhost:8000")
    print("You can start it with: python -m silver_adventure.cli server")
    print()
    
    asyncio.run(main())