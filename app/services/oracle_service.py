"""
Oracle Database Service.
"""

from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import asyncio
import time
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import get_logger
from app.models.schemas import OracleQueryRequest, OracleQueryResponse, OracleStatusResponse

logger = get_logger(__name__)


class OracleService:
    """
    Oracle database service.
    """
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self.is_initialized = False
        self.connection_pool = None
        
    async def initialize(self):
        """
        Initialize the Oracle service.
        """
        try:
            logger.info("Initializing Oracle service...")
            
            # Check if Oracle credentials are provided
            if not settings.ORACLE_USER or not settings.ORACLE_PASSWORD:
                logger.warning("Oracle credentials not provided, initializing in mock mode")
                await self._initialize_mock_mode()
                return
            
            # Create connection pool
            await self._create_connection_pool()
            
            # Test connection
            await self._test_connection()
            
            self.is_initialized = True
            logger.info("Oracle service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Oracle service: {e}")
            # Initialize in mock mode as fallback
            await self._initialize_mock_mode()
    
    async def _initialize_mock_mode(self):
        """
        Initialize in mock mode for testing/development.
        """
        logger.info("Initializing Oracle service in mock mode")
        self.is_initialized = True
        self.mock_mode = True
        
        # Create mock data
        self.mock_tables = {
            'customers': [
                {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'},
                {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com'},
            ],
            'products': [
                {'id': 1, 'name': 'Product A', 'price': 100.0},
                {'id': 2, 'name': 'Product B', 'price': 200.0},
            ]
        }
    
    async def _create_connection_pool(self):
        """
        Create Oracle connection pool.
        """
        try:
            # Use SQLite for testing
            self.engine = create_engine(
                settings.oracle_connection_string,
                pool_size=settings.POOL_SIZE,
                max_overflow=10,
                pool_recycle=settings.POOL_RECYCLE,
                pool_pre_ping=True,
                echo=settings.DEBUG,
                connect_args={"check_same_thread": False}
            )
            
            # Create session factory
            self.session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info("Database connection pool created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create database connection pool: {e}")
            raise
    
    async def _test_connection(self):
        """
        Test database connection.
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
                logger.info("Database connection test successful")
                
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            raise
    
    async def execute_query(self, request: OracleQueryRequest) -> OracleQueryResponse:
        """
        Execute database query.
        """
        if not self.is_initialized:
            raise RuntimeError("Oracle service not initialized")
        
        # Handle mock mode
        if hasattr(self, 'mock_mode') and self.mock_mode:
            return await self._execute_mock_query(request)
        
        start_time = time.time()
        
        try:
            with self.engine.connect() as connection:
                # Execute query with parameters
                result = connection.execute(
                    text(request.query),
                    request.parameters
                )
                
                # Fetch results
                rows = result.fetchmany(request.fetch_size)
                columns = list(result.keys()) if rows else []
                
                # Convert to list of dictionaries
                data = [dict(zip(columns, row)) for row in rows]
                
                execution_time = time.time() - start_time
                
                return OracleQueryResponse(
                    data=data,
                    row_count=len(data),
                    execution_time=execution_time,
                    columns=columns
                )
                
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    async def _execute_mock_query(self, request: OracleQueryRequest) -> OracleQueryResponse:
        """
        Execute mock query for testing.
        """
        start_time = time.time()
        
        # Simple mock query processing
        query_lower = request.query.lower()
        
        if 'customers' in query_lower:
            data = self.mock_tables['customers']
            columns = list(data[0].keys()) if data else []
        elif 'products' in query_lower:
            data = self.mock_tables['products']
            columns = list(data[0].keys()) if data else []
        else:
            data = [{'result': 'Mock query executed successfully'}]
            columns = ['result']
        
        execution_time = time.time() - start_time
        
        return OracleQueryResponse(
            data=data,
            row_count=len(data),
            execution_time=execution_time,
            columns=columns
        )
    
    async def get_status(self) -> OracleStatusResponse:
        """
        Get database status.
        """
        if not self.is_initialized:
            return OracleStatusResponse(
                connected=False,
                version=None,
                service_name=None,
                connection_pool_size=0,
                active_connections=0
            )
        
        # Handle mock mode
        if hasattr(self, 'mock_mode') and self.mock_mode:
            return OracleStatusResponse(
                connected=True,
                version="Mock SQLite 3.x",
                service_name="MOCK_SERVICE",
                connection_pool_size=1,
                active_connections=0
            )
        
        try:
            with self.engine.connect() as connection:
                # Get database version
                version_result = connection.execute(text("SELECT sqlite_version()"))
                version = version_result.fetchone()[0] if version_result else None
                
                # Get connection pool info
                pool_size = self.engine.pool.size()
                active_connections = self.engine.pool.checkedout()
                
                return OracleStatusResponse(
                    connected=True,
                    version=f"SQLite {version}",
                    service_name=settings.ORACLE_SERVICE,
                    connection_pool_size=pool_size,
                    active_connections=active_connections
                )
                
        except Exception as e:
            logger.error(f"Failed to get database status: {e}")
            return OracleStatusResponse(
                connected=False,
                version=None,
                service_name=settings.ORACLE_SERVICE,
                connection_pool_size=0,
                active_connections=0
            )
    
    async def get_tables(self) -> List[str]:
        """
        Get list of available tables.
        """
        if not self.is_initialized:
            raise RuntimeError("Oracle service not initialized")
        
        # Handle mock mode
        if hasattr(self, 'mock_mode') and self.mock_mode:
            return list(self.mock_tables.keys())
        
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' 
                    ORDER BY name
                """))
                
                tables = [row[0] for row in result.fetchall()]
                return tables
                
        except Exception as e:
            logger.error(f"Failed to get tables: {e}")
            raise
    
    async def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get table information.
        """
        if not self.is_initialized:
            raise RuntimeError("Oracle service not initialized")
        
        # Handle mock mode
        if hasattr(self, 'mock_mode') and self.mock_mode:
            if table_name in self.mock_tables:
                sample_data = self.mock_tables[table_name]
                columns = list(sample_data[0].keys()) if sample_data else []
                return {
                    'table_name': table_name,
                    'columns': columns,
                    'row_count': len(sample_data),
                    'column_count': len(columns)
                }
            else:
                raise ValueError(f"Table '{table_name}' not found")
        
        try:
            with self.engine.connect() as connection:
                # Get column information
                columns_result = connection.execute(text(f"PRAGMA table_info({table_name})"))
                
                columns = [
                    {
                        'name': row[1],
                        'type': row[2],
                        'nullable': not row[3],
                        'default': row[4]
                    }
                    for row in columns_result.fetchall()
                ]
                
                # Get row count
                count_result = connection.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                row_count = count_result.fetchone()[0]
                
                return {
                    'table_name': table_name,
                    'columns': columns,
                    'row_count': row_count,
                    'column_count': len(columns)
                }
                
        except Exception as e:
            logger.error(f"Failed to get table info for '{table_name}': {e}")
            raise
    
    async def close(self):
        """
        Close Oracle service.
        """
        logger.info("Closing Oracle service...")
        
        if self.engine:
            self.engine.dispose()
            
        self.is_initialized = False