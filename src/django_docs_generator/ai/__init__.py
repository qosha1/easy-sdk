"""
AI integration package for enhanced Django analysis
"""

from .engine import AIAnalysisEngine
from .prompts import PromptTemplates

__all__ = [
    "AIAnalysisEngine",
    "PromptTemplates",
]