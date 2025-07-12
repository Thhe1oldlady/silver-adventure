# Silver Adventure - Development Guide

## Overview

This document provides comprehensive instructions for developing with the Silver Adventure template.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Development Workflow](#development-workflow)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software
- Python 3.9 or higher
- Git
- VS Code (recommended)

### Optional Software
- Anaconda or Miniconda
- Docker
- PyPy (for performance optimization)

## Development Setup

### 1. Environment Setup

**Option A: Using Anaconda (Recommended)**
```bash
# Create and activate environment
conda env create -f environment.yml
conda activate silver-adventure
```

**Option B: Using pip**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Development Installation
```bash
# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### 3. Environment Configuration
```bash
# Copy environment template
cp config/.env.example config/.env

# Edit configuration
vim config/.env
```

### 4. VS Code Setup
Open the project in VS Code, and the configured extensions and settings will be automatically applied.

## Project Structure

```
silver-adventure/
├── .devcontainer/          # Development container config
├── .github/               # GitHub Actions workflows
├── .vscode/              # VS Code configuration
├── config/               # Configuration files
├── docs/                 # Documentation
├── scripts/              # Utility scripts
├── src/                  # Source code
│   └── silver_adventure/
│       ├── api/          # API endpoints
│       ├── models/       # Data models
│       ├── services/     # Business logic
│       ├── templates/    # Email templates
│       └── utils/        # Utility functions
├── tests/                # Test files
├── data/                 # Data files (created at runtime)
├── models/               # ML models (created at runtime)
└── logs/                 # Log files (created at runtime)
```

## Running the Application

### Local Development
```bash
# Start the FastAPI server
uvicorn src.silver_adventure.main:app --reload --host 0.0.0.0 --port 8000

# Or use the VS Code task
# Press Ctrl+Shift+P -> "Tasks: Run Task" -> "Run FastAPI Server"
```

### Access Points
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Run with coverage
pytest --cov=src/silver_adventure --cov-report=html

# Run specific test file
pytest tests/unit/test_email_service.py -v
```

### Test Scripts
```bash
# Test email service
python scripts/test_email_service.py

# Test churn service
python scripts/test_churn_service.py
```

## Code Quality

### Formatting
```bash
# Format code
black src/ tests/

# Check formatting
black --check src/ tests/
```

### Import Sorting
```bash
# Sort imports
isort src/ tests/

# Check import sorting
isort --check-only src/ tests/
```

### Linting
```bash
# Lint code
flake8 src/ tests/

# VS Code integration provides real-time linting
```

### All Quality Checks
```bash
# Run all quality checks (VS Code task available)
black src/ tests/ && isort src/ tests/ && flake8 src/ tests/
```

## Development Workflow

### 1. Feature Development
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes
# ... develop ...

# Run tests
pytest

# Check code quality
black src/ tests/
isort src/ tests/
flake8 src/ tests/

# Commit changes
git add .
git commit -m "Add new feature"
```

### 2. Email Template Development
```bash
# Edit templates in src/silver_adventure/services/email_service.py
# Test templates
python scripts/test_email_service.py

# View generated emails in development mode
```

### 3. ML Model Development
```bash
# Modify models in src/silver_adventure/services/churn_service.py
# Test models
python scripts/test_churn_service.py

# Train new models via API
curl -X POST http://localhost:8000/api/v1/pipeline/train
```

## Environment Variables

### Required Variables
```env
# Application
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key

# Email (optional for development)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@silver-adventure.com
```

### Optional Variables
```env
# Database
DATABASE_URL=sqlite:///./silver_adventure.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/silver_adventure.log

# Features
ENABLE_EMAIL_SENDING=true
ENABLE_CHURN_PREDICTION=true
ENABLE_GOLDEN_MOOD_TEMPLATES=true
```

## Debugging

### VS Code Debugging
1. Set breakpoints in your code
2. Press F5 or use "Run and Debug" panel
3. Choose "Python: FastAPI" configuration

### API Debugging
```bash
# Test endpoints with curl
curl -X GET http://localhost:8000/health

# Test email generation
curl -X POST http://localhost:8000/api/v1/email/send \
  -H "Content-Type: application/json" \
  -d '{"to_email": "test@example.com", "template": "welcome", "context": {"name": "John"}}'
```

## Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Ensure PYTHONPATH includes src
export PYTHONPATH="${PYTHONPATH}:./src"

# Or install in development mode
pip install -e .
```

**2. Database Issues**
```bash
# Remove database file and restart
rm silver_adventure.db
uvicorn src.silver_adventure.main:app --reload
```

**3. Port Already in Use**
```bash
# Use different port
uvicorn src.silver_adventure.main:app --reload --port 8001

# Or kill existing process
lsof -ti:8000 | xargs kill
```

**4. Email Service Issues**
- Check SMTP configuration in `.env`
- Verify email credentials
- Test in development mode (emails will be logged)

**5. Model Training Issues**
- Ensure `models/` and `data/` directories exist
- Check disk space
- Verify sample data generation

### Performance Tips

**1. Use PyPy for ML Operations**
```bash
# Install PyPy
# Set PYPY_ENABLED=true in .env
```

**2. Enable Production Optimizations**
```bash
# Use multiple workers
uvicorn src.silver_adventure.main:app --workers 4

# Enable compression
# Configure in production deployment
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run quality checks
6. Submit a pull request

## Getting Help

- Check the [FAQ](FAQ.md)
- Review [API Documentation](http://localhost:8000/docs)
- Submit issues on GitHub
- Join our community discussions