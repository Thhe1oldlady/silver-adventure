"""Test configuration and fixtures."""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from silver_adventure.core.config import Config
from silver_adventure.core.pipeline import Pipeline, PipelineContext
from silver_adventure.ml.churn_prediction import ChurnPredictor


@pytest.fixture
def sample_config():
    """Create a sample configuration for testing."""
    return Config(
        environment="test",
        debug=True,
        log_level="DEBUG"
    )


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    np.random.seed(42)
    
    data = {
        'customer_id': [f'CUST_{i:04d}' for i in range(100)],
        'age': np.random.randint(18, 80, 100),
        'income': np.random.lognormal(10, 0.5, 100),
        'tenure': np.random.randint(1, 120, 100),
        'monthly_charges': np.random.uniform(20, 120, 100),
        'contract_type': np.random.choice(['Month-to-month', 'One year', 'Two year'], 100),
        'payment_method': np.random.choice(['Credit card', 'Bank transfer', 'Electronic check'], 100),
        'internet_service': np.random.choice(['DSL', 'Fiber optic', 'No'], 100),
        'phone_service': np.random.choice(['Yes', 'No'], 100),
    }
    
    return pd.DataFrame(data)


@pytest.fixture
def sample_customer_data():
    """Create sample customer data for churn prediction."""
    return {
        'customer_id': 'CUST_001',
        'tenure': 12,
        'monthly_charges': 79.99,
        'total_charges': 959.88,
        'contract_type': 'Month-to-month',
        'payment_method': 'Credit card',
        'internet_service': 'Fiber optic',
        'phone_service': 'Yes'
    }


@pytest.fixture
def sample_pipeline_context():
    """Create a sample pipeline context."""
    return PipelineContext(
        data={"test": "data"},
        pipeline_name="test_pipeline",
        metadata={"test_key": "test_value"}
    )


@pytest.fixture
def churn_predictor():
    """Create a churn predictor instance."""
    return ChurnPredictor()


@pytest.fixture
def training_data():
    """Create training data for ML models."""
    np.random.seed(42)
    
    n_samples = 1000
    
    # Create features
    tenure = np.random.randint(1, 72, n_samples)
    monthly_charges = np.random.uniform(20, 120, n_samples)
    total_charges = tenure * monthly_charges + np.random.normal(0, 100, n_samples)
    total_charges = np.maximum(0, total_charges)
    
    contract_type = np.random.choice(['Month-to-month', 'One year', 'Two year'], n_samples)
    payment_method = np.random.choice(['Credit card', 'Bank transfer', 'Electronic check'], n_samples)
    internet_service = np.random.choice(['DSL', 'Fiber optic', 'No'], n_samples)
    phone_service = np.random.choice(['Yes', 'No'], n_samples)
    
    # Create DataFrame
    X = pd.DataFrame({
        'tenure': tenure,
        'monthly_charges': monthly_charges,
        'total_charges': total_charges,
        'contract_type': contract_type,
        'payment_method': payment_method,
        'internet_service': internet_service,
        'phone_service': phone_service,
    })
    
    # Create labels
    churn_prob = (
        0.1 +  # Base probability
        0.3 * (tenure < 12) +  # Short tenure
        0.2 * (monthly_charges > 80) +  # High charges
        0.3 * (contract_type == 'Month-to-month') +  # Month-to-month
        0.2 * (payment_method == 'Electronic check') +  # Electronic check
        np.random.normal(0, 0.1, n_samples)  # Random noise
    )
    
    churn_prob = np.clip(churn_prob, 0, 1)
    y = (np.random.random(n_samples) < churn_prob).astype(int)
    
    return X, y


@pytest.fixture
def temp_csv_file(tmp_path, sample_dataframe):
    """Create a temporary CSV file for testing."""
    csv_file = tmp_path / "test_data.csv"
    sample_dataframe.to_csv(csv_file, index=False)
    return str(csv_file)


@pytest.fixture
def temp_json_file(tmp_path):
    """Create a temporary JSON file for testing."""
    json_file = tmp_path / "test_data.json"
    test_data = {
        "customers": [
            {"id": 1, "name": "John Doe", "age": 30},
            {"id": 2, "name": "Jane Smith", "age": 25}
        ]
    }
    
    import json
    with open(json_file, 'w') as f:
        json.dump(test_data, f)
    
    return str(json_file)


# Test utilities
def assert_dataframe_equal(df1, df2, check_dtype=False):
    """Assert that two DataFrames are equal."""
    pd.testing.assert_frame_equal(df1, df2, check_dtype=check_dtype)


def assert_pipeline_context_valid(context: PipelineContext):
    """Assert that pipeline context is valid."""
    assert context is not None
    assert hasattr(context, 'data')
    assert hasattr(context, 'metadata')
    assert hasattr(context, 'pipeline_name')
    assert hasattr(context, 'errors')
    assert isinstance(context.metadata, dict)
    assert isinstance(context.errors, list)


def create_mock_api_response(status_code=200, data=None):
    """Create a mock API response."""
    class MockResponse:
        def __init__(self, status_code, data):
            self.status_code = status_code
            self.data = data or {}
        
        def json(self):
            return self.data
        
        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception(f"HTTP {self.status_code}")
    
    return MockResponse(status_code, data)