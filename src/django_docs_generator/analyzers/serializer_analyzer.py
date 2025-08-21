"""
Django REST Framework serializer analyzer for detailed field analysis
"""

import ast
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from ..core.config import DjangoDocsConfig

logger = logging.getLogger(__name__)


class SerializerField:
    """Represents a single serializer field"""
    
    def __init__(self, name: str, field_type: str):
        self.name = name
        self.field_type = field_type
        self.required = True
        self.read_only = False
        self.write_only = False
        self.allow_null = False
        self.allow_blank = False
        self.default = None
        self.help_text = ""
        self.source = None
        self.validators = []
        self.choices = []
        self.max_length = None
        self.min_length = None
        self.max_value = None
        self.min_value = None
        self.related_model = None
        self.nested_serializer = None
        self.method_name = None  # For SerializerMethodField
        self.child_field = None  # For ListField
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert field to dictionary representation"""
        return {
            'name': self.name,
            'type': self.field_type,
            'required': self.required,
            'read_only': self.read_only,
            'write_only': self.write_only,
            'allow_null': self.allow_null,
            'allow_blank': self.allow_blank,
            'default': self.default,
            'help_text': self.help_text,
            'source': self.source,
            'validators': self.validators,
            'choices': self.choices,
            'max_length': self.max_length,
            'min_length': self.min_length,
            'max_value': self.max_value,
            'min_value': self.min_value,
            'related_model': self.related_model,
            'nested_serializer': self.nested_serializer,
            'method_name': self.method_name,
            'child_field': self.child_field.to_dict() if self.child_field else None,
        }


class SerializerInfo:
    """Information about a Django REST framework serializer"""
    
    def __init__(self, name: str, file_path: str):
        self.name = name
        self.file_path = file_path
        self.base_classes = []
        self.fields: Dict[str, SerializerField] = {}
        self.meta_info = {}
        self.docstring = ""
        self.methods = []
        self.nested_serializers: Set[str] = set()
        self.related_models: Set[str] = set()
        self.line_number = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert serializer info to dictionary"""
        return {
            'name': self.name,
            'file_path': self.file_path,
            'base_classes': self.base_classes,
            'fields': {name: field.to_dict() for name, field in self.fields.items()},
            'meta_info': self.meta_info,
            'docstring': self.docstring,
            'methods': self.methods,
            'nested_serializers': list(self.nested_serializers),
            'related_models': list(self.related_models),
            'line_number': self.line_number,
        }


class SerializerAnalyzer:
    """
    Analyzes Django REST Framework serializers to extract field information,
    relationships, and metadata for documentation generation
    """
    
    def __init__(self, config: DjangoDocsConfig):
        self.config = config
        
        # DRF field type mappings
        self.drf_field_types = {
            'BooleanField': 'boolean',
            'CharField': 'string',
            'ChoiceField': 'choice',
            'DateField': 'date',
            'DateTimeField': 'datetime',
            'DecimalField': 'decimal',
            'DictField': 'object',
            'EmailField': 'email',
            'FileField': 'file',
            'FloatField': 'float',
            'ImageField': 'image',
            'IntegerField': 'integer',
            'JSONField': 'json',
            'ListField': 'list',
            'ModelField': 'model',
            'PrimaryKeyRelatedField': 'primary_key',
            'ReadOnlyField': 'read_only',
            'SerializerMethodField': 'method',
            'SlugField': 'slug',
            'TimeField': 'time',
            'URLField': 'url',
            'UUIDField': 'uuid',
            'HyperlinkedIdentityField': 'hyperlink_identity',
            'HyperlinkedRelatedField': 'hyperlink_related',
            'StringRelatedField': 'string_related',
            'SlugRelatedField': 'slug_related',
        }
        
        # Field attributes that can be analyzed
        self.field_attributes = {
            'required', 'read_only', 'write_only', 'allow_null', 'allow_blank',
            'default', 'help_text', 'source', 'max_length', 'min_length',
            'max_value', 'min_value', 'choices', 'child', 'method_name'
        }
    
    def analyze_app_serializers(self, app_name: str, app_info: Dict) -> List[SerializerInfo]:
        """
        Analyze all serializers in a Django app
        
        Args:
            app_name: Name of the Django app
            app_info: App information from scanner
            
        Returns:
            List of SerializerInfo objects
        """
        serializers = []
        
        try:
            # Get serializer files from app info
            serializer_files = app_info.get('serializers', [])
            
            for serializer_file in serializer_files:
                file_serializers = self.analyze_serializer_file(Path(serializer_file))
                serializers.extend(file_serializers)
            
            logger.info(f"Analyzed {len(serializers)} serializers in app '{app_name}'")
            
        except Exception as e:
            logger.error(f"Failed to analyze serializers in app '{app_name}': {str(e)}")
        
        return serializers
    
    def analyze_serializer_file(self, file_path: Path) -> List[SerializerInfo]:
        """
        Analyze a single serializer file
        
        Args:
            file_path: Path to the serializer file
            
        Returns:
            List of SerializerInfo objects found in the file
        """
        serializers = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Extract imports to understand field types
            imports = self._extract_imports(tree)
            
            # Find serializer classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if self._is_serializer_class(node):
                        serializer_info = self._analyze_serializer_class(
                            node, str(file_path), imports
                        )
                        if serializer_info:
                            serializers.append(serializer_info)
            
            logger.debug(f"Found {len(serializers)} serializers in {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to analyze serializer file {file_path}: {str(e)}")
        
        return serializers
    
    def _extract_imports(self, tree: ast.AST) -> Dict[str, str]:
        """Extract import statements to understand available field types"""
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
    
    def _is_serializer_class(self, node: ast.ClassDef) -> bool:
        """Check if a class is a Django REST framework serializer"""
        for base in node.bases:
            base_name = self._get_name_from_node(base)
            if base_name and any(serializer_type in base_name for serializer_type in 
                               ['Serializer', 'ModelSerializer', 'ListSerializer']):
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
    
    def _analyze_serializer_class(self, node: ast.ClassDef, file_path: str, imports: Dict[str, str]) -> Optional[SerializerInfo]:
        """Analyze a single serializer class"""
        try:
            serializer_info = SerializerInfo(node.name, file_path)
            serializer_info.line_number = node.lineno
            serializer_info.docstring = ast.get_docstring(node) or ""
            
            # Extract base classes
            for base in node.bases:
                base_name = self._get_name_from_node(base)
                if base_name:
                    serializer_info.base_classes.append(base_name)
            
            # Analyze class body
            for item in node.body:
                if isinstance(item, ast.Assign):
                    # Field assignments
                    self._analyze_field_assignment(item, serializer_info, imports)
                elif isinstance(item, ast.ClassDef):
                    # Meta class
                    if item.name == 'Meta':
                        serializer_info.meta_info = self._analyze_meta_class(item)
                elif isinstance(item, ast.FunctionDef):
                    # Methods (including SerializerMethodField methods)
                    serializer_info.methods.append(item.name)
            
            return serializer_info
            
        except Exception as e:
            logger.error(f"Failed to analyze serializer class {node.name}: {str(e)}")
            return None
    
    def _analyze_field_assignment(self, node: ast.Assign, serializer_info: SerializerInfo, imports: Dict[str, str]) -> None:
        """Analyze a field assignment in a serializer"""
        try:
            # Get field name
            if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
                return
            
            field_name = node.targets[0].id
            
            # Skip private fields
            if field_name.startswith('_'):
                return
            
            # Analyze field value
            field_info = self._analyze_field_value(node.value, field_name, imports)
            if field_info:
                serializer_info.fields[field_name] = field_info
                
                # Track relationships
                if field_info.nested_serializer:
                    serializer_info.nested_serializers.add(field_info.nested_serializer)
                if field_info.related_model:
                    serializer_info.related_models.add(field_info.related_model)
                    
        except Exception as e:
            logger.warning(f"Failed to analyze field assignment: {str(e)}")
    
    def _analyze_field_value(self, node: ast.AST, field_name: str, imports: Dict[str, str]) -> Optional[SerializerField]:
        """Analyze a field value (right side of assignment)"""
        try:
            if isinstance(node, ast.Call):
                # Field instantiation like CharField(max_length=100)
                field_type = self._get_field_type_from_call(node, imports)
                if not field_type:
                    return None
                
                field = SerializerField(field_name, field_type)
                
                # Analyze field arguments
                self._analyze_field_arguments(node, field)
                
                return field
                
        except Exception as e:
            logger.warning(f"Failed to analyze field value for {field_name}: {str(e)}")
        
        return None
    
    def _get_field_type_from_call(self, node: ast.Call, imports: Dict[str, str]) -> Optional[str]:
        """Get the field type from a field instantiation call"""
        func_name = self._get_name_from_node(node.func)
        if not func_name:
            return None
        
        # Resolve import aliases
        if func_name in imports:
            full_name = imports[func_name]
        else:
            full_name = func_name
        
        # Map to standard field type
        for drf_type, standard_type in self.drf_field_types.items():
            if drf_type in full_name:
                return standard_type
        
        # Return the original name if not found in mapping
        return func_name
    
    def _analyze_field_arguments(self, node: ast.Call, field: SerializerField) -> None:
        """Analyze arguments passed to a field constructor"""
        try:
            # Positional arguments
            for i, arg in enumerate(node.args):
                if i == 0 and isinstance(arg, ast.Str):
                    # First string argument might be help_text for some fields
                    field.help_text = arg.s
            
            # Keyword arguments
            for keyword in node.keywords:
                if keyword.arg in self.field_attributes:
                    value = self._extract_literal_value(keyword.value)
                    setattr(field, keyword.arg, value)
                elif keyword.arg == 'queryset':
                    # Related field queryset
                    field.related_model = self._extract_model_from_queryset(keyword.value)
                elif keyword.arg == 'many':
                    # Many-to-many field
                    if self._extract_literal_value(keyword.value):
                        field.field_type = f"list_{field.field_type}"
                        
        except Exception as e:
            logger.warning(f"Failed to analyze field arguments: {str(e)}")
    
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
            elif isinstance(node, ast.Dict):
                return {
                    self._extract_literal_value(k): self._extract_literal_value(v)
                    for k, v in zip(node.keys, node.values)
                }
        except Exception:
            pass
        
        return None
    
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
    
    def _analyze_meta_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Analyze serializer Meta class"""
        meta_info = {}
        
        try:
            for item in node.body:
                if isinstance(item, ast.Assign):
                    if len(item.targets) == 1 and isinstance(item.targets[0], ast.Name):
                        attr_name = item.targets[0].id
                        attr_value = self._extract_literal_value(item.value)
                        
                        if attr_value is not None:
                            meta_info[attr_name] = attr_value
                        elif attr_name == 'model':
                            # Extract model name
                            model_name = self._get_name_from_node(item.value)
                            if model_name:
                                meta_info[attr_name] = model_name
                                
        except Exception as e:
            logger.warning(f"Failed to analyze Meta class: {str(e)}")
        
        return meta_info
    
    def get_serializer_inheritance_tree(self, serializers: List[SerializerInfo]) -> Dict[str, List[str]]:
        """Build inheritance tree for serializers"""
        inheritance_tree = {}
        
        # Create a map of serializer names to their info
        serializer_map = {s.name: s for s in serializers}
        
        for serializer in serializers:
            children = []
            for other_serializer in serializers:
                if serializer.name in other_serializer.base_classes:
                    children.append(other_serializer.name)
            
            inheritance_tree[serializer.name] = children
        
        return inheritance_tree
    
    def get_field_dependencies(self, serializers: List[SerializerInfo]) -> Dict[str, Set[str]]:
        """Get dependencies between serializers through nested fields"""
        dependencies = {}
        
        for serializer in serializers:
            deps = set()
            
            # Add nested serializers
            deps.update(serializer.nested_serializers)
            
            # Add related models
            deps.update(serializer.related_models)
            
            dependencies[serializer.name] = deps
        
        return dependencies