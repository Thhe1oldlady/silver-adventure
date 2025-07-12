# Oracle Tech Integration with FastAPI and Churn Prediction

A comprehensive FastAPI application that integrates Oracle technology with machine learning capabilities for churn prediction and real-time data processing.

## Features

- **FastAPI Integration**: High-performance API endpoints for real-time requests
- **Churn Prediction**: Machine learning algorithms for customer churn prediction
- **Oracle Database Integration**: Seamless connectivity with Oracle databases
- **JSON Script Handling**: Comprehensive JSON data processing capabilities
- **Modular Architecture**: Clean, scalable, and maintainable code structure
- **Professional Logging**: Comprehensive logging and error handling
- **Network Optimization**: Configured for scalability and performance

## Project Structure

```
silver-adventure/
├── app/
│   ├── api/                 # FastAPI route definitions
│   ├── core/                # Core application configuration
│   ├── models/              # Data models and schemas
│   ├── services/            # Business logic services
│   ├── utils/               # Utility functions
│   ├── db/                  # Database connection and operations
│   └── scripts/             # JSON processing scripts
├── config/                  # Configuration files
├── tests/                   # Test files
├── data/                    # Data files
├── logs/                    # Application logs
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Thhe1oldlady/silver-adventure.git
cd silver-adventure
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Health Check
- `GET /health` - Application health status

### Churn Prediction
- `POST /predict/churn` - Predict customer churn probability
- `GET /predict/churn/batch` - Batch churn prediction

### Data Management
- `POST /data/upload` - Upload JSON data
- `GET /data/process` - Process uploaded data
- `GET /data/export` - Export processed data

### Oracle Integration
- `GET /oracle/status` - Oracle database connection status
- `POST /oracle/query` - Execute custom Oracle queries
- `GET /oracle/tables` - List available tables

## Configuration

The application uses environment variables for configuration:

- `ORACLE_HOST`: Oracle database host
- `ORACLE_PORT`: Oracle database port
- `ORACLE_SERVICE`: Oracle service name
- `ORACLE_USER`: Oracle username
- `ORACLE_PASSWORD`: Oracle password
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `REDIS_URL`: Redis connection URL for caching

## Machine Learning Models

The application includes pre-trained models for:
- Customer churn prediction
- Behavioral analysis
- Risk assessment

Models are automatically loaded on startup and can be retrained through the API.

## Network Configuration

The application is optimized for:
- High availability
- Load balancing
- Horizontal scaling
- Connection pooling
- Caching strategies

## Logging and Monitoring

- Structured JSON logging
- Request/response logging
- Performance metrics
- Error tracking
- Health monitoring

## Testing

Run the test suite:
```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
