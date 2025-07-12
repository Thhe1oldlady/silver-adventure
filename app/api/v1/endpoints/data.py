"""
Data management endpoints.
"""

from fastapi import APIRouter, Request, HTTPException, File, UploadFile
from typing import List, Optional
import json
import time
import uuid
from datetime import datetime

from app.models.schemas import (
    JSONProcessingRequest,
    JSONProcessingResponse,
    DataUploadResponse,
    DataExportRequest
)
from app.services.json_processing_service import JSONProcessingService
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Initialize JSON processing service
json_service = JSONProcessingService()


@router.on_event("startup")
async def startup_event():
    """
    Initialize data management services.
    """
    await json_service.initialize()


@router.post("/upload", response_model=DataUploadResponse)
async def upload_data(file: UploadFile = File(...)):
    """
    Upload JSON data file.
    """
    try:
        # Validate file type
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Only JSON files are supported")
        
        # Read file content
        content = await file.read()
        
        # Validate JSON
        try:
            json_data = json.loads(content)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON format: {e}")
        
        # Generate file ID
        file_id = str(uuid.uuid4())
        
        # Store file info (in a real implementation, you'd store this in a database)
        file_info = {
            "file_id": file_id,
            "filename": file.filename,
            "file_size": len(content),
            "content": json_data,
            "upload_time": datetime.now()
        }
        
        logger.info(f"File uploaded successfully: {file.filename} ({len(content)} bytes)")
        
        return DataUploadResponse(
            file_id=file_id,
            filename=file.filename,
            file_size=len(content)
        )
        
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process", response_model=JSONProcessingResponse)
async def process_json_data(request: JSONProcessingRequest):
    """
    Process JSON data using specified script.
    """
    try:
        result = await json_service.process_json(request)
        
        logger.info(f"JSON processing completed using script: {result.script_used}")
        return result
        
    except Exception as e:
        logger.error(f"JSON processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scripts")
async def get_available_scripts():
    """
    Get list of available JSON processing scripts.
    """
    try:
        scripts = await json_service.get_available_scripts()
        
        script_details = []
        for script in scripts:
            info = await json_service.get_script_info(script)
            script_details.append({
                "name": script,
                "description": info.get("description", ""),
                "options": info.get("options", [])
            })
        
        return {
            "scripts": script_details,
            "count": len(scripts)
        }
        
    except Exception as e:
        logger.error(f"Failed to get scripts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scripts/{script_name}")
async def get_script_info(script_name: str):
    """
    Get information about a specific processing script.
    """
    try:
        script_info = await json_service.get_script_info(script_name)
        
        return {
            "script_name": script_name,
            **script_info
        }
        
    except Exception as e:
        logger.error(f"Failed to get script info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export")
async def export_data(request: DataExportRequest, app_request: Request):
    """
    Export data in specified format.
    """
    try:
        # Get Oracle service from app state
        oracle_service = app_request.app.state.oracle_service
        if not oracle_service or not oracle_service.is_initialized:
            raise HTTPException(status_code=503, detail="Oracle service not available")
        
        # Build query based on filters
        query = f"SELECT * FROM {request.table_name}"
        parameters = {}
        
        if request.filters:
            where_clauses = []
            for field, value in request.filters.items():
                where_clauses.append(f"{field} = :{field}")
                parameters[field] = value
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
        
        # Execute query
        from app.models.schemas import OracleQueryRequest
        query_request = OracleQueryRequest(
            query=query,
            parameters=parameters,
            fetch_size=10000
        )
        
        result = await oracle_service.execute_query(query_request)
        
        # Format data based on requested format
        if request.format == "json":
            exported_data = {
                "table_name": request.table_name,
                "data": result.data,
                "metadata": {
                    "row_count": result.row_count,
                    "columns": result.columns,
                    "export_time": datetime.now().isoformat(),
                    "format": request.format
                }
            }
        elif request.format == "csv":
            # Convert to CSV format (simplified)
            csv_lines = []
            if result.data:
                # Header
                csv_lines.append(",".join(result.columns))
                # Data rows
                for row in result.data:
                    csv_lines.append(",".join(str(row.get(col, "")) for col in result.columns))
            
            exported_data = {
                "table_name": request.table_name,
                "csv_data": "\n".join(csv_lines),
                "metadata": {
                    "row_count": result.row_count,
                    "columns": result.columns,
                    "export_time": datetime.now().isoformat(),
                    "format": request.format
                }
            }
        else:
            # Default to JSON
            exported_data = {
                "table_name": request.table_name,
                "data": result.data,
                "metadata": {
                    "row_count": result.row_count,
                    "columns": result.columns,
                    "export_time": datetime.now().isoformat(),
                    "format": request.format
                }
            }
        
        logger.info(f"Data exported successfully: {request.table_name} ({result.row_count} rows)")
        return exported_data
        
    except Exception as e:
        logger.error(f"Data export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validate")
async def validate_json_data(data: dict, validation_rules: Optional[dict] = None):
    """
    Validate JSON data structure.
    """
    try:
        # Default validation rules
        default_rules = {
            "required_fields": [],
            "field_types": {},
            "value_ranges": {}
        }
        
        rules = validation_rules or default_rules
        
        # Process using validator script
        processing_request = JSONProcessingRequest(
            data=data,
            script_name="data_validator",
            options=rules
        )
        
        result = await json_service.process_json(processing_request)
        
        return {
            "validation_result": result.processed_data,
            "processing_time": result.processing_time
        }
        
    except Exception as e:
        logger.error(f"JSON validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sample-data")
async def get_sample_data():
    """
    Get sample JSON data for testing.
    """
    sample_data = {
        "customer_data": {
            "customer_id": "CUST001",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "age": 35,
            "tenure": 24,
            "monthly_charges": 75.50,
            "total_charges": 1812.00,
            "contract_type": "one-year",
            "payment_method": "credit_card",
            "services": ["internet", "phone", "tv"],
            "last_payment": "2023-12-01"
        },
        "batch_data": {
            "records": [
                {
                    "customer_id": "CUST001",
                    "age": 35,
                    "tenure": 24,
                    "monthly_charges": 75.50,
                    "total_charges": 1812.00
                },
                {
                    "customer_id": "CUST002",
                    "age": 28,
                    "tenure": 12,
                    "monthly_charges": 65.00,
                    "total_charges": 780.00
                }
            ]
        }
    }
    
    return {
        "sample_data": sample_data,
        "description": "Sample JSON data for testing various endpoints"
    }