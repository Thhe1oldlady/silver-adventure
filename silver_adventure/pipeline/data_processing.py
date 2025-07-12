"""Data processing pipeline components."""

import pandas as pd
import json
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import httpx
from datetime import datetime

from ..core.pipeline import PipelineStep, PipelineContext
from ..core.config import get_config
from ..core.logger import get_logger

try:
    import sqlalchemy
    from sqlalchemy import create_engine, text
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False


class CSVProcessingStep(PipelineStep):
    """Step for processing CSV files."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.file_path = self.config.get("file_path", "")
        self.operation = self.config.get("operation", "load")  # load, save
        self.csv_options = self.config.get("csv_options", {})
    
    def execute(self, context: PipelineContext) -> PipelineContext:
        """Execute CSV processing."""
        if self.operation == "load":
            return self._load_csv(context)
        elif self.operation == "save":
            return self._save_csv(context)
        else:
            raise ValueError(f"Unknown operation: {self.operation}")
    
    def _load_csv(self, context: PipelineContext) -> PipelineContext:
        """Load data from CSV file."""
        # Use file path from config or context
        file_path = self.file_path or context.get_metadata("file_path")
        
        if not file_path:
            raise ValueError("No file path provided for CSV loading")
        
        # Check if file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        # Load CSV with pandas
        try:
            df = pd.read_csv(file_path, **self.csv_options)
            context.data = df
            
            # Update metadata
            context.update_metadata(
                file_path=file_path,
                rows_loaded=len(df),
                columns_loaded=len(df.columns),
                column_names=list(df.columns),
                load_time=datetime.utcnow().isoformat()
            )
            
            self.logger.info(f"Loaded CSV file: {file_path} ({len(df)} rows)")
            
        except Exception as e:
            self.logger.error(f"Failed to load CSV file: {str(e)}")
            raise
        
        return context
    
    def _save_csv(self, context: PipelineContext) -> PipelineContext:
        """Save data to CSV file."""
        data = context.data
        
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Data must be a pandas DataFrame to save as CSV")
        
        # Use file path from config or context
        file_path = self.file_path or context.get_metadata("output_file_path")
        
        if not file_path:
            raise ValueError("No file path provided for CSV saving")
        
        # Ensure directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save CSV
        try:
            data.to_csv(file_path, index=False, **self.csv_options)
            
            # Update metadata
            context.update_metadata(
                output_file_path=file_path,
                rows_saved=len(data),
                columns_saved=len(data.columns),
                save_time=datetime.utcnow().isoformat()
            )
            
            self.logger.info(f"Saved CSV file: {file_path} ({len(data)} rows)")
            
        except Exception as e:
            self.logger.error(f"Failed to save CSV file: {str(e)}")
            raise
        
        return context


class DatabaseStep(PipelineStep):
    """Step for database operations."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.operation = self.config.get("operation", "load")  # load, save
        self.table_name = self.config.get("table_name", "")
        self.query = self.config.get("query", "")
        self.connection_string = self.config.get("connection_string", "")
    
    def execute(self, context: PipelineContext) -> PipelineContext:
        """Execute database operation."""
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError("sqlalchemy is required for database operations")
        
        if self.operation == "load":
            return self._load_from_database(context)
        elif self.operation == "save":
            return self._save_to_database(context)
        else:
            raise ValueError(f"Unknown operation: {self.operation}")
    
    def _load_from_database(self, context: PipelineContext) -> PipelineContext:
        """Load data from database."""
        # Get connection string
        connection_string = self._get_connection_string(context)
        
        # Create engine
        engine = create_engine(connection_string)
        
        try:
            # Execute query
            query = self.query or f"SELECT * FROM {self.table_name}"
            df = pd.read_sql(query, engine)
            
            context.data = df
            
            # Update metadata
            context.update_metadata(
                table_name=self.table_name,
                query=query,
                rows_loaded=len(df),
                columns_loaded=len(df.columns),
                column_names=list(df.columns),
                load_time=datetime.utcnow().isoformat()
            )
            
            self.logger.info(f"Loaded from database: {self.table_name} ({len(df)} rows)")
            
        except Exception as e:
            self.logger.error(f"Failed to load from database: {str(e)}")
            raise
        finally:
            engine.dispose()
        
        return context
    
    def _save_to_database(self, context: PipelineContext) -> PipelineContext:
        """Save data to database."""
        data = context.data
        
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Data must be a pandas DataFrame to save to database")
        
        # Get connection string
        connection_string = self._get_connection_string(context)
        
        # Create engine
        engine = create_engine(connection_string)
        
        try:
            # Save to database
            table_name = self.table_name or context.get_metadata("table_name")
            if not table_name:
                raise ValueError("No table name provided")
            
            data.to_sql(table_name, engine, if_exists='replace', index=False)
            
            # Update metadata
            context.update_metadata(
                table_name=table_name,
                rows_saved=len(data),
                columns_saved=len(data.columns),
                save_time=datetime.utcnow().isoformat()
            )
            
            self.logger.info(f"Saved to database: {table_name} ({len(data)} rows)")
            
        except Exception as e:
            self.logger.error(f"Failed to save to database: {str(e)}")
            raise
        finally:
            engine.dispose()
        
        return context
    
    def _get_connection_string(self, context: PipelineContext) -> str:
        """Get database connection string."""
        if self.connection_string:
            return self.connection_string
        
        # Use default configuration
        config = get_config()
        return config.database.postgres_url


class APIStep(PipelineStep):
    """Step for API operations."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.operation = self.config.get("operation", "get")  # get, post, put, delete
        self.url = self.config.get("url", "")
        self.headers = self.config.get("headers", {})
        self.params = self.config.get("params", {})
        self.timeout = self.config.get("timeout", 30)
    
    def execute(self, context: PipelineContext) -> PipelineContext:
        """Execute API operation."""
        if self.operation == "get":
            return self._api_get(context)
        elif self.operation == "post":
            return self._api_post(context)
        elif self.operation == "put":
            return self._api_put(context)
        elif self.operation == "delete":
            return self._api_delete(context)
        else:
            raise ValueError(f"Unknown operation: {self.operation}")
    
    def _api_get(self, context: PipelineContext) -> PipelineContext:
        """Execute GET request."""
        url = self.url or context.get_metadata("api_url")
        
        if not url:
            raise ValueError("No URL provided for API GET")
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=self.headers, params=self.params)
                response.raise_for_status()
                
                # Parse response
                if response.headers.get("content-type", "").startswith("application/json"):
                    data = response.json()
                else:
                    data = response.text
                
                context.data = data
                
                # Update metadata
                context.update_metadata(
                    api_url=url,
                    response_status=response.status_code,
                    response_headers=dict(response.headers),
                    request_time=datetime.utcnow().isoformat()
                )
                
                self.logger.info(f"API GET successful: {url}")
                
        except Exception as e:
            self.logger.error(f"API GET failed: {str(e)}")
            raise
        
        return context
    
    def _api_post(self, context: PipelineContext) -> PipelineContext:
        """Execute POST request."""
        url = self.url or context.get_metadata("api_url")
        
        if not url:
            raise ValueError("No URL provided for API POST")
        
        # Use context data as payload
        payload = context.data
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload, headers=self.headers, params=self.params)
                response.raise_for_status()
                
                # Parse response
                if response.headers.get("content-type", "").startswith("application/json"):
                    data = response.json()
                else:
                    data = response.text
                
                context.data = data
                
                # Update metadata
                context.update_metadata(
                    api_url=url,
                    response_status=response.status_code,
                    response_headers=dict(response.headers),
                    request_time=datetime.utcnow().isoformat()
                )
                
                self.logger.info(f"API POST successful: {url}")
                
        except Exception as e:
            self.logger.error(f"API POST failed: {str(e)}")
            raise
        
        return context
    
    def _api_put(self, context: PipelineContext) -> PipelineContext:
        """Execute PUT request."""
        url = self.url or context.get_metadata("api_url")
        
        if not url:
            raise ValueError("No URL provided for API PUT")
        
        # Use context data as payload
        payload = context.data
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.put(url, json=payload, headers=self.headers, params=self.params)
                response.raise_for_status()
                
                # Parse response
                if response.headers.get("content-type", "").startswith("application/json"):
                    data = response.json()
                else:
                    data = response.text
                
                context.data = data
                
                # Update metadata
                context.update_metadata(
                    api_url=url,
                    response_status=response.status_code,
                    response_headers=dict(response.headers),
                    request_time=datetime.utcnow().isoformat()
                )
                
                self.logger.info(f"API PUT successful: {url}")
                
        except Exception as e:
            self.logger.error(f"API PUT failed: {str(e)}")
            raise
        
        return context
    
    def _api_delete(self, context: PipelineContext) -> PipelineContext:
        """Execute DELETE request."""
        url = self.url or context.get_metadata("api_url")
        
        if not url:
            raise ValueError("No URL provided for API DELETE")
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.delete(url, headers=self.headers, params=self.params)
                response.raise_for_status()
                
                # Parse response
                if response.headers.get("content-type", "").startswith("application/json"):
                    data = response.json()
                else:
                    data = response.text
                
                context.data = data
                
                # Update metadata
                context.update_metadata(
                    api_url=url,
                    response_status=response.status_code,
                    response_headers=dict(response.headers),
                    request_time=datetime.utcnow().isoformat()
                )
                
                self.logger.info(f"API DELETE successful: {url}")
                
        except Exception as e:
            self.logger.error(f"API DELETE failed: {str(e)}")
            raise
        
        return context


class JSONProcessingStep(PipelineStep):
    """Step for processing JSON files."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.file_path = self.config.get("file_path", "")
        self.operation = self.config.get("operation", "load")  # load, save
    
    def execute(self, context: PipelineContext) -> PipelineContext:
        """Execute JSON processing."""
        if self.operation == "load":
            return self._load_json(context)
        elif self.operation == "save":
            return self._save_json(context)
        else:
            raise ValueError(f"Unknown operation: {self.operation}")
    
    def _load_json(self, context: PipelineContext) -> PipelineContext:
        """Load data from JSON file."""
        # Use file path from config or context
        file_path = self.file_path or context.get_metadata("file_path")
        
        if not file_path:
            raise ValueError("No file path provided for JSON loading")
        
        # Check if file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(f"JSON file not found: {file_path}")
        
        # Load JSON
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            context.data = data
            
            # Update metadata
            context.update_metadata(
                file_path=file_path,
                data_type=type(data).__name__,
                load_time=datetime.utcnow().isoformat()
            )
            
            self.logger.info(f"Loaded JSON file: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to load JSON file: {str(e)}")
            raise
        
        return context
    
    def _save_json(self, context: PipelineContext) -> PipelineContext:
        """Save data to JSON file."""
        data = context.data
        
        # Use file path from config or context
        file_path = self.file_path or context.get_metadata("output_file_path")
        
        if not file_path:
            raise ValueError("No file path provided for JSON saving")
        
        # Ensure directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            # Update metadata
            context.update_metadata(
                output_file_path=file_path,
                data_type=type(data).__name__,
                save_time=datetime.utcnow().isoformat()
            )
            
            self.logger.info(f"Saved JSON file: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save JSON file: {str(e)}")
            raise
        
        return context