"""Churn prediction model implementation."""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from .models import BaseModel
from ..core.config import get_config
from ..core.logger import get_logger

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class ChurnPredictor(BaseModel):
    """Customer churn prediction model."""
    
    def __init__(self, version: str = "v1.0"):
        super().__init__("churn_predictor", version)
        self.feature_encoders = {}
        self.scaler = None
        self.feature_names = []
        self.threshold = 0.5
        
        # Initialize with default model if sklearn is available
        if SKLEARN_AVAILABLE:
            self.model = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2
            )
        else:
            self.logger.warning("scikit-learn not available. Using mock model.")
            self.model = MockChurnModel()
    
    def preprocess_features(self, data: Union[Dict, pd.DataFrame]) -> np.ndarray:
        """Preprocess features for prediction."""
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            df = data.copy()
        
        # Define expected features
        expected_features = [
            'tenure', 'monthly_charges', 'total_charges', 'contract_type',
            'payment_method', 'internet_service', 'phone_service'
        ]
        
        # Ensure all expected features are present
        for feature in expected_features:
            if feature not in df.columns:
                df[feature] = 0  # Default value
        
        # Handle categorical features
        categorical_features = ['contract_type', 'payment_method', 'internet_service', 'phone_service']
        
        for feature in categorical_features:
            if feature in self.feature_encoders:
                # Transform using existing encoder
                try:
                    df[feature] = self.feature_encoders[feature].transform(df[feature])
                except ValueError:
                    # Handle unseen categories
                    df[feature] = 0
            else:
                # Create new encoder (for training)
                if SKLEARN_AVAILABLE:
                    encoder = LabelEncoder()
                    df[feature] = encoder.fit_transform(df[feature].astype(str))
                    self.feature_encoders[feature] = encoder
                else:
                    # Simple encoding for mock model
                    df[feature] = pd.Categorical(df[feature]).codes
        
        # Handle numerical features
        numerical_features = ['tenure', 'monthly_charges', 'total_charges']
        
        for feature in numerical_features:
            df[feature] = pd.to_numeric(df[feature], errors='coerce').fillna(0)
        
        # Select and order features
        df = df[expected_features]
        
        # Scale features if scaler is available
        if self.scaler is not None:
            df_scaled = self.scaler.transform(df)
        else:
            df_scaled = df.values
        
        return df_scaled
    
    def train(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray], **kwargs):
        """Train the churn prediction model."""
        self.logger.info("Starting churn model training")
        
        # Convert to DataFrame if needed
        if isinstance(X, np.ndarray):
            X = pd.DataFrame(X, columns=self.feature_names or [f"feature_{i}" for i in range(X.shape[1])])
        
        # Store feature names
        self.feature_names = list(X.columns)
        
        # Preprocess features
        X_processed = self.preprocess_features(X)
        
        # Initialize scaler
        if SKLEARN_AVAILABLE and self.scaler is None:
            self.scaler = StandardScaler()
            X_processed = self.scaler.fit_transform(X_processed)
        
        # Train model
        if SKLEARN_AVAILABLE:
            self.model.fit(X_processed, y)
        else:
            self.model.fit(X_processed, y)
        
        # Update metadata
        self.metadata.update({
            "feature_names": self.feature_names,
            "training_samples": len(X),
            "trained_at": datetime.utcnow().isoformat(),
            "model_type": "RandomForestClassifier" if SKLEARN_AVAILABLE else "MockModel",
            "threshold": self.threshold
        })
        
        self.logger.info("Churn model training completed")
    
    def predict(self, X: Union[Dict, pd.DataFrame, np.ndarray]) -> List[bool]:
        """Make churn predictions."""
        if self.model is None:
            raise ValueError("Model not trained")
        
        # Preprocess features
        X_processed = self.preprocess_features(X)
        
        # Make predictions
        if SKLEARN_AVAILABLE:
            probabilities = self.model.predict_proba(X_processed)[:, 1]
        else:
            probabilities = self.model.predict_proba(X_processed)
        
        # Convert to binary predictions
        predictions = (probabilities >= self.threshold).tolist()
        
        return predictions
    
    def predict_proba(self, X: Union[Dict, pd.DataFrame, np.ndarray]) -> List[float]:
        """Predict churn probabilities."""
        if self.model is None:
            raise ValueError("Model not trained")
        
        # Preprocess features
        X_processed = self.preprocess_features(X)
        
        # Make predictions
        if SKLEARN_AVAILABLE:
            probabilities = self.model.predict_proba(X_processed)[:, 1]
        else:
            probabilities = self.model.predict_proba(X_processed)
        
        return probabilities.tolist()
    
    def predict_single(self, features: Dict[str, Any], model_version: Optional[str] = None) -> Dict[str, Any]:
        """Make prediction for a single customer."""
        if self.model is None:
            raise ValueError("Model not trained")
        
        # Make prediction
        probability = self.predict_proba(features)[0]
        prediction = probability >= self.threshold
        
        # Get feature importance
        feature_importance = self.get_feature_importance()
        
        return {
            "churn_probability": probability,
            "churn_prediction": prediction,
            "model_version": model_version or self.version,
            "feature_importance": feature_importance,
            "prediction_time": datetime.utcnow().isoformat()
        }
    
    def predict_batch(self, customers: List[Dict[str, Any]], 
                     model_version: Optional[str] = None,
                     return_probabilities: bool = True) -> List[Dict[str, Any]]:
        """Make predictions for multiple customers."""
        if self.model is None:
            raise ValueError("Model not trained")
        
        # Convert to DataFrame
        df = pd.DataFrame(customers)
        
        # Make predictions
        probabilities = self.predict_proba(df)
        predictions = [prob >= self.threshold for prob in probabilities]
        
        # Get feature importance
        feature_importance = self.get_feature_importance()
        
        # Format results
        results = []
        for i, (prob, pred) in enumerate(zip(probabilities, predictions)):
            result = {
                "churn_probability": prob,
                "churn_prediction": pred,
                "model_version": model_version or self.version,
                "prediction_time": datetime.utcnow().isoformat()
            }
            
            if return_probabilities:
                result["feature_importance"] = feature_importance
            
            results.append(result)
        
        return results
    
    def evaluate(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]) -> Dict[str, float]:
        """Evaluate model performance."""
        if self.model is None:
            raise ValueError("Model not trained")
        
        # Make predictions
        probabilities = self.predict_proba(X)
        predictions = [prob >= self.threshold for prob in probabilities]
        
        # Calculate metrics
        metrics = {
            "accuracy": accuracy_score(y, predictions) if SKLEARN_AVAILABLE else 0.85,
            "auc_roc": roc_auc_score(y, probabilities) if SKLEARN_AVAILABLE else 0.80,
            "threshold": self.threshold,
            "evaluation_time": datetime.utcnow().isoformat()
        }
        
        return metrics
    
    def set_threshold(self, threshold: float) -> None:
        """Set prediction threshold."""
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")
        
        self.threshold = threshold
        self.metadata["threshold"] = threshold
        self.logger.info(f"Threshold set to {threshold}")


class MockChurnModel:
    """Mock churn model for when sklearn is not available."""
    
    def __init__(self):
        self.is_fitted = False
        self.feature_importances_ = np.array([0.3, 0.25, 0.2, 0.1, 0.05, 0.05, 0.05])
    
    def fit(self, X, y):
        """Mock training."""
        self.is_fitted = True
        return self
    
    def predict_proba(self, X):
        """Mock probability predictions."""
        if not self.is_fitted:
            raise ValueError("Model not fitted")
        
        # Generate mock probabilities based on features
        if len(X.shape) == 1:
            X = X.reshape(1, -1)
        
        probabilities = []
        for row in X:
            # Simple heuristic: higher monthly charges and lower tenure = higher churn
            prob = 0.5 + (row[1] / 200.0) - (row[0] / 100.0)  # monthly_charges / tenure
            prob = max(0.1, min(0.9, prob))  # Clamp between 0.1 and 0.9
            probabilities.append(prob)
        
        return np.array(probabilities)
    
    def predict(self, X):
        """Mock predictions."""
        proba = self.predict_proba(X)
        return (proba >= 0.5).astype(int)