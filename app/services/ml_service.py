"""
Machine Learning Service for churn prediction.
"""

import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score
import asyncio
import os
from datetime import datetime

from app.core.config import settings
from app.core.logging import get_logger
from app.models.schemas import ChurnPredictionRequest, ChurnPredictionResponse

logger = get_logger(__name__)


class MLService:
    """
    Machine Learning service for churn prediction.
    """
    
    def __init__(self):
        self.model: Optional[RandomForestClassifier] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_names: List[str] = []
        self.model_version: str = "1.0.0"
        self.is_initialized: bool = False
        
    async def initialize(self):
        """
        Initialize the ML service.
        """
        try:
            logger.info("Initializing ML service...")
            
            # Create models directory if it doesn't exist
            model_dir = settings.MODEL_PATH
            if not os.path.exists(model_dir):
                os.makedirs(model_dir)
                logger.info(f"Created models directory: {model_dir}")
            
            # Try to load existing model
            model_path = os.path.join(model_dir, "churn_model.pkl")
            scaler_path = os.path.join(model_dir, "scaler.pkl")
            
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                await self._load_model(model_path, scaler_path)
                logger.info("Loaded existing model from disk")
            else:
                await self._train_default_model()
                logger.info("Trained new default model")
            
            self.is_initialized = True
            logger.info("ML service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ML service: {e}")
            raise
    
    async def _load_model(self, model_path: str, scaler_path: str):
        """
        Load model from disk.
        """
        try:
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            
            # Set feature names
            self.feature_names = [
                'age', 'tenure', 'monthly_charges', 'total_charges',
                'contract_type_encoded', 'payment_method_encoded'
            ]
            
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    async def _train_default_model(self):
        """
        Train a default model with synthetic data.
        """
        try:
            logger.info("Training default model with synthetic data...")
            
            # Generate synthetic training data
            np.random.seed(42)
            n_samples = 1000
            
            # Features
            age = np.random.randint(18, 80, n_samples)
            tenure = np.random.randint(1, 72, n_samples)
            monthly_charges = np.random.uniform(20, 120, n_samples)
            total_charges = monthly_charges * tenure + np.random.normal(0, 100, n_samples)
            contract_type = np.random.choice([0, 1, 2], n_samples)  # 0=month-to-month, 1=one-year, 2=two-year
            payment_method = np.random.choice([0, 1, 2, 3], n_samples)  # payment methods
            
            # Target (churn) - synthetic rules
            churn_prob = (
                0.1 + 
                0.3 * (age < 25) + 
                0.2 * (tenure < 12) + 
                0.25 * (monthly_charges > 80) +
                0.15 * (contract_type == 0)  # month-to-month more likely to churn
            )
            churn = np.random.binomial(1, churn_prob)
            
            # Create DataFrame
            X = pd.DataFrame({
                'age': age,
                'tenure': tenure,
                'monthly_charges': monthly_charges,
                'total_charges': total_charges,
                'contract_type_encoded': contract_type,
                'payment_method_encoded': payment_method
            })
            
            y = churn
            
            self.feature_names = list(X.columns)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                class_weight='balanced'
            )
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
            
            auc_score = roc_auc_score(y_test, y_pred_proba)
            logger.info(f"Model trained with AUC score: {auc_score:.3f}")
            
            # Save model
            model_path = os.path.join(settings.MODEL_PATH, "churn_model.pkl")
            scaler_path = os.path.join(settings.MODEL_PATH, "scaler.pkl")
            
            joblib.dump(self.model, model_path)
            joblib.dump(self.scaler, scaler_path)
            
            logger.info("Model saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to train default model: {e}")
            raise
    
    async def predict_churn(self, request: ChurnPredictionRequest) -> ChurnPredictionResponse:
        """
        Predict churn for a single customer.
        """
        if not self.is_initialized:
            raise RuntimeError("ML service not initialized")
        
        try:
            # Extract features
            features = self._extract_features(request.features)
            
            # Scale features
            features_scaled = self.scaler.transform([features])
            
            # Make prediction
            churn_prob = self.model.predict_proba(features_scaled)[0][1]
            
            # Determine risk level
            if churn_prob < 0.3:
                risk_level = "low"
            elif churn_prob < 0.7:
                risk_level = "medium"
            else:
                risk_level = "high"
            
            # Get feature importance
            feature_importance = self.model.feature_importances_
            top_factors = [
                self.feature_names[i] for i in np.argsort(feature_importance)[::-1][:3]
            ]
            
            return ChurnPredictionResponse(
                customer_id=request.customer_id,
                churn_probability=float(churn_prob),
                risk_level=risk_level,
                factors=top_factors
            )
            
        except Exception as e:
            logger.error(f"Prediction failed for customer {request.customer_id}: {e}")
            raise
    
    async def predict_batch(self, requests: List[ChurnPredictionRequest]) -> List[ChurnPredictionResponse]:
        """
        Predict churn for multiple customers.
        """
        if not self.is_initialized:
            raise RuntimeError("ML service not initialized")
        
        results = []
        
        for request in requests:
            try:
                prediction = await self.predict_churn(request)
                results.append(prediction)
            except Exception as e:
                logger.error(f"Batch prediction failed for customer {request.customer_id}: {e}")
                # Continue with other predictions
                continue
        
        return results
    
    def _extract_features(self, features: Dict[str, Any]) -> List[float]:
        """
        Extract and encode features for prediction.
        """
        try:
            # Extract numeric features
            age = float(features.get('age', 0))
            tenure = float(features.get('tenure', 0))
            monthly_charges = float(features.get('monthly_charges', 0))
            total_charges = float(features.get('total_charges', 0))
            
            # Encode categorical features
            contract_type = features.get('contract_type', 'month-to-month')
            contract_mapping = {
                'month-to-month': 0,
                'one-year': 1,
                'two-year': 2
            }
            contract_encoded = contract_mapping.get(contract_type.lower(), 0)
            
            payment_method = features.get('payment_method', 'credit_card')
            payment_mapping = {
                'credit_card': 0,
                'bank_transfer': 1,
                'electronic_check': 2,
                'mailed_check': 3
            }
            payment_encoded = payment_mapping.get(payment_method.lower(), 0)
            
            return [
                age, tenure, monthly_charges, total_charges,
                contract_encoded, payment_encoded
            ]
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            raise ValueError(f"Invalid features: {e}")
    
    async def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information.
        """
        if not self.is_initialized:
            return {"initialized": False}
        
        return {
            "initialized": True,
            "model_version": self.model_version,
            "feature_names": self.feature_names,
            "model_type": type(self.model).__name__,
            "feature_count": len(self.feature_names)
        }
    
    async def close(self):
        """
        Close the ML service.
        """
        logger.info("Closing ML service...")
        self.is_initialized = False