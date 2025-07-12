# Silver Adventure - PyPy-Optimized Pipeline System

_A comprehensive Python-based pipeline system with PyPy optimization for data processing and AI integration._

## Overview

Silver Adventure is a modular, scalable pipeline system designed for efficient data processing and AI model integration. It features PyPy optimization for performance-critical components, FastAPI web services, and comprehensive machine learning capabilities including churn prediction.

## Features

- **🚀 PyPy Optimization**: Performance-optimized components with PyPy JIT compilation
- **🔧 Modular Pipeline System**: Flexible, composable pipeline architecture
- **🤖 AI/ML Integration**: Built-in churn prediction and model management
- **🌐 FastAPI Web Services**: RESTful API endpoints for pipeline execution
- **📊 Monitoring & Observability**: Comprehensive logging and metrics collection
- **🐍 Anaconda Integration**: Environment management and dependency handling
- **🧪 Comprehensive Testing**: Unit, integration, and performance tests

## Quick Start

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Thhe1oldlady/silver-adventure.git
   cd silver-adventure
   ```

2. **Create Anaconda environment**:
   ```bash
   conda env create -f environment.yml
   conda activate silver-adventure
   ```

3. **Install the package**:
   ```bash
   pip install -e .
   ```

### Basic Usage

#### Command Line Interface

```bash
# Start the API server
silver-pipeline server --host 0.0.0.0 --port 8000

# List available pipelines
silver-pipeline pipeline list

# Run a pipeline
silver-pipeline pipeline run data_processing --input '{"data": [1, 2, 3]}'

# Make churn prediction
silver-pipeline model predict churn_predictor --input '{"tenure": 12, "monthly_charges": 79.99, "total_charges": 959.88, "contract_type": "Month-to-month", "payment_method": "Credit card", "internet_service": "Fiber optic", "phone_service": "Yes"}'

# Check system health
silver-pipeline health
```

#### Python API

```python
from silver_adventure.core.pipeline import PipelineBuilder
from silver_adventure.pipeline.components import DataValidationStep, DataCleaningStep
from silver_adventure.ml.churn_prediction import ChurnPredictor

# Create a pipeline
pipeline = (
    PipelineBuilder("my_pipeline")
    .add_step(DataValidationStep("validate"))
    .add_step(DataCleaningStep("clean"))
    .build()
)

# Execute pipeline
result = pipeline.execute(my_data)

# Use churn predictor
predictor = ChurnPredictor()
prediction = predictor.predict_single(customer_data)
```

#### REST API

```bash
# Start the server
uvicorn silver_adventure.api.server:app --host 0.0.0.0 --port 8000

# Execute pipeline
curl -X POST "http://localhost:8000/api/v1/pipelines/execute" \
  -H "Content-Type: application/json" \
  -d '{"pipeline_name": "data_processing", "data": {"input": "data"}}'

# Churn prediction
curl -X POST "http://localhost:8000/api/v1/ml/churn/predict" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "CUST_001", "features": {...}}'
```

## Architecture

### Core Components

- **`silver_adventure.core`**: Core pipeline framework and configuration
- **`silver_adventure.api`**: FastAPI web services and endpoints
- **`silver_adventure.ml`**: Machine learning models and utilities
- **`silver_adventure.pipeline`**: Pipeline components and registry
- **`silver_adventure.utils`**: Utility functions and performance tools

### Pipeline System

The pipeline system is built around composable steps that can be chained together:

```python
from silver_adventure.core.pipeline import PipelineBuilder

pipeline = (
    PipelineBuilder("data_processing")
    .add_data_processing_step("extract", extract_function)
    .add_data_processing_step("transform", transform_function)
    .add_data_processing_step("load", load_function)
    .build()
)
```

### PyPy Optimization

Silver Adventure includes PyPy-specific optimizations:

```python
from silver_adventure.utils.performance import pypy_optimizer

@pypy_optimizer.optimize_for_pypy
def cpu_intensive_function(data):
    # This function will be JIT-compiled by PyPy
    return process_data(data)
```

## Examples

The `examples/` directory contains comprehensive samples:

- **`data_processing_pipeline.py`**: Basic data processing pipeline
- **`churn_prediction_sample.py`**: Churn prediction with ML models
- **`api_client_sample.py`**: API client usage examples
- **`pypy_optimization_sample.py`**: PyPy optimization demonstrations

## Configuration

Silver Adventure uses a hierarchical configuration system:

```python
from silver_adventure.core.config import Config

config = Config(
    environment="production",
    api={"host": "0.0.0.0", "port": 8000},
    pipeline={"batch_size": 1000, "max_workers": 4},
    ml={"model_path": "models/", "churn_threshold": 0.5}
)
```

Configuration can be loaded from:
- Environment variables
- YAML files
- Python dictionaries

## Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/

# Run with coverage
pytest --cov=silver_adventure
```

## Performance Optimization

### PyPy Configuration

The system includes PyPy-specific optimizations:

```python
# PyPy environment variables
export PYPY_GC_NURSERY_SIZE=32MB
export PYPY_JIT_ENABLE=1
export PYPY_JIT_THRESHOLD=1039

# Run with PyPy
pypy3 -m silver_adventure.cli server
```

### Monitoring

Built-in performance monitoring:

```python
from silver_adventure.utils.monitoring import get_metrics_collector

metrics = get_metrics_collector()
metrics.increment_counter("pipeline.executions")
metrics.set_gauge("memory.usage", memory_usage())
```

## Docker Support

```dockerfile
FROM pypy:3.9-slim

WORKDIR /app
COPY . .

RUN pip install -e .

EXPOSE 8000
CMD ["silver-pipeline", "server"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with PyPy for performance optimization
- FastAPI for web services
- Pandas and NumPy for data processing
- scikit-learn for machine learning
- Prometheus for metrics collection

---

## Support

For questions and support:
- 📧 Email: team@silver-adventure.com
- 🐛 Issues: [GitHub Issues](https://github.com/Thhe1oldlady/silver-adventure/issues)
- 📖 Documentation: [GitHub Wiki](https://github.com/Thhe1oldlady/silver-adventure/wiki)
