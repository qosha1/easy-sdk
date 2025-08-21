"""
Main Django API Documentation Generator class
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Union

from rich.console import Console
from rich.progress import Progress, TaskID
from rich.table import Table

from ..analyzers.django_scanner import DjangoProjectScanner
from ..analyzers.serializer_analyzer import SerializerAnalyzer
from ..analyzers.view_analyzer import ViewAnalyzer
from ..ai.engine import AIAnalysisEngine
from ..generators.sphinx_generator import SphinxDocumentationGenerator
from ..generators.typescript_generator import TypeScriptGenerator
from .config import DjangoDocsConfig

logger = logging.getLogger(__name__)


class GenerationResult:
    """Result of documentation generation process"""
    
    def __init__(self):
        self.success = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.generated_files: List[Path] = []
        self.skipped_apps: List[str] = []
        self.processed_apps: List[str] = []
        self.generation_time: float = 0.0
        self.statistics: Dict[str, int] = {}
    
    def add_error(self, error: str) -> None:
        """Add an error to the result"""
        self.errors.append(error)
        self.success = False
        logger.error(error)
    
    def add_warning(self, warning: str) -> None:
        """Add a warning to the result"""
        self.warnings.append(warning)
        logger.warning(warning)
    
    def add_generated_file(self, file_path: Path) -> None:
        """Add a generated file to the result"""
        self.generated_files.append(file_path)
    
    def print_summary(self, console: Console) -> None:
        """Print generation summary to console"""
        if self.success:
            console.print(f"✅ Documentation generation completed in {self.generation_time:.2f}s", style="green")
        else:
            console.print(f"❌ Documentation generation failed after {self.generation_time:.2f}s", style="red")
        
        # Statistics table
        if self.statistics:
            table = Table(title="Generation Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Count", justify="right", style="green")
            
            for metric, count in self.statistics.items():
                table.add_row(metric, str(count))
            
            console.print(table)
        
        # File summary
        if self.generated_files:
            console.print(f"\n📁 Generated {len(self.generated_files)} files:")
            for file_path in self.generated_files[:10]:  # Show first 10
                console.print(f"  • {file_path}")
            if len(self.generated_files) > 10:
                console.print(f"  ... and {len(self.generated_files) - 10} more files")
        
        # Warnings and errors
        if self.warnings:
            console.print(f"\n⚠️  {len(self.warnings)} warnings:", style="yellow")
            for warning in self.warnings[:5]:  # Show first 5
                console.print(f"  • {warning}")
        
        if self.errors:
            console.print(f"\n❌ {len(self.errors)} errors:", style="red")
            for error in self.errors[:5]:  # Show first 5
                console.print(f"  • {error}")


class DjangoDocsGenerator:
    """
    Main class for generating Django API documentation using AI-powered analysis
    """
    
    def __init__(
        self,
        project_path: Union[str, Path],
        config: Optional[DjangoDocsConfig] = None,
        config_path: Optional[Union[str, Path]] = None
    ):
        """
        Initialize the Django documentation generator
        
        Args:
            project_path: Path to Django project root
            config: Configuration object (optional)
            config_path: Path to configuration file (optional)
        """
        self.project_path = Path(project_path)
        
        # Load configuration
        if config:
            self.config = config
        elif config_path:
            self.config = DjangoDocsConfig.from_file(config_path)
        else:
            # Try to load from Django settings, fallback to default
            self.config = DjangoDocsConfig.from_django_settings(self.project_path)
        
        # Initialize console for rich output
        self.console = Console()
        
        # Initialize components
        self._initialize_components()
        
        # Setup logging
        self._setup_logging()
    
    def _initialize_components(self) -> None:
        """Initialize all generator components"""
        self.scanner = DjangoProjectScanner(self.config)
        self.serializer_analyzer = SerializerAnalyzer(self.config)
        self.view_analyzer = ViewAnalyzer(self.config)
        self.ai_engine = AIAnalysisEngine(self.config)
        self.sphinx_generator = SphinxDocumentationGenerator(self.config)
        self.typescript_generator = TypeScriptGenerator(self.config)
    
    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        level = logging.DEBUG if self.config.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def generate_all(self) -> GenerationResult:
        """
        Generate all documentation types (Sphinx + TypeScript)
        
        Returns:
            GenerationResult with details about the generation process
        """
        start_time = time.time()
        result = GenerationResult()
        
        try:
            with Progress(console=self.console) as progress:
                # Main progress task
                main_task = progress.add_task("🔍 Generating API documentation...", total=100)
                
                # Step 1: Scan Django project (20%)
                progress.update(main_task, description="🔍 Scanning Django project...")
                scan_result = self.scanner.scan_project(self.project_path)
                if not scan_result.success:
                    for error in scan_result.errors:
                        result.add_error(f"Scanner error: {error}")
                    return result
                
                progress.update(main_task, advance=20)
                
                # Step 2: Analyze serializers and views (30%)
                progress.update(main_task, description="🔬 Analyzing serializers and views...")
                analysis_result = self._analyze_django_components(scan_result.discovered_apps)
                if not analysis_result:
                    result.add_error("Failed to analyze Django components")
                    return result
                
                progress.update(main_task, advance=30)
                
                # Step 3: AI-powered analysis (20%)
                progress.update(main_task, description="🧠 Running AI analysis...")
                ai_result = self._run_ai_analysis(analysis_result)
                progress.update(main_task, advance=20)
                
                # Step 4: Generate Sphinx documentation (15%)
                progress.update(main_task, description="📚 Generating Sphinx documentation...")
                sphinx_result = self.generate_sphinx_docs()
                if not sphinx_result.success:
                    for error in sphinx_result.errors:
                        result.add_error(f"Sphinx generation error: {error}")
                
                result.generated_files.extend(sphinx_result.generated_files)
                progress.update(main_task, advance=15)
                
                # Step 5: Generate TypeScript interfaces (15%)
                progress.update(main_task, description="📝 Generating TypeScript interfaces...")
                typescript_result = self.generate_typescript_types()
                if not typescript_result.success:
                    for error in typescript_result.errors:
                        result.add_error(f"TypeScript generation error: {error}")
                
                result.generated_files.extend(typescript_result.generated_files)
                progress.update(main_task, advance=15)
                
                progress.update(main_task, description="✅ Documentation generation complete!")
        
        except Exception as e:
            result.add_error(f"Unexpected error during generation: {str(e)}")
            logger.exception("Unexpected error during documentation generation")
        
        finally:
            result.generation_time = time.time() - start_time
            result.statistics = self._compile_statistics()
        
        return result
    
    def generate_sphinx_docs(self) -> GenerationResult:
        """
        Generate only Sphinx documentation
        
        Returns:
            GenerationResult for Sphinx generation
        """
        result = GenerationResult()
        
        try:
            # Ensure output directories exist
            self.config.create_output_directories()
            
            # Generate Sphinx documentation
            sphinx_files = self.sphinx_generator.generate_documentation()
            result.generated_files.extend(sphinx_files)
            
        except Exception as e:
            result.add_error(f"Sphinx generation failed: {str(e)}")
            logger.exception("Failed to generate Sphinx documentation")
        
        return result
    
    def generate_typescript_types(self) -> GenerationResult:
        """
        Generate only TypeScript type definitions
        
        Returns:
            GenerationResult for TypeScript generation
        """
        result = GenerationResult()
        
        try:
            # Ensure output directories exist
            self.config.create_output_directories()
            
            # Generate TypeScript types
            typescript_files = self.typescript_generator.generate_types()
            result.generated_files.extend(typescript_files)
            
        except Exception as e:
            result.add_error(f"TypeScript generation failed: {str(e)}")
            logger.exception("Failed to generate TypeScript types")
        
        return result
    
    def _analyze_django_components(self, discovered_apps: Dict) -> Optional[Dict]:
        """Analyze Django serializers and views"""
        try:
            analysis_result = {}
            
            for app_name, app_info in discovered_apps.items():
                if not self.config.should_include_app(app_name):
                    continue
                
                # Analyze serializers
                serializer_analysis = self.serializer_analyzer.analyze_app_serializers(
                    app_name, app_info
                )
                
                # Analyze views
                view_analysis = self.view_analyzer.analyze_app_views(app_name, app_info)
                
                analysis_result[app_name] = {
                    'serializers': serializer_analysis,
                    'views': view_analysis,
                    'app_info': app_info
                }
            
            return analysis_result
            
        except Exception as e:
            logger.exception(f"Failed to analyze Django components: {str(e)}")
            return None
    
    def _run_ai_analysis(self, analysis_result: Dict) -> Dict:
        """Run AI analysis on the Django components"""
        try:
            # AI analysis will enhance the basic structural analysis
            enhanced_analysis = self.ai_engine.enhance_analysis(analysis_result)
            return enhanced_analysis
            
        except Exception as e:
            logger.exception(f"AI analysis failed: {str(e)}")
            # Return original analysis if AI fails
            return analysis_result
    
    def _compile_statistics(self) -> Dict[str, int]:
        """Compile generation statistics"""
        stats = {
            'Total Apps': len(self.scanner.discovered_apps) if hasattr(self.scanner, 'discovered_apps') else 0,
            'Processed Apps': len(self.config.include_apps) if self.config.include_apps else 0,
            'Generated Files': len([]),  # Will be updated with actual counts
            'Serializers Analyzed': 0,  # Will be updated
            'Views Analyzed': 0,  # Will be updated
            'TypeScript Interfaces': 0,  # Will be updated
        }
        
        return stats
    
    def validate_project(self) -> List[str]:
        """
        Validate that the project is a valid Django project
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not self.project_path.exists():
            errors.append(f"Project path does not exist: {self.project_path}")
            return errors
        
        # Check for manage.py
        manage_py = self.project_path / "manage.py"
        if not manage_py.exists():
            errors.append("No manage.py found - not a Django project")
        
        # Check for Django apps
        potential_apps = [d for d in self.project_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
        if not potential_apps:
            errors.append("No Django apps found in project")
        
        # Check for settings module
        if self.config.django_settings_module:
            try:
                import importlib
                importlib.import_module(self.config.django_settings_module)
            except ImportError:
                errors.append(f"Cannot import Django settings module: {self.config.django_settings_module}")
        
        return errors