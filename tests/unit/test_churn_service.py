"""
Unit tests for the Churn Service
"""

import pytest
import os
import pandas as pd
from unittest.mock import patch, MagicMock
from silver_adventure.services.churn_service import ChurnService


class TestChurnService:
    """Test cases for ChurnService"""
    
    def test_health_check(self, churn_service):
        """Test churn service health check"""
        assert churn_service.health_check() is True
    
    def test_get_required_features(self, churn_service):
        """Test getting required features for churn prediction"""
        features = churn_service.get_required_features()
        
        assert isinstance(features, list)
        assert len(features) > 0
        assert "tenure_months" in features
        assert "monthly_charges" in features
        assert "total_charges" in features
    
    def test_generate_sample_data(self, churn_service):
        """Test generating sample training data"""
        df = churn_service._generate_sample_data()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert "customer_id" in df.columns
        assert "churn" in df.columns
        
        # Check that required features are present
        required_features = churn_service.get_required_features()
        for feature in required_features:
            assert feature in df.columns
        
        # Check data types and ranges
        assert df["tenure_months"].min() >= 1
        assert df["tenure_months"].max() <= 72
        assert df["monthly_charges"].min() > 0
        assert df["churn"].isin([0, 1]).all()
    
    def test_preprocess_data(self, churn_service):
        """Test data preprocessing"""
        # Create sample data
        sample_data = pd.DataFrame({
            "tenure_months": [12, 24, 6],
            "monthly_charges": [50.0, 75.0, 100.0],
            "total_charges": [600.0, 1800.0, 600.0],
            "contract_length": [12, 24, 1],
            "payment_method": ["Credit Card", "Bank Transfer", "Electronic Check"],
            "internet_service": ["DSL", "Fiber Optic", "No"],
            "online_security": ["Yes", "No", "Yes"],
            "online_backup": ["No", "Yes", "No"],
            "device_protection": ["Yes", "No", "Yes"],
            "tech_support": ["No", "Yes", "No"],
            "streaming_tv": ["Yes", "No", "Yes"],
            "streaming_movies": ["No", "Yes", "No"],
            "paperless_billing": ["Yes", "No", "Yes"],
            "senior_citizen": [0, 1, 0],
            "partner": ["Yes", "No", "Yes"],
            "dependents": ["No", "Yes", "No"],
            "phone_service": ["Yes", "Yes", "No"],
            "multiple_lines": ["No", "Yes", "No"]
        })
        
        # Test preprocessing with fitting
        processed_data = churn_service._preprocess_data(sample_data, "test_model", fit_preprocessors=True)
        
        assert isinstance(processed_data, pd.DataFrame)
        assert len(processed_data) == len(sample_data)
        
        # Check that categorical columns are encoded
        categorical_cols = ["payment_method", "internet_service", "online_security"]
        for col in categorical_cols:
            if col in processed_data.columns:
                assert processed_data[col].dtype in ['int64', 'int32']
        
        # Test preprocessing without fitting (using existing preprocessors)
        processed_data2 = churn_service._preprocess_data(sample_data, "test_model", fit_preprocessors=False)
        assert isinstance(processed_data2, pd.DataFrame)
    
    @pytest.mark.asyncio
    async def test_train_model(self, churn_service):
        """Test model training"""
        # This might take a while, so we'll test with a smaller dataset
        result = await churn_service.train_model("random_forest")
        
        assert isinstance(result, dict)
        assert "model_id" in result
        assert "accuracy" in result
        assert "status" in result
        assert result["status"] == "trained"
        assert 0 <= result["accuracy"] <= 1
    
    @pytest.mark.asyncio
    async def test_predict_churn(self, churn_service, sample_customer_data):
        """Test churn prediction"""
        # Extract features from sample data
        features = {k: v for k, v in sample_customer_data.items() 
                   if k in churn_service.get_required_features()}
        
        result = await churn_service.predict_churn(
            customer_id=sample_customer_data["customer_id"],
            features=features
        )
        
        assert isinstance(result, dict)
        assert "customer_id" in result
        assert "churn_probability" in result
        assert "risk_level" in result
        assert "recommendations" in result
        
        assert result["customer_id"] == sample_customer_data["customer_id"]
        assert 0 <= result["churn_probability"] <= 1
        assert result["risk_level"] in ["Low", "Medium", "High"]
        assert isinstance(result["recommendations"], list)
        assert len(result["recommendations"]) > 0
    
    def test_generate_recommendations(self, churn_service, sample_customer_data):
        """Test recommendation generation"""
        # Test high risk recommendations
        high_risk_recommendations = churn_service._generate_recommendations("High", sample_customer_data)
        assert isinstance(high_risk_recommendations, list)
        assert len(high_risk_recommendations) > 0
        assert any("immediate" in rec.lower() for rec in high_risk_recommendations)
        
        # Test medium risk recommendations
        medium_risk_recommendations = churn_service._generate_recommendations("Medium", sample_customer_data)
        assert isinstance(medium_risk_recommendations, list)
        assert len(medium_risk_recommendations) > 0
        assert any("proactive" in rec.lower() for rec in medium_risk_recommendations)
        
        # Test low risk recommendations
        low_risk_recommendations = churn_service._generate_recommendations("Low", sample_customer_data)
        assert isinstance(low_risk_recommendations, list)
        assert len(low_risk_recommendations) > 0
        assert any("continue" in rec.lower() for rec in low_risk_recommendations)
    
    def test_get_pipeline_status(self, churn_service):
        """Test getting pipeline status"""
        status = churn_service.get_pipeline_status()
        
        assert isinstance(status, dict)
        assert "pipeline_health" in status
        assert "models_loaded" in status
        assert "available_models" in status
        assert "last_update" in status
        
        assert isinstance(status["models_loaded"], int)
        assert isinstance(status["available_models"], list)
        assert status["pipeline_health"] in ["healthy", "degraded", "error"]
    
    def test_model_configuration(self, churn_service):
        """Test model configuration"""
        assert "random_forest" in churn_service.model_config
        assert "gradient_boosting" in churn_service.model_config
        
        # Check random forest config
        rf_config = churn_service.model_config["random_forest"]
        assert "n_estimators" in rf_config
        assert "max_depth" in rf_config
        assert "random_state" in rf_config
        
        # Check gradient boosting config
        gb_config = churn_service.model_config["gradient_boosting"]
        assert "n_estimators" in gb_config
        assert "learning_rate" in gb_config
        assert "random_state" in gb_config
    
    def test_feature_requirements(self, churn_service):
        """Test that required features are properly defined"""
        features = churn_service.get_required_features()
        
        # Check that essential features are included
        essential_features = ["tenure_months", "monthly_charges", "total_charges"]
        for feature in essential_features:
            assert feature in features
        
        # Check that features are strings
        for feature in features:
            assert isinstance(feature, str)
            assert len(feature) > 0
    
    @pytest.mark.asyncio
    async def test_predict_with_missing_features(self, churn_service):
        """Test prediction with missing features"""
        # Provide only partial features
        partial_features = {
            "tenure_months": 12,
            "monthly_charges": 75.0,
            "total_charges": 900.0
        }
        
        result = await churn_service.predict_churn(
            customer_id="TEST_PARTIAL",
            features=partial_features
        )
        
        assert isinstance(result, dict)
        assert "customer_id" in result
        assert "churn_probability" in result
        assert "risk_level" in result
        assert result["customer_id"] == "TEST_PARTIAL"