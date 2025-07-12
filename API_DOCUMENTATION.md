# Oracle FastAPI Integration - API Documentation

## Overview
This application provides a comprehensive solution for Oracle database integration with FastAPI, including machine learning capabilities for churn prediction and JSON data processing.

## Quick Start

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/Thhe1oldlady/silver-adventure.git
cd silver-adventure

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### 2. Run the Application
```bash
# Development mode
./run_dev.sh

# Or directly with uvicorn
uvicorn app.main:app --reload
```

### 3. Access the API
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Health Check
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed health status

### Churn Prediction
- `POST /api/v1/predict/churn` - Predict churn for a single customer
- `POST /api/v1/predict/churn/batch` - Batch churn prediction
- `GET /api/v1/predict/churn/model-info` - Get model information
- `GET /api/v1/predict/churn/feature-importance` - Get feature importance

### Oracle Database
- `GET /api/v1/oracle/status` - Database connection status
- `POST /api/v1/oracle/query` - Execute custom SQL queries
- `GET /api/v1/oracle/tables` - List available tables
- `GET /api/v1/oracle/tables/{table_name}` - Get table information
- `GET /api/v1/oracle/test-connection` - Test database connection
- `GET /api/v1/oracle/sample-queries` - Get sample queries

### Data Management
- `POST /api/v1/data/upload` - Upload JSON data files
- `POST /api/v1/data/process` - Process JSON data with scripts
- `GET /api/v1/data/scripts` - List available processing scripts
- `GET /api/v1/data/scripts/{script_name}` - Get script information
- `POST /api/v1/data/export` - Export data in various formats
- `GET /api/v1/data/validate` - Validate JSON data
- `GET /api/v1/data/sample-data` - Get sample data for testing

## Usage Examples

### Churn Prediction
```bash
curl -X POST "http://localhost:8000/api/v1/predict/churn" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST001",
    "features": {
      "age": 35,
      "tenure": 24,
      "monthly_charges": 75.50,
      "total_charges": 1812.00,
      "contract_type": "one-year",
      "payment_method": "credit_card"
    }
  }'
```

### Oracle Query
```bash
curl -X POST "http://localhost:8000/api/v1/oracle/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM customers WHERE age > :age",
    "parameters": {"age": 30},
    "fetch_size": 100
  }'
```

### JSON Processing
```bash
curl -X POST "http://localhost:8000/api/v1/data/process" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "name": "John Doe",
      "email": "john@example.com",
      "age": 35,
      "phone": null
    },
    "script_name": "data_cleaner",
    "options": {
      "remove_nulls": true,
      "remove_empty_strings": true
    }
  }'
```

## Configuration

### Environment Variables
- `ORACLE_HOST`: Oracle database host
- `ORACLE_PORT`: Oracle database port
- `ORACLE_SERVICE`: Oracle service name
- `ORACLE_USER`: Oracle username
- `ORACLE_PASSWORD`: Oracle password
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `DEBUG`: Enable debug mode

### JSON Processing Scripts
Available scripts for data processing:
- `data_cleaner`: Remove null values and empty strings
- `data_validator`: Validate data structure and content
- `data_transformer`: Transform data structure and values
- `data_aggregator`: Aggregate data by groups
- `data_filter`: Filter data based on criteria
- `data_enricher`: Enrich data with additional information

### Machine Learning Features
The churn prediction model uses the following features:
- `age`: Customer age
- `tenure`: Number of months as customer
- `monthly_charges`: Monthly charges amount
- `total_charges`: Total charges amount
- `contract_type`: Type of contract (month-to-month, one-year, two-year)
- `payment_method`: Payment method (credit_card, bank_transfer, etc.)

## Testing

Run the test suite:
```bash
python test_app.py
```

## Docker Support

Build and run with Docker:
```bash
# Build the image
docker build -t oracle-fastapi-integration .

# Run the container
docker run -p 8000:8000 oracle-fastapi-integration
```

Use Docker Compose for full stack:
```bash
docker-compose up
```

## Monitoring

The application includes:
- Prometheus metrics endpoint
- Structured JSON logging
- Health check endpoints
- Performance monitoring

## Error Handling

The application includes comprehensive error handling:
- Input validation
- Database connection errors
- Model prediction errors
- File upload errors
- Query execution errors

## Security

Security features:
- Input validation
- SQL injection protection
- File upload restrictions
- Error message sanitization
- Connection pooling

## Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the logs in the `logs/` directory
3. Use the health check endpoints to diagnose issues
4. Refer to the sample data and queries provided