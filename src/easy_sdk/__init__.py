"""
Django API Documentation Generator

An intelligent Python library that automatically generates comprehensive API documentation 
for Django backend repositories by leveraging AI and structural code analysis.
"""

__version__ = "0.1.1"
__author__ = "Django Docs Generator Team"
__email__ = "contact@example.com"

from .core.generator import DjangoDocsGenerator
from .core.config import DjangoDocsConfig

__all__ = [
    "DjangoDocsGenerator",
    "DjangoDocsConfig",
]