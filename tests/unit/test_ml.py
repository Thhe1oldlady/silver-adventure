"""Unit tests for ML models."""

import pytest
import pandas as pd
import numpy as np
from silver_adventure.ml.churn_prediction import ChurnPredictor
from silver_adventure.ml.models import BaseModel, ModelRegistry


class TestChurnPredictor:
    """Test ChurnPredictor functionality."""
    
    def test_predictor_initialization(self):
        """Test predictor initialization."""
        predictor = ChurnPredictor()
        
        assert predictor.name == "churn_predictor"
        assert predictor.version == "v1.0"
        assert predictor.threshold == 0.5
        assert predictor.model is not None
    
    def test_feature_preprocessing(self):
        """Test feature preprocessing."""
        predictor = ChurnPredictor()
        
        # Test with dictionary input
        sample_data = {
            'tenure': 12,
            'monthly_charges': 79.99,
            'total_charges': 959.88,
            'contract_type': 'Month-to-month',
            'payment_method': 'Credit card',
            'internet_service': 'Fiber optic',
            'phone_service': 'Yes'
        }
        
        processed = predictor.preprocess_features(sample_data)
        
        assert processed is not None
        assert processed.shape[1] == 7  # Expected number of features
        assert processed.shape[0] == 1   # Single sample
    
    def test_single_prediction(self):
        """Test single customer prediction."""
        predictor = ChurnPredictor()
        
        customer_data = {
            'customer_id': 'CUST_001',
            'tenure': 12,
            'monthly_charges': 79.99,
            'total_charges': 959.88,
            'contract_type': 'Month-to-month',
            'payment_method': 'Credit card',
            'internet_service': 'Fiber optic',
            'phone_service': 'Yes'
        }
        
        prediction = predictor.predict_single(customer_data)
        
        assert 'churn_probability' in prediction
        assert 'churn_prediction' in prediction
        assert 'model_version' in prediction
        assert 'feature_importance' in prediction
        
        # Validate probability range
        prob = prediction['churn_probability']
        assert 0 <= prob <= 1
        
        # Validate prediction type
        assert isinstance(prediction['churn_prediction'], bool)
    
    def test_batch_prediction(self):
        """Test batch prediction."""
        predictor = ChurnPredictor()
        
        customers = [
            {
                'customer_id': 'CUST_001',
                'tenure': 12,
                'monthly_charges': 79.99,
                'total_charges': 959.88,
                'contract_type': 'Month-to-month',
                'payment_method': 'Credit card',
                'internet_service': 'Fiber optic',
                'phone_service': 'Yes'
            },
            {
                'customer_id': 'CUST_002',
                'tenure': 24,
                'monthly_charges': 45.50,
                'total_charges': 1092.00,
                'contract_type': 'One year',
                'payment_method': 'Bank transfer',
                'internet_service': 'DSL',
                'phone_service': 'No'
            }
        ]
        
        predictions = predictor.predict_batch(customers)
        
        assert len(predictions) == 2
        
        for pred in predictions:
            assert 'churn_probability' in pred
            assert 'churn_prediction' in pred
            assert 'model_version' in pred
            assert 0 <= pred['churn_probability'] <= 1
            assert isinstance(pred['churn_prediction'], bool)
    
    def test_model_training(self, training_data):
        """Test model training."""
        predictor = ChurnPredictor()
        X, y = training_data
        
        # Train model
        predictor.train(X, y)
        
        # Check that model was trained
        assert predictor.model is not None
        assert len(predictor.feature_names) > 0
        assert 'training_samples' in predictor.metadata
        assert 'trained_at' in predictor.metadata
    
    def test_model_evaluation(self, training_data):
        """Test model evaluation."""
        predictor = ChurnPredictor()
        X, y = training_data
        
        # Train model first
        predictor.train(X, y)
        
        # Evaluate model
        metrics = predictor.evaluate(X, y)
        
        assert 'accuracy' in metrics
        assert 'auc_roc' in metrics
        assert 'threshold' in metrics
        assert 'evaluation_time' in metrics
        
        # Check metric ranges
        assert 0 <= metrics['accuracy'] <= 1
        assert 0 <= metrics['auc_roc'] <= 1
    
    def test_threshold_setting(self):
        """Test threshold setting."""
        predictor = ChurnPredictor()
        
        # Test valid threshold
        predictor.set_threshold(0.7)
        assert predictor.threshold == 0.7
        
        # Test invalid threshold
        with pytest.raises(ValueError):
            predictor.set_threshold(1.5)
        
        with pytest.raises(ValueError):
            predictor.set_threshold(-0.1)
    
    def test_feature_importance(self, training_data):
        """Test feature importance extraction."""
        predictor = ChurnPredictor()
        X, y = training_data
        
        # Train model
        predictor.train(X, y)
        
        # Get feature importance
        importance = predictor.get_feature_importance()
        
        assert isinstance(importance, dict)
        # Should have importance for each feature
        assert len(importance) > 0
        
        # All importance values should be floats
        for value in importance.values():
            assert isinstance(value, float)
            assert value >= 0


class TestBaseModel:
    """Test BaseModel functionality."""
    
    def test_model_creation(self):
        """Test base model creation."""
        
        class TestModel(BaseModel):
            def train(self, X, y, **kwargs):
                self.model = "trained"
            
            def predict(self, X):
                return ["prediction"] * len(X)
            
            def predict_proba(self, X):
                return [0.5] * len(X)
        
        model = TestModel("test_model", "v1.0")
        
        assert model.name == "test_model"
        assert model.version == "v1.0"
        assert model.model is None
        assert isinstance(model.metadata, dict)
    
    def test_model_save_load(self, tmp_path):
        """Test model save and load."""
        
        class TestModel(BaseModel):
            def train(self, X, y, **kwargs):
                self.model = {"trained": True}
            
            def predict(self, X):
                return ["prediction"] * len(X)
            
            def predict_proba(self, X):
                return [0.5] * len(X)
        
        model = TestModel("test_model", "v1.0")
        model.train([], [])
        model.metadata["test_key"] = "test_value"
        
        # Save model
        model.save(str(tmp_path))
        
        # Load model
        new_model = TestModel("test_model", "v1.0")
        new_model.load(str(tmp_path))
        
        assert new_model.model == {"trained": True}
        assert new_model.metadata["test_key"] == "test_value"
    
    def test_model_validation(self):
        """Test model validation."""
        
        class TestModel(BaseModel):
            def train(self, X, y, **kwargs):
                self.model = "trained"
            
            def predict(self, X):
                return ["prediction"] * len(X)
            
            def predict_proba(self, X):
                return [0.5] * len(X)
        
        model = TestModel("test_model", "v1.0")
        
        # Test validation without trained model
        with pytest.raises(ValueError):
            model.validate([1, 2, 3])
        
        # Train model
        model.train([], [])
        
        # Test validation with trained model
        result = model.validate([1, 2, 3])
        
        assert "predictions_count" in result
        assert "model_name" in result
        assert "model_version" in result
        assert result["predictions_count"] == 3


class TestModelRegistry:
    """Test ModelRegistry functionality."""
    
    def test_registry_operations(self):
        """Test model registry operations."""
        
        class TestModel(BaseModel):
            def train(self, X, y, **kwargs):
                self.model = "trained"
            
            def predict(self, X):
                return ["prediction"] * len(X)
            
            def predict_proba(self, X):
                return [0.5] * len(X)
        
        registry = ModelRegistry()
        
        # Register model
        model = TestModel("test_model", "v1.0")
        registry.register_model(model)
        
        # Test model retrieval
        retrieved = registry.get_model("test_model", "v1.0")
        assert retrieved is not None
        assert retrieved.name == "test_model"
        
        # Test model listing
        models = registry.list_models()
        assert len(models) == 1
        assert models[0]["name"] == "test_model"
        assert models[0]["version"] == "v1.0"
        
        # Test model removal
        success = registry.remove_model("test_model", "v1.0")
        assert success
        
        # Verify removal
        retrieved = registry.get_model("test_model", "v1.0")
        assert retrieved is None
    
    def test_registry_save_load(self, tmp_path):
        """Test registry save and load operations."""
        
        class TestModel(BaseModel):
            def train(self, X, y, **kwargs):
                self.model = "trained"
            
            def predict(self, X):
                return ["prediction"] * len(X)
            
            def predict_proba(self, X):
                return [0.5] * len(X)
        
        registry = ModelRegistry()
        
        # Register and train model
        model = TestModel("test_model", "v1.0")
        model.train([], [])
        registry.register_model(model)
        
        # Save all models
        registry.save_all_models(str(tmp_path))
        
        # Verify files were created
        assert (tmp_path / "test_model_v1.0.pkl").exists()
        assert (tmp_path / "test_model_v1.0_metadata.json").exists()


class TestMockChurnModel:
    """Test MockChurnModel functionality."""
    
    def test_mock_model_training(self):
        """Test mock model training."""
        from silver_adventure.ml.churn_prediction import MockChurnModel
        
        model = MockChurnModel()
        
        # Train model
        X = np.random.random((100, 7))
        y = np.random.randint(0, 2, 100)
        
        model.fit(X, y)
        
        assert model.is_fitted
    
    def test_mock_model_prediction(self):
        """Test mock model prediction."""
        from silver_adventure.ml.churn_prediction import MockChurnModel
        
        model = MockChurnModel()
        
        # Train model
        X = np.random.random((100, 7))
        y = np.random.randint(0, 2, 100)
        model.fit(X, y)
        
        # Test prediction
        test_X = np.random.random((10, 7))
        
        # Test probability prediction
        probabilities = model.predict_proba(test_X)
        assert len(probabilities) == 10
        assert all(0 <= p <= 1 for p in probabilities)
        
        # Test binary prediction
        predictions = model.predict(test_X)
        assert len(predictions) == 10
        assert all(p in [0, 1] for p in predictions)
    
    def test_mock_model_unfitted_error(self):
        """Test error when using unfitted model."""
        from silver_adventure.ml.churn_prediction import MockChurnModel
        
        model = MockChurnModel()
        
        # Test that unfitted model raises error
        with pytest.raises(ValueError):
            model.predict_proba(np.random.random((10, 7)))
        
        with pytest.raises(ValueError):
            model.predict(np.random.random((10, 7)))