# Silver Adventure - Comprehensive Repository Template

[![CI/CD Pipeline](https://github.com/Thhe1oldlady/silver-adventure/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/Thhe1oldlady/silver-adventure/actions/workflows/ci-cd.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive, reusable repository template featuring FastAPI backend, machine learning capabilities, automated email generation, and seamless VS Code integration. This template provides a complete foundation for modern Python applications with data science and automation features.

## 🚀 Features

### Core Capabilities
- **FastAPI Backend**: High-performance web API with automatic documentation
- **Machine Learning**: Churn prediction models and data analysis pipelines
- **Email Generation**: "Golden Mood" themed email automation with customizable templates
- **VS Code Integration**: Optimized development environment with extensions and settings
- **CI/CD Pipeline**: Automated testing, deployment, and quality checks

### Technical Stack
- **Backend**: FastAPI, Uvicorn, SQLAlchemy
- **ML/Data Science**: NumPy, Pandas, Scikit-learn, Jupyter
- **Email**: Jinja2 templates, SMTP integration
- **Environment**: Anaconda, PyPy compatibility
- **Testing**: Pytest, automated test suites
- **Quality**: Black, Flake8, isort

## 📋 Quick Start

### Prerequisites
- Python 3.9+ or Anaconda
- Git
- VS Code (recommended)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Thhe1oldlady/silver-adventure.git
   cd silver-adventure
   ```

2. **Set up environment (Choose one):**

   **Option A: Using Anaconda (Recommended)**
   ```bash
   conda env create -f environment.yml
   conda activate silver-adventure
   ```

   **Option B: Using pip**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp config/.env.example config/.env
   # Edit config/.env with your settings
   ```

4. **Run the application:**
   ```bash
   uvicorn src.silver_adventure.main:app --reload
   ```

5. **Access the API:**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 🎯 Template Usage

### For New Projects
1. Use this repository as a template on GitHub
2. Clone your new repository
3. Follow the installation steps above
4. Customize the configuration files
5. Start building your application

### Key Files to Customize
- `config/.env` - Environment variables
- `src/silver_adventure/models/` - Data models
- `src/silver_adventure/templates/` - Email templates
- `README.md` - Update with your project details

## 🔧 Development

### VS Code Setup
The repository includes optimized VS Code configuration:
- **Extensions**: Python, Pylance, GitHub Copilot
- **Settings**: Integrated linting, formatting, and debugging
- **Tasks**: Automated testing and deployment commands

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/silver_adventure

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
```

### Code Quality
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/
```

## 📧 Email Generation

The "Golden Mood" email system provides:
- **Customizable Templates**: Professional, friendly, and promotional themes
- **Dynamic Content**: Personalized subject lines and content
- **Batch Processing**: Send multiple emails efficiently
- **Template Management**: Easy template creation and modification

### Usage Example
```python
from src.silver_adventure.services.email_service import EmailService

email_service = EmailService()
email_service.send_golden_mood_email(
    to_email="user@example.com",
    template="welcome",
    context={"name": "John Doe"}
)
```

## 🤖 Machine Learning

### Churn Prediction
Built-in customer churn prediction model:
- **Training Pipeline**: Automated model training and validation
- **API Endpoints**: Real-time prediction API
- **Model Management**: Version control and model updates

### Data Processing
- **Pipeline Architecture**: Modular data processing components
- **Feature Engineering**: Automated feature extraction and selection
- **Model Evaluation**: Comprehensive metrics and validation

## 🔄 CI/CD Pipeline

Automated workflows include:
- **Code Quality**: Linting, formatting, and security checks
- **Testing**: Unit and integration tests
- **Deployment**: Automated deployment to staging and production
- **Monitoring**: Performance and error tracking

## 📚 Documentation

- **API Docs**: Automatic FastAPI documentation at `/docs`
- **Development Guide**: See `docs/development.md`
- **Deployment Guide**: See `docs/deployment.md`
- **Email Templates**: See `docs/email-templates.md`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and quality checks
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/Thhe1oldlady/silver-adventure/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Thhe1oldlady/silver-adventure/discussions)
- **Documentation**: [Project Wiki](https://github.com/Thhe1oldlady/silver-adventure/wiki)

## 🌟 Acknowledgments

Built with ❤️ using:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [GitHub Copilot](https://github.com/features/copilot) - AI pair programming
- [VS Code](https://code.visualstudio.com/) - Powerful code editor
- [Anaconda](https://www.anaconda.com/) - Data science platform

---

Made with GitHub Copilot and VS Code 🚀
