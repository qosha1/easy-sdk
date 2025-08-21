"""
Django project scanner for discovering apps, models, views, and serializers
"""

import ast
import importlib.util
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

from ..core.config import DjangoDocsConfig

logger = logging.getLogger(__name__)


class ScanResult:
    """Result of Django project scanning"""
    
    def __init__(self):
        self.success = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.discovered_apps: Dict[str, Dict] = {}
        self.project_info: Dict = {}
    
    def add_error(self, error: str) -> None:
        """Add an error to the scan result"""
        self.errors.append(error)
        self.success = False
        logger.error(error)
    
    def add_warning(self, warning: str) -> None:
        """Add a warning to the scan result"""
        self.warnings.append(warning)
        logger.warning(warning)


class AppInfo:
    """Information about a Django app"""
    
    def __init__(self, name: str, path: Path):
        self.name = name
        self.path = path
        self.models_file: Optional[Path] = None
        self.views_files: List[Path] = []
        self.serializers_files: List[Path] = []
        self.urls_files: List[Path] = []
        self.apps_config: Optional[Dict] = None
        self.python_files: List[Path] = []
        self.has_rest_framework = False


class DjangoProjectScanner:
    """
    Scans Django projects to discover apps, models, views, serializers, and URL patterns
    """
    
    def __init__(self, config: DjangoDocsConfig):
        self.config = config
        self.project_path = config.project_path
        
        # File patterns to look for
        self.serializer_patterns = [
            re.compile(r'serializers?\.py$'),
            re.compile(r'.*serializers?\.py$'),
            re.compile(r'api/.*\.py$'),
        ]
        
        self.view_patterns = [
            re.compile(r'views?\.py$'),
            re.compile(r'.*views?\.py$'),
            re.compile(r'api/.*\.py$'),
            re.compile(r'viewsets?\.py$'),
        ]
        
        self.url_patterns = [
            re.compile(r'urls\.py$'),
            re.compile(r'.*urls\.py$'),
        ]
    
    def scan_project(self, project_path: Optional[Path] = None) -> ScanResult:
        """
        Scan a Django project and discover all apps and components
        
        Args:
            project_path: Optional override for project path
            
        Returns:
            ScanResult with discovered information
        """
        if project_path:
            self.project_path = project_path
        
        result = ScanResult()
        
        try:
            # Validate project structure
            if not self._validate_django_project():
                result.add_error(f"Not a valid Django project: {self.project_path}")
                return result
            
            # Discover Django settings
            project_info = self._discover_project_info()
            result.project_info = project_info
            
            # Discover Django apps
            apps = self._discover_django_apps()
            
            # Analyze each app
            for app_name, app_info in apps.items():
                if self.config.should_include_app(app_name):
                    detailed_info = self._analyze_app(app_info)
                    result.discovered_apps[app_name] = detailed_info
                else:
                    result.add_warning(f"Skipping app: {app_name} (excluded by configuration)")
            
            logger.info(f"Successfully scanned Django project at {self.project_path}")
            logger.info(f"Discovered {len(result.discovered_apps)} apps")
            
        except Exception as e:
            result.add_error(f"Failed to scan Django project: {str(e)}")
            logger.exception("Django project scanning failed")
        
        return result
    
    def _validate_django_project(self) -> bool:
        """Validate that this is a Django project"""
        if not self.project_path.exists():
            return False
        
        # Look for manage.py
        manage_py = self.project_path / "manage.py"
        if not manage_py.exists():
            return False
        
        # Look for settings file or directory in multiple locations
        potential_locations = [
            # Direct in root (non-standard but possible)
            "settings.py",
            "settings",
            # Standard Django structure: project_name/settings.py
        ]
        
        # Add subdirectories that might contain settings
        for item in self.project_path.iterdir():
            if item.is_dir() and not item.name.startswith('.') and not item.name.startswith('__'):
                potential_locations.extend([
                    f"{item.name}/settings.py",
                    f"{item.name}/settings",
                ])
        
        # Check all potential locations
        for potential_setting in potential_locations:
            settings_path = self.project_path / potential_setting
            if settings_path.exists():
                return True
        
        return False
    
    def _discover_project_info(self) -> Dict:
        """Discover Django project information"""
        info = {
            'name': self.project_path.name,
            'path': str(self.project_path),
            'manage_py': None,
            'settings_module': None,
            'root_urlconf': None,
            'installed_apps': [],
        }
        
        # Find manage.py
        manage_py = self.project_path / "manage.py"
        if manage_py.exists():
            info['manage_py'] = str(manage_py)
        
        # Try to discover settings
        settings_info = self._discover_settings()
        if settings_info:
            info.update(settings_info)
        
        return info
    
    def _discover_settings(self) -> Optional[Dict]:
        """Discover Django settings information"""
        settings_files = []
        
        # Look for settings files
        for root, dirs, files in os.walk(self.project_path):
            for file in files:
                if file == 'settings.py' or file.startswith('settings_'):
                    settings_files.append(Path(root) / file)
        
        if not settings_files:
            return None
        
        # Use the first settings file found
        settings_file = settings_files[0]
        
        try:
            # Parse settings file to extract configuration
            with open(settings_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            settings_info = {
                'settings_file': str(settings_file),
                'installed_apps': self._extract_installed_apps(tree),
                'root_urlconf': self._extract_setting_value(tree, 'ROOT_URLCONF'),
            }
            
            return settings_info
            
        except Exception as e:
            logger.warning(f"Failed to parse settings file {settings_file}: {str(e)}")
            return None
    
    def _extract_installed_apps(self, tree: ast.AST) -> List[str]:
        """Extract INSTALLED_APPS from Django settings AST"""
        installed_apps = []
        
        for node in ast.walk(tree):
            if (isinstance(node, ast.Assign) and 
                len(node.targets) == 1 and
                isinstance(node.targets[0], ast.Name) and
                node.targets[0].id == 'INSTALLED_APPS'):
                
                if isinstance(node.value, ast.List):
                    for item in node.value.elts:
                        if isinstance(item, ast.Str):
                            installed_apps.append(item.s)
                        elif isinstance(item, ast.Constant) and isinstance(item.value, str):
                            installed_apps.append(item.value)
        
        return installed_apps
    
    def _extract_setting_value(self, tree: ast.AST, setting_name: str) -> Optional[str]:
        """Extract a specific setting value from Django settings AST"""
        for node in ast.walk(tree):
            if (isinstance(node, ast.Assign) and 
                len(node.targets) == 1 and
                isinstance(node.targets[0], ast.Name) and
                node.targets[0].id == setting_name):
                
                if isinstance(node.value, ast.Str):
                    return node.value.s
                elif isinstance(node.value, ast.Constant) and isinstance(node.value, str):
                    return node.value.value
        
        return None
    
    def _discover_django_apps(self) -> Dict[str, AppInfo]:
        """Discover Django apps in the project"""
        apps = {}
        
        # Look for directories that could be Django apps
        for item in self.project_path.iterdir():
            if not item.is_dir():
                continue
            
            # Skip common non-app directories
            if item.name.startswith('.') or item.name in ['__pycache__', 'static', 'media', 'templates']:
                continue
            
            # Check if this looks like a Django app
            if self._is_django_app(item):
                app_info = AppInfo(item.name, item)
                apps[item.name] = app_info
        
        return apps
    
    def _is_django_app(self, path: Path) -> bool:
        """Check if a directory is a Django app"""
        # Must have __init__.py
        if not (path / "__init__.py").exists():
            return False
        
        # Look for Django app indicators
        django_files = ['models.py', 'views.py', 'admin.py', 'apps.py']
        
        for django_file in django_files:
            if (path / django_file).exists():
                return True
        
        # Check for any Python files that might be Django components
        for file in path.glob("*.py"):
            if file.name in ['serializers.py', 'viewsets.py', 'urls.py']:
                return True
        
        return False
    
    def _analyze_app(self, app_info: AppInfo) -> Dict:
        """Analyze a Django app in detail"""
        detailed_info = {
            'name': app_info.name,
            'path': str(app_info.path),
            'models': [],
            'views': [],
            'serializers': [],
            'urls': [],
            'has_rest_framework': False,
            'python_files': [],
        }
        
        # Find all Python files in the app
        python_files = list(app_info.path.glob("**/*.py"))
        detailed_info['python_files'] = [str(f) for f in python_files]
        
        # Categorize files
        for py_file in python_files:
            relative_path = py_file.relative_to(app_info.path)
            
            # Models
            if py_file.name == 'models.py' or 'models' in py_file.name:
                detailed_info['models'].append(str(py_file))
            
            # Views
            if any(pattern.search(str(relative_path)) for pattern in self.view_patterns):
                detailed_info['views'].append(str(py_file))
                
                # Check for REST framework usage
                if self._has_rest_framework_imports(py_file):
                    detailed_info['has_rest_framework'] = True
            
            # Serializers
            if any(pattern.search(str(relative_path)) for pattern in self.serializer_patterns):
                detailed_info['serializers'].append(str(py_file))
                detailed_info['has_rest_framework'] = True
            
            # URLs
            if any(pattern.search(str(relative_path)) for pattern in self.url_patterns):
                detailed_info['urls'].append(str(py_file))
        
        # Analyze specific components
        detailed_info['model_classes'] = self._extract_model_classes(detailed_info['models'])
        detailed_info['view_classes'] = self._extract_view_classes(detailed_info['views'])
        detailed_info['serializer_classes'] = self._extract_serializer_classes(detailed_info['serializers'])
        detailed_info['url_patterns'] = self._extract_url_patterns(detailed_info['urls'])
        
        return detailed_info
    
    def _has_rest_framework_imports(self, file_path: Path) -> bool:
        """Check if a file imports Django REST framework"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for DRF import patterns
            drf_patterns = [
                r'from rest_framework',
                r'import rest_framework',
                r'from django_filters',
                r'APIView',
                r'ViewSet',
                r'Serializer',
            ]
            
            for pattern in drf_patterns:
                if re.search(pattern, content):
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Failed to check REST framework imports in {file_path}: {str(e)}")
            return False
    
    def _extract_model_classes(self, model_files: List[str]) -> List[Dict]:
        """Extract Django model classes from files"""
        model_classes = []
        
        for model_file in model_files:
            try:
                classes = self._extract_classes_from_file(Path(model_file), 'Model')
                model_classes.extend(classes)
            except Exception as e:
                logger.warning(f"Failed to extract models from {model_file}: {str(e)}")
        
        return model_classes
    
    def _extract_view_classes(self, view_files: List[str]) -> List[Dict]:
        """Extract Django view classes from files"""
        view_classes = []
        
        for view_file in view_files:
            try:
                # Look for various view base classes
                base_classes = ['View', 'APIView', 'ViewSet', 'ModelViewSet', 'GenericAPIView']
                for base_class in base_classes:
                    classes = self._extract_classes_from_file(Path(view_file), base_class)
                    view_classes.extend(classes)
            except Exception as e:
                logger.warning(f"Failed to extract views from {view_file}: {str(e)}")
        
        return view_classes
    
    def _extract_serializer_classes(self, serializer_files: List[str]) -> List[Dict]:
        """Extract Django REST framework serializer classes from files"""
        serializer_classes = []
        
        for serializer_file in serializer_files:
            try:
                # Look for serializer base classes
                base_classes = ['Serializer', 'ModelSerializer', 'ListSerializer']
                for base_class in base_classes:
                    classes = self._extract_classes_from_file(Path(serializer_file), base_class)
                    serializer_classes.extend(classes)
            except Exception as e:
                logger.warning(f"Failed to extract serializers from {serializer_file}: {str(e)}")
        
        return serializer_classes
    
    def _extract_classes_from_file(self, file_path: Path, base_class_name: str) -> List[Dict]:
        """Extract classes that inherit from a specific base class"""
        classes = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if class inherits from the target base class
                    for base in node.bases:
                        base_name = self._get_base_class_name(base)
                        if base_name and base_class_name in base_name:
                            class_info = {
                                'name': node.name,
                                'file': str(file_path),
                                'line': node.lineno,
                                'base_classes': [self._get_base_class_name(b) for b in node.bases],
                                'docstring': ast.get_docstring(node),
                                'methods': [method.name for method in node.body if isinstance(method, ast.FunctionDef)],
                            }
                            classes.append(class_info)
                            break
        
        except Exception as e:
            logger.warning(f"Failed to parse file {file_path}: {str(e)}")
        
        return classes
    
    def _get_base_class_name(self, base_node: ast.AST) -> Optional[str]:
        """Extract base class name from AST node"""
        if isinstance(base_node, ast.Name):
            return base_node.id
        elif isinstance(base_node, ast.Attribute):
            return f"{self._get_base_class_name(base_node.value)}.{base_node.attr}"
        else:
            return None
    
    def _extract_url_patterns(self, url_files: List[str]) -> List[Dict]:
        """Extract URL patterns from Django URL configuration files"""
        url_patterns = []
        
        for url_file in url_files:
            try:
                patterns = self._parse_url_file(Path(url_file))
                url_patterns.extend(patterns)
            except Exception as e:
                logger.warning(f"Failed to extract URL patterns from {url_file}: {str(e)}")
        
        return url_patterns
    
    def _parse_url_file(self, file_path: Path) -> List[Dict]:
        """Parse a Django URLs file to extract patterns"""
        patterns = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple regex-based extraction (could be enhanced with AST parsing)
            url_pattern_regex = r"path\(['\"]([^'\"]+)['\"],?\s*([^,\)]+)"
            
            matches = re.finditer(url_pattern_regex, content)
            
            for match in matches:
                pattern_info = {
                    'pattern': match.group(1),
                    'view': match.group(2).strip(),
                    'file': str(file_path),
                }
                patterns.append(pattern_info)
        
        except Exception as e:
            logger.warning(f"Failed to parse URL file {file_path}: {str(e)}")
        
        return patterns