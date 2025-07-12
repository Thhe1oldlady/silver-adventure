#!/usr/bin/env python3
"""
Setup script for AI Module

This script provides installation and setup functionality for the AI module
developed for the silver-adventure repository.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
readme_path = Path(__file__).parent / "README_AI_MODULE.md"
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "AI Module for Silver Adventure Repository"

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as f:
        requirements = [
            line.strip() for line in f 
            if line.strip() and not line.startswith("#")
        ]
else:
    requirements = []

setup(
    name="ai-module-silver-adventure",
    version="1.0.0",
    author="AI Assistant",
    author_email="ai@example.com",
    description="AI Module for Silver Adventure Repository",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Thhe1oldlady/silver-adventure",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "nlp": [
            "nltk>=3.7",
            "spacy>=3.4.0",
        ],
        "ml": [
            "scikit-learn>=1.1.0",
            "numpy>=1.21.0",
            "pandas>=1.4.0",
        ],
        "web": [
            "flask>=2.0.0",
            "fastapi>=0.78.0",
            "requests>=2.28.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-module-demo=ai_module.examples.demo:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="ai, artificial intelligence, nlp, text processing, chatbot, machine learning",
    project_urls={
        "Bug Reports": "https://github.com/Thhe1oldlady/silver-adventure/issues",
        "Source": "https://github.com/Thhe1oldlady/silver-adventure",
        "Documentation": "https://github.com/Thhe1oldlady/silver-adventure#readme",
    },
)