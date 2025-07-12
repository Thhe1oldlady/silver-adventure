"""
Churn Service - Customer Churn Prediction

This service handles machine learning models for predicting customer churn.
It includes model training, prediction, and pipeline management capabilities.
"""

import json
import logging
import os
import pickle
from datetime import datetime
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

logger = logging.getLogger(__name__)


class ChurnService:
    """Service for customer churn prediction and model management"""

    def __init__(self):
        self.model_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "models"
        )
        self.data_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "data"
        )

        # Ensure directories exist
        os.makedirs(self.model_path, exist_ok=True)
        os.makedirs(self.data_path, exist_ok=True)

        # Model configuration
        self.model_config = {
            "random_forest": {
                "n_estimators": 100,
                "max_depth": 10,
                "min_samples_split": 5,
                "min_samples_leaf": 2,
                "random_state": 42,
            },
            "gradient_boosting": {
                "n_estimators": 100,
                "learning_rate": 0.1,
                "max_depth": 6,
                "random_state": 42,
            },
        }

        # Feature definitions
        self.required_features = [
            "tenure_months",
            "monthly_charges",
            "total_charges",
            "contract_length",
            "payment_method",
            "internet_service",
            "online_security",
            "online_backup",
            "device_protection",
            "tech_support",
            "streaming_tv",
            "streaming_movies",
            "paperless_billing",
            "senior_citizen",
            "partner",
            "dependents",
            "phone_service",
            "multiple_lines",
        ]

        # Load models if they exist
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self._load_models()

    def health_check(self) -> bool:
        """Check if churn service is healthy"""
        try:
            # Check if model directories exist
            if not os.path.exists(self.model_path):
                return False

            # Check if at least one model is loaded
            if not self.models:
                # Try to load sample data for training
                self._generate_sample_data()
                return True

            return True

        except Exception as e:
            logger.error(f"Churn service health check failed: {str(e)}")
            return False

    def get_required_features(self) -> List[str]:
        """Get list of required features for churn prediction"""
        return self.required_features

    def _load_models(self):
        """Load trained models and preprocessors"""
        try:
            model_files = {
                "random_forest": "churn_model_rf.pkl",
                "gradient_boosting": "churn_model_gb.pkl",
            }

            for model_name, filename in model_files.items():
                model_file = os.path.join(self.model_path, filename)
                scaler_file = os.path.join(self.model_path, f"scaler_{model_name}.pkl")
                encoder_file = os.path.join(
                    self.model_path, f"encoder_{model_name}.pkl"
                )

                if os.path.exists(model_file):
                    self.models[model_name] = joblib.load(model_file)
                    logger.info(f"Loaded {model_name} model")

                    if os.path.exists(scaler_file):
                        self.scalers[model_name] = joblib.load(scaler_file)

                    if os.path.exists(encoder_file):
                        self.encoders[model_name] = joblib.load(encoder_file)

        except Exception as e:
            logger.warning(f"Could not load models: {str(e)}")

    def _generate_sample_data(self) -> pd.DataFrame:
        """Generate sample data for training and testing"""
        np.random.seed(42)
        n_samples = 1000

        # Generate synthetic customer data
        data = {
            "customer_id": [f"CUST_{i:04d}" for i in range(n_samples)],
            "tenure_months": np.random.randint(1, 72, n_samples),
            "monthly_charges": np.abs(np.random.normal(65, 20, n_samples)),
            "total_charges": np.abs(np.random.normal(2000, 1000, n_samples)),
            "contract_length": np.random.choice(
                [1, 12, 24], n_samples, p=[0.5, 0.3, 0.2]
            ),
            "payment_method": np.random.choice(
                ["Credit Card", "Bank Transfer", "Electronic Check", "Mailed Check"],
                n_samples,
            ),
            "internet_service": np.random.choice(
                ["DSL", "Fiber Optic", "No"], n_samples, p=[0.4, 0.4, 0.2]
            ),
            "online_security": np.random.choice(["Yes", "No"], n_samples),
            "online_backup": np.random.choice(["Yes", "No"], n_samples),
            "device_protection": np.random.choice(["Yes", "No"], n_samples),
            "tech_support": np.random.choice(["Yes", "No"], n_samples),
            "streaming_tv": np.random.choice(["Yes", "No"], n_samples),
            "streaming_movies": np.random.choice(["Yes", "No"], n_samples),
            "paperless_billing": np.random.choice(["Yes", "No"], n_samples),
            "senior_citizen": np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
            "partner": np.random.choice(["Yes", "No"], n_samples),
            "dependents": np.random.choice(["Yes", "No"], n_samples),
            "phone_service": np.random.choice(["Yes", "No"], n_samples, p=[0.9, 0.1]),
            "multiple_lines": np.random.choice(["Yes", "No"], n_samples),
        }

        df = pd.DataFrame(data)

        # Generate churn labels based on logical rules
        churn_prob = (
            (df["tenure_months"] < 12) * 0.3
            + (df["monthly_charges"] > 80) * 0.2
            + (df["contract_length"] == 1) * 0.25
            + (df["payment_method"] == "Electronic Check") * 0.15
            + (df["senior_citizen"] == 1) * 0.1
        )

        # Add some randomness
        churn_prob += np.random.normal(0, 0.1, n_samples)
        churn_prob = np.clip(churn_prob, 0, 1)

        df["churn"] = np.random.binomial(1, churn_prob)

        # Save sample data
        sample_data_path = os.path.join(self.data_path, "sample_churn_data.csv")
        df.to_csv(sample_data_path, index=False)
        logger.info(f"Generated sample data: {sample_data_path}")

        return df

    def _preprocess_data(
        self, df: pd.DataFrame, model_name: str, fit_preprocessors: bool = False
    ) -> pd.DataFrame:
        """Preprocess data for model training/prediction"""
        df_processed = df.copy()

        # Handle missing values
        df_processed["total_charges"] = pd.to_numeric(
            df_processed["total_charges"], errors="coerce"
        )
        df_processed["total_charges"] = df_processed["total_charges"].fillna(
            df_processed["total_charges"].median()
        )

        # Encode categorical variables
        categorical_columns = [
            "payment_method",
            "internet_service",
            "online_security",
            "online_backup",
            "device_protection",
            "tech_support",
            "streaming_tv",
            "streaming_movies",
            "paperless_billing",
            "partner",
            "dependents",
            "phone_service",
            "multiple_lines",
        ]

        if fit_preprocessors:
            self.encoders[model_name] = {}

        for col in categorical_columns:
            if col in df_processed.columns:
                if fit_preprocessors:
                    le = LabelEncoder()
                    df_processed[col] = le.fit_transform(df_processed[col].astype(str))
                    self.encoders[model_name][col] = le
                else:
                    if model_name in self.encoders and col in self.encoders[model_name]:
                        le = self.encoders[model_name][col]
                        # Handle unseen categories
                        unique_values = set(df_processed[col].unique())
                        known_values = set(le.classes_)

                        if unique_values - known_values:
                            # Add unknown categories
                            new_classes = list(le.classes_) + list(
                                unique_values - known_values
                            )
                            le.classes_ = np.array(new_classes)

                        df_processed[col] = le.transform(df_processed[col].astype(str))

        # Scale numerical features
        numerical_columns = ["tenure_months", "monthly_charges", "total_charges"]

        if fit_preprocessors:
            scaler = StandardScaler()
            df_processed[numerical_columns] = scaler.fit_transform(
                df_processed[numerical_columns]
            )
            self.scalers[model_name] = scaler
        else:
            if model_name in self.scalers:
                scaler = self.scalers[model_name]
                df_processed[numerical_columns] = scaler.transform(
                    df_processed[numerical_columns]
                )

        return df_processed

    async def train_model(self, model_type: str = "random_forest") -> Dict[str, Any]:
        """Train or retrain the churn prediction model"""
        try:
            # Load or generate training data
            sample_data_path = os.path.join(self.data_path, "sample_churn_data.csv")

            if not os.path.exists(sample_data_path):
                logger.info("No training data found, generating sample data")
                df = self._generate_sample_data()
            else:
                df = pd.read_csv(sample_data_path)

            # Prepare features and target
            feature_cols = [col for col in self.required_features if col in df.columns]
            X = df[feature_cols]
            y = df["churn"]

            # Preprocess data
            X_processed = self._preprocess_data(X, model_type, fit_preprocessors=True)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_processed, y, test_size=0.2, random_state=42, stratify=y
            )

            # Train model
            if model_type == "random_forest":
                model = RandomForestClassifier(**self.model_config["random_forest"])
            elif model_type == "gradient_boosting":
                model = GradientBoostingClassifier(
                    **self.model_config["gradient_boosting"]
                )
            else:
                raise ValueError(f"Unknown model type: {model_type}")

            model.fit(X_train, y_train)

            # Evaluate model
            y_pred = model.predict(X_test)

            metrics = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred),
                "recall": recall_score(y_test, y_pred),
                "f1_score": f1_score(y_test, y_pred),
            }

            # Cross-validation
            cv_scores = cross_val_score(model, X_processed, y, cv=5)
            metrics["cv_mean"] = cv_scores.mean()
            metrics["cv_std"] = cv_scores.std()

            # Save model and preprocessors
            model_id = f"{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            model_file = os.path.join(self.model_path, f"churn_model_{model_type}.pkl")
            scaler_file = os.path.join(self.model_path, f"scaler_{model_type}.pkl")
            encoder_file = os.path.join(self.model_path, f"encoder_{model_type}.pkl")

            joblib.dump(model, model_file)
            joblib.dump(self.scalers[model_type], scaler_file)
            joblib.dump(self.encoders[model_type], encoder_file)

            # Update loaded models
            self.models[model_type] = model

            # Save training metadata
            metadata = {
                "model_id": model_id,
                "model_type": model_type,
                "training_date": datetime.now().isoformat(),
                "metrics": metrics,
                "feature_count": len(feature_cols),
                "training_samples": len(X_train),
            }

            metadata_file = os.path.join(self.model_path, f"metadata_{model_type}.json")
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

            logger.info(
                f"Model {model_type} trained successfully with accuracy: {metrics['accuracy']:.3f}"
            )

            return {
                "model_id": model_id,
                "accuracy": metrics["accuracy"],
                "precision": metrics["precision"],
                "recall": metrics["recall"],
                "f1_score": metrics["f1_score"],
                "cv_mean": metrics["cv_mean"],
                "status": "trained",
            }

        except Exception as e:
            logger.error(f"Model training failed: {str(e)}")
            raise Exception(f"Model training failed: {str(e)}")

    async def predict_churn(
        self, customer_id: str, features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict churn probability for a customer"""
        try:
            # Use random forest model by default
            model_type = "random_forest"

            # If no model is loaded, train one
            if model_type not in self.models:
                logger.info("No model found, training new model")
                await self.train_model(model_type)

            model = self.models[model_type]

            # Convert features to DataFrame
            feature_data = {}
            for feature in self.required_features:
                if feature in features:
                    feature_data[feature] = [features[feature]]
                else:
                    # Use default values for missing features
                    if feature in ["tenure_months", "monthly_charges", "total_charges"]:
                        feature_data[feature] = [50]  # Default numerical value
                    elif feature == "contract_length":
                        feature_data[feature] = [12]  # Default contract length
                    elif feature == "senior_citizen":
                        feature_data[feature] = [0]  # Default not senior
                    else:
                        feature_data[feature] = ["No"]  # Default categorical value

            df = pd.DataFrame(feature_data)

            # Preprocess features
            X_processed = self._preprocess_data(df, model_type, fit_preprocessors=False)

            # Make prediction
            churn_probability = model.predict_proba(X_processed)[0, 1]

            # Determine risk level
            if churn_probability >= 0.7:
                risk_level = "High"
            elif churn_probability >= 0.4:
                risk_level = "Medium"
            else:
                risk_level = "Low"

            # Generate recommendations
            recommendations = self._generate_recommendations(risk_level, features)

            return {
                "customer_id": customer_id,
                "churn_probability": float(churn_probability),
                "risk_level": risk_level,
                "recommendations": recommendations,
            }

        except Exception as e:
            logger.error(
                f"Churn prediction failed for customer {customer_id}: {str(e)}"
            )
            raise Exception(f"Churn prediction failed: {str(e)}")

    def _generate_recommendations(
        self, risk_level: str, features: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on risk level and features"""
        recommendations = []

        if risk_level == "High":
            recommendations.extend(
                [
                    "Immediate intervention required - contact customer within 24 hours",
                    "Offer personalized retention incentives",
                    "Schedule call with customer success manager",
                    "Consider upgrading to premium support",
                ]
            )
        elif risk_level == "Medium":
            recommendations.extend(
                [
                    "Proactive engagement - reach out within 1 week",
                    "Send personalized offers or discounts",
                    "Provide additional product value education",
                    "Monitor usage patterns closely",
                ]
            )
        else:
            recommendations.extend(
                [
                    "Continue standard engagement",
                    "Share success stories and use cases",
                    "Maintain regular check-ins",
                    "Encourage referrals and reviews",
                ]
            )

        # Feature-specific recommendations
        if features.get("monthly_charges", 0) > 80:
            recommendations.append("Consider offering cost optimization review")

        if features.get("tenure_months", 12) < 6:
            recommendations.append("Focus on onboarding and early success")

        if features.get("contract_length", 12) == 1:
            recommendations.append("Offer long-term contract incentives")

        if features.get("tech_support") == "No":
            recommendations.append("Promote technical support services")

        return recommendations

    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get the current pipeline status"""
        try:
            status = {
                "pipeline_health": "healthy",
                "models_loaded": len(self.models),
                "available_models": list(self.models.keys()),
                "last_update": datetime.now().isoformat(),
                "model_details": {},
            }

            # Get model details
            for model_name in self.models.keys():
                metadata_file = os.path.join(
                    self.model_path, f"metadata_{model_name}.json"
                )
                if os.path.exists(metadata_file):
                    with open(metadata_file, "r") as f:
                        metadata = json.load(f)
                        status["model_details"][model_name] = metadata

            return status

        except Exception as e:
            logger.error(f"Failed to get pipeline status: {str(e)}")
            return {
                "pipeline_health": "error",
                "error": str(e),
                "last_update": datetime.now().isoformat(),
            }
