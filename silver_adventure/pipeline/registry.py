"""Pipeline registry for managing and discovering pipelines."""

from typing import Dict, List, Optional, Any
from ..core.pipeline import Pipeline, PipelineStep
from ..core.logger import get_logger
from .components import DataValidationStep, DataCleaningStep, DataTransformationStep
from .data_processing import CSVProcessingStep, DatabaseStep, APIStep


class PipelineRegistry:
    """Registry for managing and discovering pipelines."""
    
    def __init__(self):
        self.pipelines: Dict[str, Pipeline] = {}
        self.logger = get_logger("pipeline.registry")
        self._register_default_pipelines()
    
    def register_pipeline(self, name: str, pipeline: Pipeline) -> None:
        """Register a pipeline."""
        self.pipelines[name] = pipeline
        self.logger.info(f"Pipeline registered: {name}")
    
    def get_pipeline(self, name: str) -> Optional[Pipeline]:
        """Get a pipeline by name."""
        return self.pipelines.get(name)
    
    def list_pipelines(self) -> List[str]:
        """List all registered pipeline names."""
        return list(self.pipelines.keys())
    
    def remove_pipeline(self, name: str) -> bool:
        """Remove a pipeline from registry."""
        if name in self.pipelines:
            del self.pipelines[name]
            self.logger.info(f"Pipeline removed: {name}")
            return True
        return False
    
    def get_pipeline_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get pipeline information."""
        pipeline = self.get_pipeline(name)
        if pipeline is None:
            return None
        
        return {
            "name": pipeline.name,
            "steps": [step.name for step in pipeline.steps],
            "step_count": len(pipeline.steps),
            "config": pipeline.config
        }
    
    def _register_default_pipelines(self) -> None:
        """Register default pipelines."""
        
        # Data Processing Pipeline
        data_processing_steps = [
            DataValidationStep("validate_input"),
            DataCleaningStep("clean_data"),
            DataTransformationStep("transform_data")
        ]
        
        data_processing_pipeline = Pipeline(
            name="data_processing",
            steps=data_processing_steps,
            config={"description": "General data processing pipeline"}
        )
        
        self.register_pipeline("data_processing", data_processing_pipeline)
        
        # CSV Processing Pipeline
        csv_steps = [
            CSVProcessingStep("load_csv"),
            DataValidationStep("validate_csv_data"),
            DataCleaningStep("clean_csv_data"),
            DataTransformationStep("transform_csv_data")
        ]
        
        csv_pipeline = Pipeline(
            name="csv_processing",
            steps=csv_steps,
            config={"description": "CSV file processing pipeline"}
        )
        
        self.register_pipeline("csv_processing", csv_pipeline)
        
        # Database Pipeline
        database_steps = [
            DatabaseStep("load_from_database"),
            DataValidationStep("validate_db_data"),
            DataTransformationStep("transform_db_data"),
            DatabaseStep("save_to_database")
        ]
        
        database_pipeline = Pipeline(
            name="database_processing",
            steps=database_steps,
            config={"description": "Database processing pipeline"}
        )
        
        self.register_pipeline("database_processing", database_pipeline)
        
        # API Data Pipeline
        api_steps = [
            APIStep("fetch_api_data"),
            DataValidationStep("validate_api_data"),
            DataTransformationStep("transform_api_data"),
            APIStep("send_api_data")
        ]
        
        api_pipeline = Pipeline(
            name="api_processing",
            steps=api_steps,
            config={"description": "API data processing pipeline"}
        )
        
        self.register_pipeline("api_processing", api_pipeline)
        
        # ML Training Pipeline
        ml_steps = [
            DataValidationStep("validate_training_data"),
            DataCleaningStep("clean_training_data"),
            DataTransformationStep("transform_training_data"),
            # MLTrainingStep would be added here
        ]
        
        ml_pipeline = Pipeline(
            name="ml_training",
            steps=ml_steps,
            config={"description": "Machine learning training pipeline"}
        )
        
        self.register_pipeline("ml_training", ml_pipeline)
        
        self.logger.info("Default pipelines registered")


# Global registry instance
pipeline_registry = PipelineRegistry()


def get_pipeline_registry() -> PipelineRegistry:
    """Get the global pipeline registry instance."""
    return pipeline_registry