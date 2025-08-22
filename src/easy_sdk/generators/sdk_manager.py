"""
SDK Manager - Orchestrates SDK generation across multiple languages
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.config import DjangoDocsConfig
from .sdks.python_sdk_generator import PythonSDKGenerator
from .sdks.typescript_sdk_generator import TypeScriptSDKGenerator

logger = logging.getLogger(__name__)


class SDKManager:
    """
    Manages SDK generation across multiple programming languages.
    Provides a unified interface for generating client libraries.
    """
    
    SUPPORTED_LANGUAGES = {
        'python': PythonSDKGenerator,
        'typescript': TypeScriptSDKGenerator,
        'javascript': TypeScriptSDKGenerator,  # Alias for typescript
        'ts': TypeScriptSDKGenerator,  # Short alias
        'js': TypeScriptSDKGenerator,  # Short alias
    }
    
    def __init__(self, config: DjangoDocsConfig):
        self.config = config
        
    def generate_sdk(
        self,
        analysis_result: Dict[str, Any],
        language: str,
        library_name: Optional[str] = None,
        **kwargs
    ) -> List[Path]:
        """
        Generate SDK for specified language
        
        Args:
            analysis_result: Django analysis results
            language: Target programming language
            library_name: Custom library name (optional)
            **kwargs: Additional language-specific options
            
        Returns:
            List of generated file paths
            
        Raises:
            ValueError: If language is not supported
        """
        if language.lower() not in self.SUPPORTED_LANGUAGES:
            supported = ', '.join(self.SUPPORTED_LANGUAGES.keys())
            raise ValueError(f"Unsupported language '{language}'. Supported: {supported}")
        
        generator_class = self.SUPPORTED_LANGUAGES[language.lower()]
        
        # Create generator instance with custom configuration
        if language.lower() in ['typescript', 'javascript', 'ts', 'js']:
            generator = generator_class(
                self.config,
                library_name=library_name,
                include_nodejs=kwargs.get('include_nodejs', True)
            )
        else:
            generator = generator_class(
                self.config,
                library_name=library_name
            )
        
        logger.info(f"🚀 Starting SDK generation for {language}")
        
        # Generate SDK
        generated_files = generator.generate_sdk(analysis_result)
        
        logger.info(f"✅ SDK generation completed: {len(generated_files)} files generated")
        
        return generated_files
    
    def generate_multiple_sdks(
        self,
        analysis_result: Dict[str, Any],
        languages: List[str],
        library_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, List[Path]]:
        """
        Generate SDKs for multiple languages
        
        Args:
            analysis_result: Django analysis results
            languages: List of target programming languages
            library_name: Custom library name (optional)
            **kwargs: Additional language-specific options
            
        Returns:
            Dictionary mapping language to list of generated file paths
        """
        results = {}
        
        logger.info(f"🔥 Generating SDKs for {len(languages)} languages: {', '.join(languages)}")
        
        for language in languages:
            try:
                generated_files = self.generate_sdk(
                    analysis_result=analysis_result,
                    language=language,
                    library_name=library_name,
                    **kwargs
                )
                results[language] = generated_files
                
            except Exception as e:
                logger.error(f"Failed to generate SDK for {language}: {str(e)}")
                results[language] = []
        
        total_files = sum(len(files) for files in results.values())
        logger.info(f"🎉 Multi-language SDK generation completed: {total_files} total files")
        
        return results
    
    def list_supported_languages(self) -> List[str]:
        """Get list of supported programming languages"""
        return list(self.SUPPORTED_LANGUAGES.keys())
    
    def get_language_info(self, language: str) -> Dict[str, Any]:
        """
        Get information about a supported language
        
        Args:
            language: Programming language name
            
        Returns:
            Dictionary with language information
        """
        if language.lower() not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {language}")
        
        generator_class = self.SUPPORTED_LANGUAGES[language.lower()]
        
        return {
            'name': language,
            'generator': generator_class.__name__,
            'description': generator_class.__doc__.strip() if generator_class.__doc__ else '',
            'features': self._get_language_features(language.lower())
        }
    
    def _get_language_features(self, language: str) -> List[str]:
        """Get features supported by a language generator"""
        features_map = {
            'python': [
                'Async/await support',
                'Type hints with Pydantic',
                'Automatic retries with exponential backoff',
                'Comprehensive error handling',
                'Token-based authentication',
                'Request/response validation',
                'Modular client structure'
            ],
            'typescript': [
                'Full TypeScript type definitions',
                'Modern async/await API',
                'Browser and Node.js support',
                'Automatic retries with exponential backoff',
                'Comprehensive error handling',
                'Token-based authentication',
                'Tree-shakable modules',
                'ESM and CommonJS support'
            ],
            'javascript': [
                'Full TypeScript type definitions',
                'Modern async/await API', 
                'Browser and Node.js support',
                'Automatic retries with exponential backoff',
                'Comprehensive error handling',
                'Token-based authentication',
                'Tree-shakable modules',
                'ESM and CommonJS support'
            ]
        }
        
        # Handle aliases
        if language in ['ts', 'js']:
            language = 'typescript'
        
        return features_map.get(language, [])
    
    def validate_analysis_result(self, analysis_result: Dict[str, Any]) -> bool:
        """
        Validate that analysis result is suitable for SDK generation
        
        Args:
            analysis_result: Django analysis results
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(analysis_result, dict):
            logger.error("Analysis result must be a dictionary")
            return False
        
        if not analysis_result:
            logger.error("Analysis result is empty")
            return False
        
        # Check for at least one app with endpoints
        has_endpoints = False
        for app_name, app_data in analysis_result.items():
            if isinstance(app_data, dict):
                views = app_data.get('views', [])
                if views:
                    for view in views:
                        view_data = view if isinstance(view, dict) else {
                            'endpoints': getattr(view, 'endpoints', [])
                        }
                        if view_data.get('endpoints'):
                            has_endpoints = True
                            break
                    if has_endpoints:
                        break
        
        if not has_endpoints:
            logger.error("No API endpoints found in analysis result")
            return False
        
        logger.info("Analysis result validation passed")
        return True
    
    def preview_sdk_structure(
        self,
        analysis_result: Dict[str, Any],
        language: str,
        library_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Preview the structure of generated SDK without actually generating files
        
        Args:
            analysis_result: Django analysis results
            language: Target programming language
            library_name: Custom library name (optional)
            
        Returns:
            Dictionary describing the SDK structure
        """
        if language.lower() not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {language}")
        
        generator_class = self.SUPPORTED_LANGUAGES[language.lower()]
        generator = generator_class(self.config, library_name=library_name)
        
        # Extract API structure
        api_structure = generator._extract_api_structure(analysis_result)
        
        # Build preview structure
        preview = {
            'language': language,
            'library_name': library_name or 'api_client',
            'package_name': getattr(generator, 'package_name', library_name),
            'total_apps': len(api_structure['apps']),
            'total_endpoints': sum(len(app['endpoints']) for app in api_structure['apps']),
            'apps': [],
            'common_patterns': api_structure.get('common_patterns', []),
            'auth_strategy': api_structure.get('auth_strategy', 'token'),
            'estimated_files': self._estimate_file_count(api_structure, language)
        }
        
        # Add app details
        for app in api_structure['apps']:
            app_preview = {
                'name': app['name'],
                'class_name': app['class_name'],
                'endpoints': len(app['endpoints']),
                'models': len(app['models']),
                'operations': [op['name'] for op in app['operations']]
            }
            preview['apps'].append(app_preview)
        
        return preview
    
    def _estimate_file_count(self, api_structure: Dict[str, Any], language: str) -> int:
        """Estimate number of files that will be generated"""
        base_files = 5  # Core files (client, exceptions, utils, etc.)
        
        if language.lower() in ['python']:
            # Python: setup.py, requirements.txt, __init__.py, base_client.py, exceptions.py
            # Plus one client file per app, one model file per serializer
            app_files = len(api_structure['apps'])  # Client files
            model_files = sum(len(app['models']) for app in api_structure['apps'])
            return base_files + app_files + model_files + 2  # +2 for setup files
            
        elif language.lower() in ['typescript', 'javascript', 'ts', 'js']:
            # TypeScript: package.json, tsconfig.json, base client, exceptions, utils
            # Plus one client file per app, one types file per app, common types
            app_files = len(api_structure['apps']) * 2  # Client + types per app
            return base_files + app_files + 3  # +3 for package files
            
        return base_files + len(api_structure['apps'])