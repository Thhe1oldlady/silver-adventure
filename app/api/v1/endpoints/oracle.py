"""
Oracle database endpoints.
"""

from fastapi import APIRouter, Request, HTTPException
from typing import List

from app.models.schemas import (
    OracleQueryRequest,
    OracleQueryResponse,
    OracleStatusResponse
)
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/status", response_model=OracleStatusResponse)
async def get_oracle_status(app_request: Request):
    """
    Get Oracle database status.
    """
    try:
        # Get Oracle service from app state
        oracle_service = app_request.app.state.oracle_service
        if not oracle_service:
            raise HTTPException(status_code=503, detail="Oracle service not available")
        
        status = await oracle_service.get_status()
        return status
        
    except Exception as e:
        logger.error(f"Failed to get Oracle status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=OracleQueryResponse)
async def execute_query(request: OracleQueryRequest, app_request: Request):
    """
    Execute Oracle query.
    """
    try:
        # Get Oracle service from app state
        oracle_service = app_request.app.state.oracle_service
        if not oracle_service or not oracle_service.is_initialized:
            raise HTTPException(status_code=503, detail="Oracle service not available")
        
        # Execute query
        result = await oracle_service.execute_query(request)
        
        logger.info(f"Query executed successfully, returned {result.row_count} rows")
        return result
        
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tables")
async def get_tables(app_request: Request):
    """
    Get list of available tables.
    """
    try:
        # Get Oracle service from app state
        oracle_service = app_request.app.state.oracle_service
        if not oracle_service or not oracle_service.is_initialized:
            raise HTTPException(status_code=503, detail="Oracle service not available")
        
        tables = await oracle_service.get_tables()
        
        return {
            "tables": tables,
            "count": len(tables)
        }
        
    except Exception as e:
        logger.error(f"Failed to get tables: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tables/{table_name}")
async def get_table_info(table_name: str, app_request: Request):
    """
    Get information about a specific table.
    """
    try:
        # Get Oracle service from app state
        oracle_service = app_request.app.state.oracle_service
        if not oracle_service or not oracle_service.is_initialized:
            raise HTTPException(status_code=503, detail="Oracle service not available")
        
        table_info = await oracle_service.get_table_info(table_name)
        
        return table_info
        
    except Exception as e:
        logger.error(f"Failed to get table info for '{table_name}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-connection")
async def test_connection(app_request: Request):
    """
    Test Oracle database connection.
    """
    try:
        # Get Oracle service from app state
        oracle_service = app_request.app.state.oracle_service
        if not oracle_service:
            raise HTTPException(status_code=503, detail="Oracle service not available")
        
        # Test with a simple query
        test_query = OracleQueryRequest(
            query="SELECT 1 as test_value FROM DUAL",
            fetch_size=1
        )
        
        result = await oracle_service.execute_query(test_query)
        
        return {
            "connection_test": "successful",
            "query_result": result.data,
            "execution_time": result.execution_time
        }
        
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sample-queries")
async def get_sample_queries():
    """
    Get sample Oracle queries for testing.
    """
    sample_queries = [
        {
            "name": "Test Connection",
            "query": "SELECT 1 as test_value FROM DUAL",
            "description": "Simple test query to verify connection"
        },
        {
            "name": "Current Date",
            "query": "SELECT SYSDATE as current_date FROM DUAL",
            "description": "Get current database date"
        },
        {
            "name": "Database Version",
            "query": "SELECT banner FROM v$version WHERE rownum = 1",
            "description": "Get Oracle database version"
        },
        {
            "name": "User Tables",
            "query": "SELECT table_name FROM user_tables ORDER BY table_name",
            "description": "List all user tables"
        },
        {
            "name": "Session Info",
            "query": "SELECT username, osuser, program FROM v$session WHERE username = USER",
            "description": "Get current session information"
        }
    ]
    
    return {
        "sample_queries": sample_queries,
        "count": len(sample_queries)
    }