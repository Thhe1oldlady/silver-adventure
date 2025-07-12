"""Core pipeline components."""

import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime

from ..core.pipeline import PipelineStep, PipelineContext
from ..core.logger import get_logger


class DataValidationStep(PipelineStep):
    """Step for validating data quality and structure."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.validation_rules = self.config.get("validation_rules", {})
    
    def execute(self, context: PipelineContext) -> PipelineContext:
        """Execute data validation."""
        data = context.data
        
        # Basic validation
        if data is None:
            raise ValueError("No data provided for validation")
        
        # DataFrame validation
        if isinstance(data, pd.DataFrame):
            self._validate_dataframe(data, context)
        elif isinstance(data, dict):
            self._validate_dict(data, context)
        elif isinstance(data, list):
            self._validate_list(data, context)
        else:
            self.logger.warning(f"Unknown data type for validation: {type(data)}")
        
        # Update metadata
        context.update_metadata(
            validation_passed=True,
            validation_time=datetime.utcnow().isoformat(),
            data_type=str(type(data)),
            data_size=len(data) if hasattr(data, '__len__') else 1
        )
        
        return context
    
    def _validate_dataframe(self, df: pd.DataFrame, context: PipelineContext) -> None:
        """Validate DataFrame."""
        # Check for empty DataFrame
        if df.empty:
            raise ValueError("DataFrame is empty")
        
        # Check for required columns
        required_columns = self.validation_rules.get("required_columns", [])
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Check for null values
        if self.validation_rules.get("no_nulls", False):
            null_counts = df.isnull().sum()
            if null_counts.any():
                raise ValueError(f"Null values found: {null_counts[null_counts > 0].to_dict()}")
        
        # Check data types
        expected_types = self.validation_rules.get("column_types", {})
        for column, expected_type in expected_types.items():
            if column in df.columns:
                if not df[column].dtype.name.startswith(expected_type):
                    raise ValueError(f"Column '{column}' has wrong type: {df[column].dtype}")
        
        # Update context metadata
        context.update_metadata(
            rows=len(df),
            columns=len(df.columns),
            column_names=list(df.columns),
            null_counts=df.isnull().sum().to_dict()
        )
    
    def _validate_dict(self, data: Dict, context: PipelineContext) -> None:
        """Validate dictionary data."""
        # Check for required keys
        required_keys = self.validation_rules.get("required_keys", [])
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            raise ValueError(f"Missing required keys: {missing_keys}")
        
        # Update context metadata
        context.update_metadata(
            keys=list(data.keys()),
            key_count=len(data)
        )
    
    def _validate_list(self, data: List, context: PipelineContext) -> None:
        """Validate list data."""
        if not data:
            raise ValueError("List is empty")
        
        # Check minimum length
        min_length = self.validation_rules.get("min_length", 0)
        if len(data) < min_length:
            raise ValueError(f"List too short: {len(data)} < {min_length}")
        
        # Update context metadata
        context.update_metadata(
            list_length=len(data),
            item_types=[str(type(item)) for item in data[:10]]  # First 10 items
        )


class DataCleaningStep(PipelineStep):
    """Step for cleaning and preprocessing data."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.cleaning_rules = self.config.get("cleaning_rules", {})
    
    def execute(self, context: PipelineContext) -> PipelineContext:
        """Execute data cleaning."""
        data = context.data
        
        if isinstance(data, pd.DataFrame):
            cleaned_data = self._clean_dataframe(data, context)
        elif isinstance(data, dict):
            cleaned_data = self._clean_dict(data, context)
        elif isinstance(data, list):
            cleaned_data = self._clean_list(data, context)
        else:
            cleaned_data = data
        
        context.data = cleaned_data
        context.update_metadata(
            cleaned=True,
            cleaning_time=datetime.utcnow().isoformat()
        )
        
        return context
    
    def _clean_dataframe(self, df: pd.DataFrame, context: PipelineContext) -> pd.DataFrame:
        """Clean DataFrame."""
        df_cleaned = df.copy()
        
        # Remove duplicates
        if self.cleaning_rules.get("remove_duplicates", True):
            initial_rows = len(df_cleaned)
            df_cleaned = df_cleaned.drop_duplicates()
            removed_duplicates = initial_rows - len(df_cleaned)
            context.update_metadata(removed_duplicates=removed_duplicates)
        
        # Handle null values
        null_strategy = self.cleaning_rules.get("null_strategy", "remove")
        if null_strategy == "remove":
            df_cleaned = df_cleaned.dropna()
        elif null_strategy == "fill":
            fill_values = self.cleaning_rules.get("fill_values", {})
            df_cleaned = df_cleaned.fillna(fill_values)
        
        # Remove outliers (simple IQR method)
        if self.cleaning_rules.get("remove_outliers", False):
            numeric_columns = df_cleaned.select_dtypes(include=[np.number]).columns
            for column in numeric_columns:
                Q1 = df_cleaned[column].quantile(0.25)
                Q3 = df_cleaned[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                df_cleaned = df_cleaned[
                    (df_cleaned[column] >= lower_bound) & 
                    (df_cleaned[column] <= upper_bound)
                ]
        
        # Standardize text columns
        if self.cleaning_rules.get("standardize_text", False):
            text_columns = df_cleaned.select_dtypes(include=['object']).columns
            for column in text_columns:
                df_cleaned[column] = df_cleaned[column].str.strip().str.lower()
        
        return df_cleaned
    
    def _clean_dict(self, data: Dict, context: PipelineContext) -> Dict:
        """Clean dictionary data."""
        cleaned_data = {}
        
        for key, value in data.items():
            # Remove None values
            if value is not None:
                # Clean string values
                if isinstance(value, str):
                    cleaned_value = value.strip()
                    if cleaned_value:
                        cleaned_data[key] = cleaned_value
                else:
                    cleaned_data[key] = value
        
        return cleaned_data
    
    def _clean_list(self, data: List, context: PipelineContext) -> List:
        """Clean list data."""
        # Remove None values and empty strings
        cleaned_data = [
            item for item in data 
            if item is not None and (not isinstance(item, str) or item.strip())
        ]
        
        return cleaned_data


class DataTransformationStep(PipelineStep):
    """Step for transforming data."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.transformations = self.config.get("transformations", [])
    
    def execute(self, context: PipelineContext) -> PipelineContext:
        """Execute data transformation."""
        data = context.data
        
        if isinstance(data, pd.DataFrame):
            transformed_data = self._transform_dataframe(data, context)
        elif isinstance(data, dict):
            transformed_data = self._transform_dict(data, context)
        elif isinstance(data, list):
            transformed_data = self._transform_list(data, context)
        else:
            transformed_data = data
        
        context.data = transformed_data
        context.update_metadata(
            transformed=True,
            transformation_time=datetime.utcnow().isoformat()
        )
        
        return context
    
    def _transform_dataframe(self, df: pd.DataFrame, context: PipelineContext) -> pd.DataFrame:
        """Transform DataFrame."""
        df_transformed = df.copy()
        
        for transformation in self.transformations:
            transform_type = transformation.get("type")
            
            if transform_type == "add_column":
                column_name = transformation["column"]
                column_value = transformation.get("value", 0)
                df_transformed[column_name] = column_value
            
            elif transform_type == "drop_column":
                column_name = transformation["column"]
                if column_name in df_transformed.columns:
                    df_transformed = df_transformed.drop(column_name, axis=1)
            
            elif transform_type == "rename_column":
                old_name = transformation["old_name"]
                new_name = transformation["new_name"]
                df_transformed = df_transformed.rename(columns={old_name: new_name})
            
            elif transform_type == "convert_type":
                column_name = transformation["column"]
                target_type = transformation["target_type"]
                if column_name in df_transformed.columns:
                    df_transformed[column_name] = df_transformed[column_name].astype(target_type)
            
            elif transform_type == "normalize":
                column_name = transformation["column"]
                if column_name in df_transformed.columns:
                    col_min = df_transformed[column_name].min()
                    col_max = df_transformed[column_name].max()
                    df_transformed[column_name] = (df_transformed[column_name] - col_min) / (col_max - col_min)
            
            elif transform_type == "aggregate":
                group_by = transformation.get("group_by", [])
                agg_columns = transformation.get("agg_columns", {})
                if group_by and agg_columns:
                    df_transformed = df_transformed.groupby(group_by).agg(agg_columns).reset_index()
        
        return df_transformed
    
    def _transform_dict(self, data: Dict, context: PipelineContext) -> Dict:
        """Transform dictionary data."""
        transformed_data = data.copy()
        
        for transformation in self.transformations:
            transform_type = transformation.get("type")
            
            if transform_type == "add_key":
                key = transformation["key"]
                value = transformation.get("value", None)
                transformed_data[key] = value
            
            elif transform_type == "remove_key":
                key = transformation["key"]
                if key in transformed_data:
                    del transformed_data[key]
            
            elif transform_type == "rename_key":
                old_key = transformation["old_key"]
                new_key = transformation["new_key"]
                if old_key in transformed_data:
                    transformed_data[new_key] = transformed_data.pop(old_key)
        
        return transformed_data
    
    def _transform_list(self, data: List, context: PipelineContext) -> List:
        """Transform list data."""
        transformed_data = data.copy()
        
        for transformation in self.transformations:
            transform_type = transformation.get("type")
            
            if transform_type == "sort":
                reverse = transformation.get("reverse", False)
                transformed_data = sorted(transformed_data, reverse=reverse)
            
            elif transform_type == "filter":
                filter_func = transformation.get("filter_function")
                if filter_func and callable(filter_func):
                    transformed_data = [item for item in transformed_data if filter_func(item)]
            
            elif transform_type == "map":
                map_func = transformation.get("map_function")
                if map_func and callable(map_func):
                    transformed_data = [map_func(item) for item in transformed_data]
        
        return transformed_data


class AggregationStep(PipelineStep):
    """Step for aggregating data."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.aggregation_config = self.config.get("aggregation", {})
    
    def execute(self, context: PipelineContext) -> PipelineContext:
        """Execute data aggregation."""
        data = context.data
        
        if isinstance(data, pd.DataFrame):
            aggregated_data = self._aggregate_dataframe(data, context)
        elif isinstance(data, list):
            aggregated_data = self._aggregate_list(data, context)
        else:
            aggregated_data = data
        
        context.data = aggregated_data
        context.update_metadata(
            aggregated=True,
            aggregation_time=datetime.utcnow().isoformat()
        )
        
        return context
    
    def _aggregate_dataframe(self, df: pd.DataFrame, context: PipelineContext) -> pd.DataFrame:
        """Aggregate DataFrame."""
        group_by = self.aggregation_config.get("group_by", [])
        agg_functions = self.aggregation_config.get("functions", {})
        
        if group_by and agg_functions:
            return df.groupby(group_by).agg(agg_functions).reset_index()
        
        return df
    
    def _aggregate_list(self, data: List, context: PipelineContext) -> Dict:
        """Aggregate list data."""
        return {
            "count": len(data),
            "sum": sum(data) if all(isinstance(x, (int, float)) for x in data) else None,
            "average": sum(data) / len(data) if all(isinstance(x, (int, float)) for x in data) else None,
            "min": min(data) if data else None,
            "max": max(data) if data else None
        }