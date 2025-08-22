"""
Base SDK Generator - Abstract base class for generating client SDKs
"""

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ...core.config import DjangoDocsConfig
from ...ai.engine import AIAnalysisEngine

logger = logging.getLogger(__name__)


class BaseSDKGenerator(ABC):
    """
    Abstract base class for generating client SDKs from Django API analysis.
    Provides common functionality for all language-specific generators.
    """
    
    def __init__(self, config: DjangoDocsConfig, language: str):
        self.config = config
        self.language = language
        self.output_dir = config.output.base_output_dir / f"sdk_{language}"
        self.ai_engine = AIAnalysisEngine(config)
        
    @abstractmethod
    def generate_sdk(self, analysis_result: Dict[str, Any]) -> List[Path]:
        """Generate complete SDK from Django analysis"""
        pass
    
    @abstractmethod
    def _generate_client_class(self, app_name: str, endpoints: List[Dict]) -> str:
        """Generate the main client class for an app"""
        pass
    
    @abstractmethod
    def _generate_models(self, app_name: str, serializers: List[Dict]) -> List[Tuple[str, str]]:
        """Generate data models from serializers. Returns list of (filename, content) tuples"""
        pass
    
    @abstractmethod
    def _generate_project_structure(self) -> None:
        """Create the basic project structure (setup files, etc.)"""
        pass
    
    def _extract_api_structure(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and organize API structure from analysis results"""
        logger.info(f"🔍 Analyzing API structure for {len(analysis_result)} apps")
        
        # Use AI to analyze and structure the API
        structure_analysis = self.ai_engine.analyze_api_structure(analysis_result)
        
        organized_structure = {
            'apps': [],
            'common_patterns': structure_analysis.get('common_patterns', []),
            'auth_strategy': structure_analysis.get('auth_strategy', 'token'),
            'base_url_pattern': structure_analysis.get('base_url_pattern', '/api'),
            'error_handling': structure_analysis.get('error_handling', {}),
            'pagination_strategy': structure_analysis.get('pagination_strategy', 'page_number')
        }
        
        # Process each app
        for app_name, app_data in analysis_result.items():
            if not isinstance(app_data, dict) or not (app_data.get('serializers') or app_data.get('views')):
                continue
                
            app_info = {
                'name': app_name,
                'class_name': self._to_class_name(app_name),
                'serializers': self._process_serializers(app_data.get('serializers', [])),
                'endpoints': self._process_endpoints(app_data.get('views', []), app_name),
                'models': [],
                'operations': []
            }
            
            # Generate models from serializers
            for serializer in app_info['serializers']:
                model_info = {
                    'name': serializer['name'].replace('Serializer', ''),
                    'class_name': serializer['name'].replace('Serializer', ''),
                    'fields': serializer['fields'],
                    'docstring': serializer.get('docstring', ''),
                    'validation_rules': self._extract_validation_rules(serializer['fields'])
                }
                app_info['models'].append(model_info)
            
            # Group endpoints into operations
            app_info['operations'] = self._group_endpoints_into_operations(app_info['endpoints'])
            
            organized_structure['apps'].append(app_info)
        
        return organized_structure
    
    def _process_serializers(self, serializers: List[Any]) -> List[Dict]:
        """Process serializers into standardized format"""
        processed = []
        
        for serializer in serializers:
            if hasattr(serializer, 'name'):
                # SerializerInfo object
                processed.append({
                    'name': serializer.name,
                    'fields': getattr(serializer, 'fields', {}),
                    'docstring': getattr(serializer, 'docstring', ''),
                    'file_path': getattr(serializer, 'file_path', '')
                })
            elif isinstance(serializer, dict):
                processed.append(serializer)
                
        return processed
    
    def _process_endpoints(self, views: List[Any], app_name: str) -> List[Dict]:
        """Process views/endpoints into standardized format"""
        endpoints = []
        
        for view in views:
            view_data = view if isinstance(view, dict) else {
                'name': getattr(view, 'name', ''),
                'endpoints': getattr(view, 'endpoints', []),
                'serializer_class': getattr(view, 'serializer_class', ''),
                'permission_classes': getattr(view, 'permission_classes', []),
                'authentication_classes': getattr(view, 'authentication_classes', [])
            }
            
            for endpoint in view_data.get('endpoints', []):
                endpoint_info = {
                    'method': endpoint.get('method', 'GET'),
                    'path': endpoint.get('path', '/'),
                    'name': endpoint.get('name', ''),
                    'description': endpoint.get('description', ''),
                    'serializer_class': endpoint.get('serializer_class') or view_data.get('serializer_class'),
                    'operation_id': self._generate_operation_id(endpoint.get('method', 'GET'), endpoint.get('path', '/'), app_name),
                    'parameters': self._extract_parameters(endpoint.get('path', '/')),
                    'requires_auth': bool(view_data.get('permission_classes') or view_data.get('authentication_classes')),
                    'tags': [app_name]
                }
                endpoints.append(endpoint_info)
        
        return endpoints
    
    def _extract_parameters(self, path: str) -> List[Dict]:
        """Extract parameters from URL path"""
        import re
        
        parameters = []
        
        # Extract path parameters
        path_params = re.findall(r'<(\w+:)?(\w+)>', path) or re.findall(r'\{(\w+)\}', path)
        
        for param_match in path_params:
            if isinstance(param_match, tuple) and len(param_match) == 2:
                param_name = param_match[1] if param_match[1] else param_match[0]
            else:
                param_name = param_match
                
            parameters.append({
                'name': param_name,
                'type': 'path',
                'required': True,
                'data_type': 'string'
            })
        
        return parameters
    
    def _generate_operation_id(self, method: str, path: str, app_name: str) -> str:
        """Generate a unique operation ID for the endpoint"""
        # Extract resource from path
        path_parts = [p for p in path.split('/') if p and not p.startswith('{') and not p.startswith('<')]
        resource = path_parts[-1] if path_parts else app_name
        
        # Map HTTP methods to actions
        action_map = {
            'GET': 'list' if not any('{' in p or '<' in p for p in path.split('/')) else 'get',
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'partial_update',
            'DELETE': 'delete'
        }
        
        action = action_map.get(method.upper(), method.lower())
        return f"{action}_{resource}".replace('-', '_')
    
    def _group_endpoints_into_operations(self, endpoints: List[Dict]) -> List[Dict]:
        """Group related endpoints into logical operations"""
        operations = []
        grouped = {}
        
        # Group by resource
        for endpoint in endpoints:
            resource = self._extract_resource_from_path(endpoint['path'])
            if resource not in grouped:
                grouped[resource] = []
            grouped[resource].append(endpoint)
        
        # Create operation groups
        for resource, resource_endpoints in grouped.items():
            operation = {
                'name': resource,
                'class_name': self._to_class_name(resource),
                'endpoints': resource_endpoints,
                'base_path': self._extract_base_path(resource_endpoints),
                'primary_model': self._infer_primary_model(resource_endpoints)
            }
            operations.append(operation)
        
        return operations
    
    def _extract_resource_from_path(self, path: str) -> str:
        """Extract the main resource name from a path"""
        # Remove /api/ prefix and extract main resource
        parts = [p for p in path.split('/') if p and p != 'api']
        
        # Find first non-parameter part
        for part in parts:
            if not (part.startswith('{') or part.startswith('<')):
                return part
        
        return 'default'
    
    def _extract_base_path(self, endpoints: List[Dict]) -> str:
        """Extract the base path for a group of endpoints"""
        if not endpoints:
            return '/'
            
        # Find common prefix
        paths = [ep['path'] for ep in endpoints]
        if len(paths) == 1:
            # Remove parameters from single path
            path = paths[0]
            parts = []
            for part in path.split('/'):
                if part and not (part.startswith('{') or part.startswith('<')):
                    parts.append(part)
                elif part.startswith('{') or part.startswith('<'):
                    break
            return '/' + '/'.join(parts)
        
        # Find common prefix among multiple paths
        common_parts = []
        path_parts = [p.split('/') for p in paths]
        
        for i in range(min(len(parts) for parts in path_parts)):
            parts_at_i = set(parts[i] for parts in path_parts)
            if len(parts_at_i) == 1 and not any(p.startswith('{') or p.startswith('<') for p in parts_at_i):
                common_parts.append(list(parts_at_i)[0])
            else:
                break
                
        return '/' + '/'.join(p for p in common_parts if p)
    
    def _infer_primary_model(self, endpoints: List[Dict]) -> Optional[str]:
        """Infer the primary model for a group of endpoints"""
        serializers = [ep.get('serializer_class') for ep in endpoints if ep.get('serializer_class')]
        
        if serializers:
            # Return most common serializer
            from collections import Counter
            return Counter(serializers).most_common(1)[0][0].replace('Serializer', '')
        
        return None
    
    def _extract_validation_rules(self, fields: Dict) -> Dict:
        """Extract validation rules from field definitions"""
        rules = {}
        
        for field_name, field_info in fields.items():
            field_rules = {}
            
            if field_info.get('required'):
                field_rules['required'] = True
                
            if field_info.get('max_length'):
                field_rules['max_length'] = field_info['max_length']
                
            if field_info.get('choices'):
                field_rules['choices'] = field_info['choices']
                
            if field_info.get('allow_null') is False:
                field_rules['not_null'] = True
                
            if field_rules:
                rules[field_name] = field_rules
        
        return rules
    
    def _to_class_name(self, name: str) -> str:
        """Convert name to PascalCase class name"""
        # Handle snake_case, kebab-case, etc.
        parts = name.replace('-', '_').replace(' ', '_').split('_')
        return ''.join(word.capitalize() for word in parts if word)
    
    def _to_snake_case(self, name: str) -> str:
        """Convert name to snake_case"""
        import re
        
        # Handle PascalCase/camelCase
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
        
        # Handle spaces and hyphens
        return s2.replace(' ', '_').replace('-', '_').lower()
    
    def _create_directory_structure(self) -> None:
        """Create basic directory structure"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Created SDK directory: {self.output_dir}")
    
    def _write_file(self, file_path: Path, content: str) -> Path:
        """Write content to file and return path"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        logger.debug(f"📝 Generated: {file_path}")
        return file_path