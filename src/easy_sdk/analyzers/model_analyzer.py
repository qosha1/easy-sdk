"""
Django model analyzer for extracting field definitions, relationships, and metadata
"""

import ast
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from ..core.config import DjangoDocsConfig

logger = logging.getLogger(__name__)


class ModelField:
    """Represents a single model field"""
    
    def __init__(self, name: str, field_type: str):
        self.name = name
        self.field_type = field_type
        self.null = False
        self.blank = False
        self.default = None
        self.help_text = ""
        self.verbose_name = None
        self.choices = []
        self.max_length = None
        self.max_digits = None
        self.decimal_places = None
        self.upload_to = None
        self.related_model = None
        self.related_name = None
        self.on_delete = None
        self.validators = []
        self.unique = False
        self.db_index = False
        self.primary_key = False
        self.auto_created = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert field to dictionary representation"""
        return {
            'name': self.name,
            'type': self.field_type,
            'null': self.null,
            'blank': self.blank,
            'default': self.default,
            'help_text': self.help_text,
            'verbose_name': self.verbose_name,
            'choices': self.choices,
            'max_length': self.max_length,
            'max_digits': self.max_digits,
            'decimal_places': self.decimal_places,
            'upload_to': self.upload_to,
            'related_model': self.related_model,
            'related_name': self.related_name,
            'on_delete': self.on_delete,
            'validators': self.validators,
            'unique': self.unique,
            'db_index': self.db_index,
            'primary_key': self.primary_key,
            'auto_created': self.auto_created,
        }


class ModelInfo:
    """Information about a Django model"""
    
    def __init__(self, name: str, file_path: str):
        self.name = name
        self.file_path = file_path
        self.base_classes = []
        self.fields: Dict[str, ModelField] = {}
        self.meta_info = {}
        self.docstring = ""
        self.methods = []
        self.properties = []
        self.related_models: Set[str] = set()
        self.line_number = 0
        self.is_abstract = False
        self.proxy = False
        self.constraints = []
        self.indexes = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model info to dictionary"""
        return {
            'name': self.name,
            'file_path': self.file_path,
            'base_classes': self.base_classes,
            'fields': {name: field.to_dict() for name, field in self.fields.items()},
            'meta_info': self.meta_info,
            'docstring': self.docstring,
            'methods': self.methods,
            'properties': self.properties,
            'related_models': list(self.related_models),
            'line_number': self.line_number,
            'is_abstract': self.is_abstract,
            'proxy': self.proxy,
            'constraints': self.constraints,
            'indexes': self.indexes,
        }


class ModelAnalyzer:
    """
    Analyzes Django models to extract field definitions, relationships, 
    and metadata for documentation generation
    """
    
    def __init__(self, config: DjangoDocsConfig):
        self.config = config
        
        # Django field type mappings
        self.django_field_types = {
            'AutoField': 'auto',
            'BigAutoField': 'big_auto',
            'BigIntegerField': 'big_integer',
            'BinaryField': 'binary',
            'BooleanField': 'boolean',
            'CharField': 'string',
            'DateField': 'date',
            'DateTimeField': 'datetime',
            'DecimalField': 'decimal',
            'DurationField': 'duration',
            'EmailField': 'email',
            'FileField': 'file',
            'FilePathField': 'file_path',
            'FloatField': 'float',
            'ImageField': 'image',
            'IntegerField': 'integer',
            'GenericIPAddressField': 'ip_address',
            'JSONField': 'json',
            'PositiveIntegerField': 'positive_integer',
            'PositiveSmallIntegerField': 'positive_small_integer',
            'SlugField': 'slug',
            'SmallIntegerField': 'small_integer',
            'TextField': 'text',
            'TimeField': 'time',
            'URLField': 'url',
            'UUIDField': 'uuid',
            'ForeignKey': 'foreign_key',
            'ManyToManyField': 'many_to_many',
            'OneToOneField': 'one_to_one',
        }
        
        # Field attributes that can be analyzed
        self.field_attributes = {
            'null', 'blank', 'default', 'help_text', 'verbose_name',
            'choices', 'max_length', 'max_digits', 'decimal_places',
            'upload_to', 'related_name', 'on_delete', 'unique',
            'db_index', 'primary_key', 'validators'
        }
    
    def analyze_app_models(self, app_name: str, app_info: Dict) -> List[ModelInfo]:
        """
        Analyze all models in a Django app
        
        Args:
            app_name: Name of the Django app
            app_info: App information from scanner
            
        Returns:
            List of ModelInfo objects
        """
        models = []
        
        try:
            # Get model files from app info
            model_files = app_info.get('models', [])
            
            for model_file in model_files:
                file_models = self.analyze_model_file(Path(model_file))
                models.extend(file_models)
            
            logger.info(f"Analyzed {len(models)} models in app '{app_name}'")
            
        except Exception as e:
            logger.error(f"Failed to analyze models in app '{app_name}': {str(e)}")
        
        return models
    
    def analyze_model_file(self, file_path: Path) -> List[ModelInfo]:
        """
        Analyze a single model file
        
        Args:
            file_path: Path to the model file
            
        Returns:
            List of ModelInfo objects found in the file
        """
        models = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Extract imports to understand field types
            imports = self._extract_imports(tree)
            
            # Find model classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if self._is_model_class(node):
                        model_info = self._analyze_model_class(
                            node, str(file_path), imports
                        )
                        if model_info:
                            models.append(model_info)
            
            logger.debug(f"Found {len(models)} models in {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to analyze model file {file_path}: {str(e)}")
        
        return models
    
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
    
    def _is_model_class(self, node: ast.ClassDef) -> bool:
        """Check if a class is a Django model"""
        for base in node.bases:
            base_name = self._get_name_from_node(base)
            if base_name and any(model_type in base_name for model_type in 
                               ['Model', 'models.Model']):
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
    
    def _analyze_model_class(self, node: ast.ClassDef, file_path: str, imports: Dict[str, str]) -> Optional[ModelInfo]:
        """Analyze a single model class"""
        try:
            model_info = ModelInfo(node.name, file_path)
            model_info.line_number = node.lineno
            model_info.docstring = ast.get_docstring(node) or ""
            
            # Extract base classes
            for base in node.bases:
                base_name = self._get_name_from_node(base)
                if base_name:
                    model_info.base_classes.append(base_name)
            
            # Analyze class body
            for item in node.body:
                if isinstance(item, ast.Assign):
                    # Field assignments
                    self._analyze_field_assignment(item, model_info, imports)
                elif isinstance(item, ast.ClassDef):
                    # Meta class
                    if item.name == 'Meta':
                        model_info.meta_info = self._analyze_meta_class(item)
                        model_info.is_abstract = model_info.meta_info.get('abstract', False)
                        model_info.proxy = model_info.meta_info.get('proxy', False)
                elif isinstance(item, ast.FunctionDef):
                    # Methods and properties
                    if item.name.startswith('__') and item.name.endswith('__'):
                        # Skip dunder methods except __str__
                        if item.name == '__str__':
                            model_info.methods.append(item.name)
                    else:
                        # Check if it's a property
                        if self._is_property(item):
                            model_info.properties.append(item.name)
                        else:
                            model_info.methods.append(item.name)
            
            return model_info
            
        except Exception as e:
            logger.error(f"Failed to analyze model class {node.name}: {str(e)}")
            return None
    
    def _is_property(self, node: ast.FunctionDef) -> bool:
        """Check if a method is decorated with @property"""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'property':
                return True
        return False
    
    def _analyze_field_assignment(self, node: ast.Assign, model_info: ModelInfo, imports: Dict[str, str]) -> None:
        """Analyze a field assignment in a model"""
        try:
            # Get field name
            if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
                return
            
            field_name = node.targets[0].id
            
            # Skip private fields and class variables
            if field_name.startswith('_') or field_name.isupper():
                return
            
            # Analyze field value
            field_info = self._analyze_field_value(node.value, field_name, imports)
            if field_info:
                model_info.fields[field_name] = field_info
                
                # Track relationships
                if field_info.related_model:
                    model_info.related_models.add(field_info.related_model)
                    
        except Exception as e:
            logger.warning(f"Failed to analyze field assignment: {str(e)}")
    
    def _analyze_field_value(self, node: ast.AST, field_name: str, imports: Dict[str, str]) -> Optional[ModelField]:
        """Analyze a field value (right side of assignment)"""
        try:
            if isinstance(node, ast.Call):
                # Field instantiation like CharField(max_length=100)
                field_type = self._get_field_type_from_call(node, imports)
                if not field_type:
                    return None
                
                field = ModelField(field_name, field_type)
                
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
        for django_type, standard_type in self.django_field_types.items():
            if django_type in full_name:
                return standard_type
        
        # Return the original name if not found in mapping
        return func_name
    
    def _analyze_field_arguments(self, node: ast.Call, field: ModelField) -> None:
        """Analyze arguments passed to a field constructor"""
        try:
            # Positional arguments
            for i, arg in enumerate(node.args):
                if i == 0 and field.field_type in ['foreign_key', 'many_to_many', 'one_to_one']:
                    # First argument is the related model
                    field.related_model = self._get_name_from_node(arg)
                    if field.related_model and field.related_model.startswith("'") and field.related_model.endswith("'"):
                        # Remove quotes from string literals
                        field.related_model = field.related_model[1:-1]
            
            # Keyword arguments
            for keyword in node.keywords:
                if keyword.arg in self.field_attributes:
                    value = self._extract_literal_value(keyword.value)
                    setattr(field, keyword.arg, value)
                elif keyword.arg == 'to' and field.field_type in ['foreign_key', 'many_to_many', 'one_to_one']:
                    # Alternative way to specify related model
                    field.related_model = self._get_name_from_node(keyword.value)
                    if field.related_model and field.related_model.startswith("'") and field.related_model.endswith("'"):
                        field.related_model = field.related_model[1:-1]
                        
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
    
    def _analyze_meta_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Analyze model Meta class"""
        meta_info = {}
        
        try:
            for item in node.body:
                if isinstance(item, ast.Assign):
                    if len(item.targets) == 1 and isinstance(item.targets[0], ast.Name):
                        attr_name = item.targets[0].id
                        attr_value = self._extract_literal_value(item.value)
                        
                        if attr_value is not None:
                            meta_info[attr_name] = attr_value
                        elif attr_name in ['ordering', 'unique_together', 'index_together']:
                            # These are often tuples or lists
                            meta_info[attr_name] = self._extract_literal_value(item.value) or []
                                
        except Exception as e:
            logger.warning(f"Failed to analyze Meta class: {str(e)}")
        
        return meta_info
    
    def get_model_inheritance_tree(self, models: List[ModelInfo]) -> Dict[str, List[str]]:
        """Build inheritance tree for models"""
        inheritance_tree = {}
        
        # Create a map of model names to their info
        model_map = {m.name: m for m in models}
        
        for model in models:
            children = []
            for other_model in models:
                for base_class in other_model.base_classes:
                    if model.name in base_class:
                        children.append(other_model.name)
            
            inheritance_tree[model.name] = children
        
        return inheritance_tree
    
    def get_model_dependencies(self, models: List[ModelInfo]) -> Dict[str, Set[str]]:
        """Get dependencies between models through relationships"""
        dependencies = {}
        
        for model in models:
            deps = set()
            
            # Add related models from foreign keys and relationships
            deps.update(model.related_models)
            
            dependencies[model.name] = deps
        
        return dependencies
    
    def extract_model_relationships(self, models: List[ModelInfo]) -> Dict[str, Dict[str, List[Dict]]]:
        """Extract detailed relationship information between models"""
        relationships = {}
        
        for model in models:
            model_relationships = {
                'foreign_keys': [],
                'reverse_foreign_keys': [],
                'many_to_many': [],
                'one_to_one': []
            }
            
            # Analyze forward relationships
            for field_name, field in model.fields.items():
                if field.field_type == 'foreign_key':
                    model_relationships['foreign_keys'].append({
                        'field_name': field_name,
                        'related_model': field.related_model,
                        'related_name': field.related_name,
                        'on_delete': field.on_delete
                    })
                elif field.field_type == 'many_to_many':
                    model_relationships['many_to_many'].append({
                        'field_name': field_name,
                        'related_model': field.related_model,
                        'related_name': field.related_name
                    })
                elif field.field_type == 'one_to_one':
                    model_relationships['one_to_one'].append({
                        'field_name': field_name,
                        'related_model': field.related_model,
                        'related_name': field.related_name,
                        'on_delete': field.on_delete
                    })
            
            # Find reverse relationships
            for other_model in models:
                if other_model.name == model.name:
                    continue
                    
                for field_name, field in other_model.fields.items():
                    if field.related_model == model.name:
                        if field.field_type == 'foreign_key':
                            model_relationships['reverse_foreign_keys'].append({
                                'field_name': field.related_name or f"{other_model.name.lower()}_set",
                                'related_model': other_model.name,
                                'reverse_field': field_name
                            })
            
            relationships[model.name] = model_relationships
        
        return relationships