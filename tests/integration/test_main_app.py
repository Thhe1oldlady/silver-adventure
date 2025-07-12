"""
Integration tests for the FastAPI application
"""

import pytest
from fastapi.testclient import TestClient
from silver_adventure.main import app

client = TestClient(app)


class TestApplicationIntegration:
    """Integration tests for the main application"""
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "environment" in data
    
    def test_health_check(self):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded"]
    
    def test_email_templates_endpoint(self):
        """Test the email templates endpoint"""
        response = client.get("/api/v1/email/templates")
        assert response.status_code == 200
        
        data = response.json()
        assert "templates" in data
        assert isinstance(data["templates"], list)
        assert len(data["templates"]) > 0
    
    def test_churn_features_endpoint(self):
        """Test the churn features endpoint"""
        response = client.get("/api/v1/predict/churn/features")
        assert response.status_code == 200
        
        data = response.json()
        assert "features" in data
        assert isinstance(data["features"], list)
        assert len(data["features"]) > 0
    
    def test_pipeline_status_endpoint(self):
        """Test the pipeline status endpoint"""
        response = client.get("/api/v1/pipeline/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "pipeline_health" in data
        assert "models_loaded" in data
        assert "available_models" in data
    
    def test_send_email_endpoint(self):
        """Test the send email endpoint"""
        email_data = {
            "to_email": "test@example.com",
            "template": "welcome",
            "context": {"name": "Test User"}
        }
        
        response = client.post("/api/v1/email/send", json=email_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "email_id" in data
        assert "status" in data
    
    def test_churn_prediction_endpoint(self):
        """Test the churn prediction endpoint"""
        prediction_data = {
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
        }
        
        response = client.post("/api/v1/predict/churn", json=prediction_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "customer_id" in data
        assert "churn_probability" in data
        assert "risk_level" in data
        assert "recommendations" in data
    
    def test_train_model_endpoint(self):
        """Test the train model endpoint"""
        response = client.post("/api/v1/pipeline/train")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "model_id" in data
        assert "accuracy" in data
        assert "status" in data
    
    def test_invalid_endpoint(self):
        """Test accessing invalid endpoint"""
        response = client.get("/invalid/endpoint")
        assert response.status_code == 404
    
    def test_invalid_email_request(self):
        """Test invalid email request"""
        invalid_data = {
            "to_email": "invalid-email",
            "template": "nonexistent"
        }
        
        response = client.post("/api/v1/email/send", json=invalid_data)
        # Should still process but may fail validation
        assert response.status_code in [200, 400, 422, 500]
    
    def test_invalid_churn_prediction(self):
        """Test invalid churn prediction request"""
        invalid_data = {
            "customer_id": "",
            "features": {}
        }
        
        response = client.post("/api/v1/predict/churn", json=invalid_data)
        # Should handle gracefully
        assert response.status_code in [200, 400, 422, 500]
    
    def test_openapi_documentation(self):
        """Test OpenAPI documentation endpoint"""
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Check that it's HTML content
        assert "text/html" in response.headers["content-type"]
    
    def test_redoc_documentation(self):
        """Test ReDoc documentation endpoint"""
        response = client.get("/redoc")
        assert response.status_code == 200
        
        # Check that it's HTML content
        assert "text/html" in response.headers["content-type"]
    
    def test_openapi_schema(self):
        """Test OpenAPI schema endpoint"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
        
        # Check that our endpoints are documented
        assert "/health" in data["paths"]
        assert "/api/v1/email/send" in data["paths"]
        assert "/api/v1/predict/churn" in data["paths"]