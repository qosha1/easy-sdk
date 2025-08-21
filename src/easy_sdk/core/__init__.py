"""
Core package for Django API documentation generator
"""

from .config import DjangoDocsConfig
from .generator import DjangoDocsGenerator

__all__ = [
    "DjangoDocsConfig",
    "DjangoDocsGenerator",
]