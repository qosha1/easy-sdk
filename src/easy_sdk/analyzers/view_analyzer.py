"""
Django REST Framework view analyzer for extracting API endpoint information
"""

import ast
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ..core.config import DjangoDocsConfig

logger = logging.getLogger(__name__)


class ViewEndpoint:
    """Represents a single API endpoint"""
    
    def __init__(self, path: str, method: str, view_class: str):
        self.path = path
        self.method = method.upper()
        self.view_class = view_class
        self.function_name = ""
        self.serializer_class = None
        self.permission_classes = []
        self.authentication_classes = []
        self.filter_classes = []
        self.pagination_class = None
        self.throttle_classes = []
        self.description = ""
        self.parameters = []
        self.response_serializer = None
        self.status_codes = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert endpoint to dictionary representation"""
        return {
            'path': self.path,
            'method': self.method,
            'view_class': self.view_class,
            'function_name': self.function_name,
            'serializer_class': self.serializer_class,
            'permission_classes': self.permission_classes,
            'authentication_classes': self.authentication_classes,
            'filter_classes': self.filter_classes,
            'pagination_class': self.pagination_class,
            'throttle_classes': self.throttle_classes,
            'description': self.description,
            'parameters': self.parameters,
            'response_serializer': self.response_serializer,
            'status_codes': self.status_codes,
        }


class ViewInfo:
    """Information about a Django REST framework view or viewset"""
    
    def __init__(self, name: str, file_path: str):
        self.name = name
        self.file_path = file_path
        self.base_classes = []
        self.docstring = ""
        self.line_number = 0
        self.view_type = "unknown"  # APIView, ViewSet, ModelViewSet, etc.
        self.serializer_class = None
        self.queryset = None
        self.model = None
        self.permission_classes = []
        self.authentication_classes = []
        self.filter_backends = []
        self.filterset_class = None
        self.search_fields = []
        self.ordering_fields = []
        self.ordering = []
        self.pagination_class = None
        self.throttle_classes = []
        self.endpoints: List[ViewEndpoint] = []
        self.methods = []
        self.custom_actions = []  # For ViewSets
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert view info to dictionary"""
        return {
            'name': self.name,
            'file_path': self.file_path,
            'base_classes': self.base_classes,
            'docstring': self.docstring,
            'line_number': self.line_number,
            'view_type': self.view_type,
            'serializer_class': self.serializer_class,
            'queryset': self.queryset,
            'model': self.model,
            'permission_classes': self.permission_classes,
            'authentication_classes': self.authentication_classes,
            'filter_backends': self.filter_backends,
            'filterset_class': self.filterset_class,
            'search_fields': self.search_fields,
            'ordering_fields': self.ordering_fields,
            'ordering': self.ordering,
            'pagination_class': self.pagination_class,
            'throttle_classes': self.throttle_classes,
            'endpoints': [ep.to_dict() for ep in self.endpoints],
            'methods': self.methods,
            'custom_actions': self.custom_actions,
        }


class ViewAnalyzer:
    """
    Analyzes Django REST Framework views and viewsets to extract
    API endpoint information, permissions, serializers, and more
    """
    
    def __init__(self, config: DjangoDocsConfig):
        self.config = config
        
        # DRF view type mappings
        self.view_types = {
            'APIView': 'api_view',
            'GenericAPIView': 'generic_api_view',
            'CreateAPIView': 'create_view',
            'ListAPIView': 'list_view',
            'RetrieveAPIView': 'retrieve_view',
            'UpdateAPIView': 'update_view',
            'DestroyAPIView': 'destroy_view',
            'ListCreateAPIView': 'list_create_view',
            'RetrieveUpdateAPIView': 'retrieve_update_view',
            'RetrieveDestroyAPIView': 'retrieve_destroy_view',
            'RetrieveUpdateDestroyAPIView': 'retrieve_update_destroy_view',
            'ViewSet': 'viewset',
            'GenericViewSet': 'generic_viewset',
            'ModelViewSet': 'model_viewset',
            'ReadOnlyModelViewSet': 'readonly_model_viewset',
        }
        
        # HTTP methods for different view types
        self.view_methods = {
            'api_view': ['get', 'post', 'put', 'patch', 'delete'],
            'create_view': ['post'],
            'list_view': ['get'],
            'retrieve_view': ['get'],
            'update_view': ['put', 'patch'],
            'destroy_view': ['delete'],
            'list_create_view': ['get', 'post'],
            'retrieve_update_view': ['get', 'put', 'patch'],
            'retrieve_destroy_view': ['get', 'delete'],
            'retrieve_update_destroy_view': ['get', 'put', 'patch', 'delete'],
            'model_viewset': ['get', 'post', 'put', 'patch', 'delete'],
            'readonly_model_viewset': ['get'],
        }
    
    def analyze_app_views(self, app_name: str, app_info: Dict) -> List[ViewInfo]:
        """
        Analyze all views in a Django app
        
        Args:
            app_name: Name of the Django app
            app_info: App information from scanner
            
        Returns:
            List of ViewInfo objects
        """
        views = []
        
        try:
            # Get view files from app info
            view_files = app_info.get('views', [])
            
            for view_file in view_files:
                file_views = self.analyze_view_file(Path(view_file))
                views.extend(file_views)
            
            logger.info(f"Analyzed {len(views)} views in app '{app_name}'")
            
        except Exception as e:
            logger.error(f"Failed to analyze views in app '{app_name}': {str(e)}")
        
        return views
    
    def analyze_view_file(self, file_path: Path) -> List[ViewInfo]:
        """
        Analyze a single view file
        
        Args:
            file_path: Path to the view file
            
        Returns:
            List of ViewInfo objects found in the file
        """
        views = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Extract imports to understand view types
            imports = self._extract_imports(tree)
            
            # Find view classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if self._is_view_class(node):
                        view_info = self._analyze_view_class(
                            node, str(file_path), imports
                        )
                        if view_info:
                            views.append(view_info)
            
            logger.debug(f"Found {len(views)} views in {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to analyze view file {file_path}: {str(e)}")
        
        return views
    
    def _extract_imports(self, tree: ast.AST) -> Dict[str, str]:
        """Extract import statements to understand available view types"""
        imports = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports[alias.asname or alias.name] = alias.name
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for alias in node.names:
                        import_name = alias.asname or alias.name
                        full_name = f"{node.module}.{alias.name}"
                        imports[import_name] = full_name
        
        return imports
    
    def _is_view_class(self, node: ast.ClassDef) -> bool:
        """Check if a class is a Django REST framework view"""
        for base in node.bases:
            base_name = self._get_name_from_node(base)
            if base_name and any(view_type in base_name for view_type in 
                               ['APIView', 'ViewSet', 'GenericAPIView']):
                return True
        return False
    
    def _get_name_from_node(self, node: ast.AST) -> Optional[str]:
        """Extract name from an AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value_name = self._get_name_from_node(node.value)
            if value_name:
                return f"{value_name}.{node.attr}"
        return None
    
    def _analyze_view_class(self, node: ast.ClassDef, file_path: str, imports: Dict[str, str]) -> Optional[ViewInfo]:
        """Analyze a single view class"""
        try:
            view_info = ViewInfo(node.name, file_path)
            view_info.line_number = node.lineno
            view_info.docstring = ast.get_docstring(node) or ""
            
            # Extract base classes
            for base in node.bases:
                base_name = self._get_name_from_node(base)
                if base_name:
                    view_info.base_classes.append(base_name)
                    # Determine view type
                    view_type = self._determine_view_type(base_name)
                    if view_type != "unknown":
                        view_info.view_type = view_type
            
            # Analyze class body
            for item in node.body:
                if isinstance(item, ast.Assign):
                    # Class attributes
                    self._analyze_view_attribute(item, view_info)
                elif isinstance(item, ast.FunctionDef):
                    # Methods
                    self._analyze_view_method(item, view_info)
            
            # Generate endpoints based on view type and methods
            self._generate_endpoints(view_info)
            
            return view_info
            
        except Exception as e:
            logger.error(f"Failed to analyze view class {node.name}: {str(e)}")
            return None
    
    def _determine_view_type(self, base_name: str) -> str:
        """Determine the view type from base class name"""
        for view_class, view_type in self.view_types.items():
            if view_class in base_name:
                return view_type
        return "unknown"
    
    def _analyze_view_attribute(self, node: ast.Assign, view_info: ViewInfo) -> None:
        """Analyze a class attribute in a view"""
        try:
            # Get attribute name
            if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
                return
            
            attr_name = node.targets[0].id
            attr_value = self._extract_literal_or_name_value(node.value)
            
            # Map common DRF view attributes
            if attr_name == 'serializer_class':
                view_info.serializer_class = attr_value
            elif attr_name == 'queryset':
                view_info.queryset = attr_value
                # Try to extract model from queryset
                view_info.model = self._extract_model_from_queryset(node.value)
            elif attr_name == 'permission_classes':
                view_info.permission_classes = self._extract_list_value(node.value)
            elif attr_name == 'authentication_classes':
                view_info.authentication_classes = self._extract_list_value(node.value)
            elif attr_name == 'filter_backends':
                view_info.filter_backends = self._extract_list_value(node.value)
            elif attr_name == 'filterset_class':
                view_info.filterset_class = attr_value
            elif attr_name == 'search_fields':
                view_info.search_fields = self._extract_list_value(node.value)
            elif attr_name == 'ordering_fields':
                view_info.ordering_fields = self._extract_list_value(node.value)
            elif attr_name == 'ordering':
                view_info.ordering = self._extract_list_value(node.value)
            elif attr_name == 'pagination_class':
                view_info.pagination_class = attr_value
            elif attr_name == 'throttle_classes':
                view_info.throttle_classes = self._extract_list_value(node.value)
                
        except Exception as e:
            logger.warning(f"Failed to analyze view attribute: {str(e)}")
    
    def _analyze_view_method(self, node: ast.FunctionDef, view_info: ViewInfo) -> None:
        """Analyze a method in a view class"""
        try:
            method_name = node.name
            view_info.methods.append(method_name)
            
            # Check for custom action decorator (for ViewSets)
            if self._has_action_decorator(node):
                action_info = self._extract_action_info(node)
                view_info.custom_actions.append(action_info)
                
        except Exception as e:
            logger.warning(f"Failed to analyze view method {node.name}: {str(e)}")
    
    def _has_action_decorator(self, node: ast.FunctionDef) -> bool:
        """Check if a method has @action decorator"""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'action':
                return True
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name) and decorator.func.id == 'action':
                    return True
        return False
    
    def _extract_action_info(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract information from @action decorator"""
        action_info = {
            'name': node.name,
            'methods': ['get'],  # default
            'detail': True,  # default
            'url_path': node.name,
            'url_name': node.name,
        }
        
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                if decorator.func.id == 'action':
                    # Extract action parameters
                    for keyword in decorator.keywords:
                        if keyword.arg == 'methods':
                            action_info['methods'] = self._extract_list_value(keyword.value)
                        elif keyword.arg == 'detail':
                            action_info['detail'] = self._extract_literal_value(keyword.value)
                        elif keyword.arg == 'url_path':
                            action_info['url_path'] = self._extract_literal_value(keyword.value)
                        elif keyword.arg == 'url_name':
                            action_info['url_name'] = self._extract_literal_value(keyword.value)
        
        return action_info
    
    def _extract_literal_or_name_value(self, node: ast.AST) -> Any:
        """Extract literal value or name from AST node"""
        literal = self._extract_literal_value(node)
        if literal is not None:
            return literal
        
        return self._get_name_from_node(node)
    
    def _extract_literal_value(self, node: ast.AST) -> Any:
        """Extract literal value from AST node"""
        try:
            if isinstance(node, ast.Str):
                return node.s
            elif isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.NameConstant):
                return node.value
            elif isinstance(node, ast.List):
                return [self._extract_literal_value(item) for item in node.elts]
            elif isinstance(node, ast.Tuple):
                return tuple(self._extract_literal_value(item) for item in node.elts)
        except Exception:
            pass
        
        return None
    
    def _extract_list_value(self, node: ast.AST) -> List[str]:
        """Extract list of names from AST node"""
        if isinstance(node, ast.List):
            items = []
            for item in node.elts:
                name = self._get_name_from_node(item)
                if name:
                    items.append(name)
                else:
                    # Try to extract literal string
                    literal = self._extract_literal_value(item)
                    if literal:
                        items.append(str(literal))
            return items
        elif isinstance(node, ast.Tuple):
            items = []
            for item in node.elts:
                name = self._get_name_from_node(item)
                if name:
                    items.append(name)
            return items
        
        return []
    
    def _extract_model_from_queryset(self, node: ast.AST) -> Optional[str]:
        """Extract model name from queryset expression"""
        try:
            if isinstance(node, ast.Attribute):
                # Model.objects.all() pattern
                if (node.attr == 'all' and 
                    isinstance(node.value, ast.Attribute) and 
                    node.value.attr == 'objects'):
                    return self._get_name_from_node(node.value.value)
            elif isinstance(node, ast.Call):
                # Model.objects.filter(...) pattern
                if isinstance(node.func, ast.Attribute) and node.func.attr in ['filter', 'exclude', 'all']:
                    return self._extract_model_from_queryset(node.func.value)
        except Exception:
            pass
        
        return None
    
    def _generate_endpoints(self, view_info: ViewInfo) -> None:
        """Generate endpoint information based on view type and methods"""
        try:
            # Get HTTP methods for this view type
            methods = self.view_methods.get(view_info.view_type, ['get'])
            
            # For ViewSets, we need to map methods to actions
            if 'viewset' in view_info.view_type:
                self._generate_viewset_endpoints(view_info)
            else:
                self._generate_view_endpoints(view_info, methods)
                
        except Exception as e:
            logger.warning(f"Failed to generate endpoints for {view_info.name}: {str(e)}")
    
    def _generate_view_endpoints(self, view_info: ViewInfo, methods: List[str]) -> None:
        """Generate endpoints for regular API views"""
        base_path = f"/{view_info.name.lower().replace('view', '').replace('api', '')}/"
        
        for method in methods:
            endpoint = ViewEndpoint(base_path, method, view_info.name)
            endpoint.serializer_class = view_info.serializer_class
            endpoint.permission_classes = view_info.permission_classes
            endpoint.authentication_classes = view_info.authentication_classes
            
            # Set description based on method and view type
            endpoint.description = self._generate_endpoint_description(
                method, view_info.view_type, view_info.model
            )
            
            view_info.endpoints.append(endpoint)
    
    def _generate_viewset_endpoints(self, view_info: ViewInfo) -> None:
        """Generate endpoints for ViewSets"""
        # Standard ViewSet actions
        actions = {
            'list': ('get', '/'),
            'create': ('post', '/'),
            'retrieve': ('get', '/{id}/'),
            'update': ('put', '/{id}/'),
            'partial_update': ('patch', '/{id}/'),
            'destroy': ('delete', '/{id}/'),
        }
        
        base_path = f"/{view_info.name.lower().replace('viewset', '').replace('api', '')}/"
        
        # Generate standard actions based on view type
        if view_info.view_type == 'model_viewset':
            # Full CRUD operations
            for action, (method, path_suffix) in actions.items():
                path = base_path.rstrip('/') + path_suffix
                endpoint = ViewEndpoint(path, method, view_info.name)
                endpoint.function_name = action
                endpoint.serializer_class = view_info.serializer_class
                endpoint.permission_classes = view_info.permission_classes
                endpoint.authentication_classes = view_info.authentication_classes
                endpoint.description = self._generate_endpoint_description(
                    method, action, view_info.model
                )
                view_info.endpoints.append(endpoint)
                
        elif view_info.view_type == 'readonly_model_viewset':
            # Only list and retrieve
            for action in ['list', 'retrieve']:
                method, path_suffix = actions[action]
                path = base_path.rstrip('/') + path_suffix
                endpoint = ViewEndpoint(path, method, view_info.name)
                endpoint.function_name = action
                endpoint.serializer_class = view_info.serializer_class
                endpoint.permission_classes = view_info.permission_classes
                endpoint.authentication_classes = view_info.authentication_classes
                endpoint.description = self._generate_endpoint_description(
                    method, action, view_info.model
                )
                view_info.endpoints.append(endpoint)
        
        # Add custom actions
        for action_info in view_info.custom_actions:
            for method in action_info.get('methods', ['get']):
                if action_info.get('detail', True):
                    path = f"{base_path.rstrip('/')}/{{id}}/{action_info['url_path']}/"
                else:
                    path = f"{base_path.rstrip('/')}/{action_info['url_path']}/"
                
                endpoint = ViewEndpoint(path, method, view_info.name)
                endpoint.function_name = action_info['name']
                endpoint.serializer_class = view_info.serializer_class
                endpoint.permission_classes = view_info.permission_classes
                endpoint.authentication_classes = view_info.authentication_classes
                endpoint.description = f"Custom action: {action_info['name']}"
                view_info.endpoints.append(endpoint)
    
    def _generate_endpoint_description(self, method: str, action_or_type: str, model: Optional[str]) -> str:
        """Generate human-readable description for an endpoint"""
        method = method.upper()
        model_name = model or "resource"
        
        descriptions = {
            ('GET', 'list'): f"List all {model_name} instances",
            ('POST', 'create'): f"Create a new {model_name} instance",
            ('GET', 'retrieve'): f"Retrieve a specific {model_name} instance",
            ('PUT', 'update'): f"Update a specific {model_name} instance",
            ('PATCH', 'partial_update'): f"Partially update a specific {model_name} instance",
            ('DELETE', 'destroy'): f"Delete a specific {model_name} instance",
        }
        
        return descriptions.get((method, action_or_type), f"{method} {model_name}")
    
    def map_views_to_urls(self, views: List[ViewInfo], url_patterns: List[Dict]) -> None:
        """Map view classes to their URL patterns"""
        try:
            for view in views:
                for pattern in url_patterns:
                    view_name = pattern.get('view', '')
                    if view.name in view_name:
                        # Update endpoint paths with actual URL patterns
                        for endpoint in view.endpoints:
                            endpoint.path = self._resolve_url_pattern(
                                pattern.get('pattern', endpoint.path),
                                endpoint.path
                            )
        except Exception as e:
            logger.warning(f"Failed to map views to URLs: {str(e)}")
    
    def _resolve_url_pattern(self, url_pattern: str, default_path: str) -> str:
        """Resolve Django URL pattern to actual path"""
        try:
            # Convert Django URL pattern to path
            # This is a simplified conversion - real implementation would be more complex
            resolved = url_pattern
            
            # Replace Django URL pattern syntax with OpenAPI syntax
            resolved = re.sub(r'<int:(\w+)>', r'{\1}', resolved)
            resolved = re.sub(r'<str:(\w+)>', r'{\1}', resolved)
            resolved = re.sub(r'<slug:(\w+)>', r'{\1}', resolved)
            resolved = re.sub(r'<uuid:(\w+)>', r'{\1}', resolved)
            
            # Ensure it starts with /
            if not resolved.startswith('/'):
                resolved = '/' + resolved
            
            # Ensure it ends with /
            if not resolved.endswith('/'):
                resolved += '/'
            
            return resolved
        except Exception:
            return default_path
    
    def extract_endpoint_schemas(self, views: List[ViewInfo]) -> Dict[str, Dict]:
        """Extract detailed endpoint schemas for each view"""
        schemas = {}
        
        for view in views:
            view_schemas = {}
            
            for endpoint in view.endpoints:
                endpoint_key = f"{endpoint.method}_{endpoint.path.replace('/', '_').replace('{', '').replace('}', '').strip('_')}"
                
                schema = {
                    'method': endpoint.method,
                    'path': endpoint.path,
                    'description': endpoint.description,
                    'parameters': self._extract_endpoint_parameters(endpoint, view),
                    'request_schema': self._build_endpoint_request_schema(endpoint, view),
                    'response_schema': self._build_endpoint_response_schema(endpoint, view),
                    'status_codes': self._determine_status_codes(endpoint),
                    'authentication': self._extract_authentication_info(endpoint, view),
                    'permissions': self._extract_permission_info(endpoint, view),
                    'filters': self._extract_filter_info(view),
                    'pagination': self._extract_pagination_info(view)
                }
                
                view_schemas[endpoint_key] = schema
            
            schemas[view.name] = view_schemas
        
        return schemas
    
    def _extract_endpoint_parameters(self, endpoint: ViewEndpoint, view: ViewInfo) -> List[Dict]:
        """Extract path and query parameters for an endpoint"""
        parameters = []
        
        # Extract path parameters
        import re
        path_params = re.findall(r'\{(\w+)\}', endpoint.path)
        for param in path_params:
            param_info = {
                'name': param,
                'in': 'path',
                'required': True,
                'type': 'string',  # Default, could be enhanced
                'description': f"Path parameter: {param}"
            }
            
            # Common parameter types
            if param in ['id', 'pk']:
                param_info['type'] = 'integer'
                param_info['description'] = f"Unique identifier for the {view.model or 'resource'}"
            elif param in ['slug']:
                param_info['type'] = 'string'
                param_info['description'] = f"URL slug for the {view.model or 'resource'}"
            
            parameters.append(param_info)
        
        # Extract query parameters based on view configuration
        if endpoint.method == 'GET':
            # Search parameters
            if view.search_fields:
                parameters.append({
                    'name': 'search',
                    'in': 'query',
                    'required': False,
                    'type': 'string',
                    'description': f"Search in fields: {', '.join(view.search_fields)}"
                })
            
            # Ordering parameters
            if view.ordering_fields:
                parameters.append({
                    'name': 'ordering',
                    'in': 'query',
                    'required': False,
                    'type': 'string',
                    'description': f"Order by fields: {', '.join(view.ordering_fields)}. Prefix with '-' for descending order."
                })
            
            # Pagination parameters
            if 'list' in endpoint.function_name.lower() or endpoint.path.endswith('/'):
                parameters.extend([
                    {
                        'name': 'page',
                        'in': 'query',
                        'required': False,
                        'type': 'integer',
                        'description': 'Page number for pagination'
                    },
                    {
                        'name': 'page_size',
                        'in': 'query',
                        'required': False,
                        'type': 'integer',
                        'description': 'Number of items per page'
                    }
                ])
            
            # Filtering parameters (basic inference)
            if view.filter_backends:
                # Add common filter parameters
                if view.model:
                    # Add status filter if common
                    parameters.append({
                        'name': 'status',
                        'in': 'query',
                        'required': False,
                        'type': 'string',
                        'description': 'Filter by status'
                    })
        
        return parameters
    
    def _build_endpoint_request_schema(self, endpoint: ViewEndpoint, view: ViewInfo) -> Optional[Dict]:
        """Build request schema for endpoints that accept data"""
        if endpoint.method in ['POST', 'PUT', 'PATCH']:
            if endpoint.serializer_class:
                return {
                    'type': 'object',
                    '$ref': f"#/components/schemas/{endpoint.serializer_class}Request"
                }
            else:
                # Generic request schema
                return {
                    'type': 'object',
                    'properties': {},
                    'description': f"Request data for {endpoint.method} {endpoint.path}"
                }
        return None
    
    def _build_endpoint_response_schema(self, endpoint: ViewEndpoint, view: ViewInfo) -> Dict:
        """Build response schema for an endpoint"""
        if endpoint.method == 'DELETE':
            return {
                'type': 'object',
                'properties': {},
                'description': 'No content returned'
            }
        
        if endpoint.serializer_class or endpoint.response_serializer:
            serializer_name = endpoint.response_serializer or endpoint.serializer_class
            
            # Check if it's a list endpoint
            if 'list' in endpoint.function_name.lower() or (endpoint.method == 'GET' and endpoint.path.endswith('/')):
                return {
                    'type': 'object',
                    'properties': {
                        'count': {
                            'type': 'integer',
                            'description': 'Total number of items'
                        },
                        'next': {
                            'type': 'string',
                            'nullable': True,
                            'description': 'URL to next page'
                        },
                        'previous': {
                            'type': 'string',
                            'nullable': True,
                            'description': 'URL to previous page'
                        },
                        'results': {
                            'type': 'array',
                            'items': {
                                '$ref': f"#/components/schemas/{serializer_name}"
                            }
                        }
                    }
                }
            else:
                return {
                    '$ref': f"#/components/schemas/{serializer_name}"
                }
        
        # Generic response
        return {
            'type': 'object',
            'properties': {},
            'description': f"Response from {endpoint.method} {endpoint.path}"
        }
    
    def _determine_status_codes(self, endpoint: ViewEndpoint) -> List[int]:
        """Determine possible status codes for an endpoint"""
        base_codes = [400, 401, 403, 500]  # Common error codes
        
        if endpoint.method == 'GET':
            return [200, 404] + base_codes
        elif endpoint.method == 'POST':
            return [201, 400] + base_codes
        elif endpoint.method in ['PUT', 'PATCH']:
            return [200, 404] + base_codes
        elif endpoint.method == 'DELETE':
            return [204, 404] + base_codes
        
        return [200] + base_codes
    
    def _extract_authentication_info(self, endpoint: ViewEndpoint, view: ViewInfo) -> Dict:
        """Extract authentication information"""
        auth_info = {
            'required': True,  # Default assumption
            'types': []
        }
        
        auth_classes = endpoint.authentication_classes or view.authentication_classes
        
        if auth_classes:
            for auth_class in auth_classes:
                if 'Token' in auth_class:
                    auth_info['types'].append('token')
                elif 'Session' in auth_class:
                    auth_info['types'].append('session')
                elif 'JWT' in auth_class:
                    auth_info['types'].append('jwt')
                elif 'Basic' in auth_class:
                    auth_info['types'].append('basic')
                else:
                    auth_info['types'].append('custom')
        
        if not auth_info['types']:
            auth_info['types'] = ['token']  # Default assumption
        
        return auth_info
    
    def _extract_permission_info(self, endpoint: ViewEndpoint, view: ViewInfo) -> Dict:
        """Extract permission information"""
        permission_info = {
            'required_permissions': [],
            'description': ''
        }
        
        permission_classes = endpoint.permission_classes or view.permission_classes
        
        if permission_classes:
            for permission_class in permission_classes:
                if 'IsAuthenticated' in permission_class:
                    permission_info['required_permissions'].append('authenticated')
                elif 'IsOwner' in permission_class:
                    permission_info['required_permissions'].append('owner')
                elif 'IsStaff' in permission_class:
                    permission_info['required_permissions'].append('staff')
                elif 'IsAdmin' in permission_class:
                    permission_info['required_permissions'].append('admin')
                elif 'ReadOnly' in permission_class:
                    permission_info['required_permissions'].append('read_only')
                else:
                    permission_info['required_permissions'].append('custom')
        
        # Generate description
        if permission_info['required_permissions']:
            permission_info['description'] = f"Requires: {', '.join(permission_info['required_permissions'])}"
        else:
            permission_info['description'] = "No specific permissions required"
        
        return permission_info
    
    def _extract_filter_info(self, view: ViewInfo) -> Dict:
        """Extract filtering information"""
        filter_info = {
            'enabled': bool(view.filter_backends),
            'search_fields': view.search_fields,
            'ordering_fields': view.ordering_fields,
            'filterset_class': view.filterset_class,
            'backends': view.filter_backends
        }
        
        return filter_info
    
    def _extract_pagination_info(self, view: ViewInfo) -> Dict:
        """Extract pagination information"""
        pagination_info = {
            'enabled': view.pagination_class is not None,
            'pagination_class': view.pagination_class,
            'style': 'page_number'  # Default Django REST framework style
        }
        
        if view.pagination_class:
            if 'Limit' in view.pagination_class:
                pagination_info['style'] = 'limit_offset'
            elif 'Cursor' in view.pagination_class:
                pagination_info['style'] = 'cursor'
        
        return pagination_info
    
    def generate_endpoint_examples(self, view: ViewInfo) -> Dict[str, Dict]:
        """Generate example requests and responses for view endpoints"""
        examples = {}
        
        for endpoint in view.endpoints:
            endpoint_key = f"{endpoint.method}_{endpoint.path.replace('/', '_').replace('{', '').replace('}', '').strip('_')}"
            
            endpoint_examples = {
                'request_examples': self._generate_request_examples(endpoint, view),
                'response_examples': self._generate_response_examples(endpoint, view),
                'curl_examples': self._generate_curl_examples(endpoint, view)
            }
            
            examples[endpoint_key] = endpoint_examples
        
        return examples
    
    def _generate_request_examples(self, endpoint: ViewEndpoint, view: ViewInfo) -> Dict:
        """Generate request examples for an endpoint"""
        examples = {}
        
        if endpoint.method in ['POST', 'PUT', 'PATCH']:
            if endpoint.serializer_class:
                examples['basic'] = {
                    'description': f'Basic {endpoint.method} request',
                    'content_type': 'application/json',
                    'data': self._generate_example_request_data(endpoint, view)
                }
        
        return examples
    
    def _generate_response_examples(self, endpoint: ViewEndpoint, view: ViewInfo) -> Dict:
        """Generate response examples for an endpoint"""
        examples = {}
        
        # Success response
        examples['success'] = {
            'status_code': 200 if endpoint.method == 'GET' else (201 if endpoint.method == 'POST' else 200),
            'description': 'Successful response',
            'data': self._generate_example_response_data(endpoint, view)
        }
        
        # Error responses
        if endpoint.method in ['POST', 'PUT', 'PATCH']:
            examples['validation_error'] = {
                'status_code': 400,
                'description': 'Validation error',
                'data': {
                    'error': {
                        'field_name': ['This field is required.']
                    }
                }
            }
        
        if 'retrieve' in endpoint.function_name or '{' in endpoint.path:
            examples['not_found'] = {
                'status_code': 404,
                'description': 'Resource not found',
                'data': {
                    'detail': 'Not found.'
                }
            }
        
        return examples
    
    def _generate_curl_examples(self, endpoint: ViewEndpoint, view: ViewInfo) -> List[str]:
        """Generate curl command examples"""
        curl_examples = []
        
        base_url = "https://api.example.com"
        headers = ["-H 'Authorization: Token your-token-here'", "-H 'Content-Type: application/json'"]
        
        if endpoint.method == 'GET':
            curl_cmd = f"curl -X GET {base_url}{endpoint.path}"
            if headers:
                curl_cmd += " " + " ".join(headers[:1])  # Just auth header for GET
            curl_examples.append(curl_cmd)
            
        elif endpoint.method in ['POST', 'PUT', 'PATCH']:
            data = self._generate_example_request_data(endpoint, view)
            curl_cmd = f"curl -X {endpoint.method} {base_url}{endpoint.path}"
            curl_cmd += " " + " ".join(headers)
            if data:
                import json
                curl_cmd += f" -d '{json.dumps(data)}'"
            curl_examples.append(curl_cmd)
            
        elif endpoint.method == 'DELETE':
            curl_cmd = f"curl -X DELETE {base_url}{endpoint.path}"
            curl_cmd += " " + " ".join(headers[:1])  # Just auth header
            curl_examples.append(curl_cmd)
        
        return curl_examples
    
    def _generate_example_request_data(self, endpoint: ViewEndpoint, view: ViewInfo) -> Dict:
        """Generate example request data based on the endpoint"""
        # This is a simplified example - in practice, you'd use the serializer schema
        if view.model:
            model_name = view.model.lower()
            return {
                'name': f'Example {model_name}',
                'description': f'This is an example {model_name}',
                'status': 'active'
            }
        
        return {'field': 'value'}
    
    def _generate_example_response_data(self, endpoint: ViewEndpoint, view: ViewInfo) -> Dict:
        """Generate example response data based on the endpoint"""
        if endpoint.method == 'DELETE':
            return {}
        
        # List endpoint
        if 'list' in endpoint.function_name.lower() or (endpoint.method == 'GET' and endpoint.path.endswith('/')):
            return {
                'count': 10,
                'next': None,
                'previous': None,
                'results': [self._generate_single_item_example(view)]
            }
        
        # Detail endpoint
        return self._generate_single_item_example(view)
    
    def _generate_single_item_example(self, view: ViewInfo) -> Dict:
        """Generate example data for a single item"""
        if view.model:
            model_name = view.model.lower()
            return {
                'id': 1,
                'name': f'Example {model_name}',
                'description': f'This is an example {model_name}',
                'status': 'active',
                'created_at': '2023-12-01T12:00:00Z',
                'updated_at': '2023-12-01T12:00:00Z'
            }
        
        return {
            'id': 1,
            'name': 'Example Item',
            'created_at': '2023-12-01T12:00:00Z'
        }