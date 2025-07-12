"""Base ML model classes and registry."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import pickle
import joblib
import json
from datetime import datetime

from ..core.config import get_config
from ..core.logger import get_logger


class BaseModel(ABC):
    """Abstract base class for ML models."""
    
    def __init__(self, name: str, version: str = "v1.0"):
        self.name = name
        self.version = version
        self.model = None
        self.metadata = {}
        self.logger = get_logger(f"model.{name}")
    
    @abstractmethod
    def train(self, X, y, **kwargs):
        """Train the model."""
        pass
    
    @abstractmethod
    def predict(self, X) -> Union[List, Dict]:
        """Make predictions."""
        pass
    
    @abstractmethod
    def predict_proba(self, X) -> Union[List, Dict]:
        """Predict probabilities."""
        pass
    
    def save(self, path: str) -> None:
        """Save model to file."""
        model_path = Path(path)
        model_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save model
        if self.model is not None:
            joblib.dump(self.model, model_path / f"{self.name}_{self.version}.pkl")
        
        # Save metadata
        metadata = {
            "name": self.name,
            "version": self.version,
            "created_at": datetime.utcnow().isoformat(),
            "metadata": self.metadata
        }
        
        with open(model_path / f"{self.name}_{self.version}_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.info(f"Model saved to {path}")
    
    def load(self, path: str) -> None:
        """Load model from file."""
        model_path = Path(path)
        
        # Load model
        model_file = model_path / f"{self.name}_{self.version}.pkl"
        if model_file.exists():
            self.model = joblib.load(model_file)
        
        # Load metadata
        metadata_file = model_path / f"{self.name}_{self.version}_metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                loaded_metadata = json.load(f)
                self.metadata = loaded_metadata.get("metadata", {})
        
        self.logger.info(f"Model loaded from {path}")
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance if supported."""
        if hasattr(self.model, 'feature_importances_'):
            return dict(zip(
                self.metadata.get('feature_names', []),
                self.model.feature_importances_
            ))
        return {}
    
    def validate(self, X, y=None) -> Dict[str, Any]:
        """Validate model performance."""
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        
        # Basic validation
        predictions = self.predict(X)
        validation_results = {
            "predictions_count": len(predictions),
            "model_name": self.name,
            "model_version": self.version,
            "validation_time": datetime.utcnow().isoformat()
        }
        
        # Add accuracy if labels provided
        if y is not None:
            try:
                from sklearn.metrics import accuracy_score
                accuracy = accuracy_score(y, predictions)
                validation_results["accuracy"] = accuracy
            except ImportError:
                self.logger.warning("scikit-learn not available for accuracy calculation")
        
        return validation_results


class ModelRegistry:
    """Registry for managing ML models."""
    
    def __init__(self):
        self.models = {}
        self.logger = get_logger("model.registry")
        self.config = get_config()
    
    def register_model(self, model: BaseModel) -> None:
        """Register a model."""
        model_key = f"{model.name}_{model.version}"
        self.models[model_key] = model
        self.logger.info(f"Model registered: {model_key}")
    
    def get_model(self, name: str, version: str = "v1.0") -> Optional[BaseModel]:
        """Get a model by name and version."""
        model_key = f"{name}_{version}"
        return self.models.get(model_key)
    
    def list_models(self) -> List[Dict[str, str]]:
        """List all registered models."""
        return [
            {
                "name": model.name,
                "version": model.version,
                "status": "active" if model.model is not None else "inactive"
            }
            for model in self.models.values()
        ]
    
    def remove_model(self, name: str, version: str = "v1.0") -> bool:
        """Remove a model from registry."""
        model_key = f"{name}_{version}"
        if model_key in self.models:
            del self.models[model_key]
            self.logger.info(f"Model removed: {model_key}")
            return True
        return False
    
    def load_models_from_directory(self, directory: str) -> None:
        """Load models from directory."""
        model_path = Path(directory)
        if not model_path.exists():
            self.logger.warning(f"Model directory not found: {directory}")
            return
        
        # Look for metadata files
        for metadata_file in model_path.glob("*_metadata.json"):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                model_name = metadata["name"]
                model_version = metadata["version"]
                
                # Create model instance based on type
                if model_name == "churn_predictor":
                    from .churn_prediction import ChurnPredictor
                    model = ChurnPredictor(version=model_version)
                    model.load(str(model_path))
                    self.register_model(model)
                
            except Exception as e:
                self.logger.error(f"Failed to load model from {metadata_file}: {str(e)}")
    
    def save_all_models(self, directory: str) -> None:
        """Save all models to directory."""
        for model in self.models.values():
            try:
                model.save(directory)
            except Exception as e:
                self.logger.error(f"Failed to save model {model.name}: {str(e)}")


# Global model registry instance
model_registry = ModelRegistry()


def get_model_registry() -> ModelRegistry:
    """Get the global model registry instance."""
    return model_registry