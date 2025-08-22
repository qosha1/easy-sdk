"""
Main CLI entry point for Django API Documentation Generator
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
from rich.console import Console
from rich.logging import RichHandler

from ..core.config import DjangoDocsConfig
from ..core.generator import DjangoDocsGenerator
from ..generators.sdk_manager import SDKManager


# Setup rich console
console = Console()


def setup_logging(verbose: bool) -> None:
    """Setup logging with rich handler"""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)]
    )


@click.group(invoke_without_command=True)
@click.pass_context
@click.argument('project_path', type=click.Path(exists=True, file_okay=False, dir_okay=True), required=False)
@click.option('--config', '-c', type=click.Path(exists=True), help='Path to configuration file')
@click.option('--output-dir', '-o', type=click.Path(), help='Output directory for generated documentation')
@click.option('--apps', '-a', multiple=True, help='Specific Django apps to include (default: all)')
@click.option('--exclude-apps', multiple=True, help='Django apps to exclude')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--dry-run', is_flag=True, help='Perform analysis without generating files')
@click.option('--typescript-only', is_flag=True, help='Generate only TypeScript definitions')
@click.option('--sphinx-only', is_flag=True, help='Generate only Sphinx documentation')
@click.option('--docusaurus-only', is_flag=True, help='Generate only Docusaurus documentation')
@click.option('--format', '-f', type=click.Choice(['sphinx', 'docusaurus']), default='sphinx', help='Documentation format (default: sphinx)')
@click.option('--extend-existing/--no-extend-existing', default=True, help='Extend existing documentation setups (default: true)')
@click.option('--force-create-new', is_flag=True, help='Force creation of new documentation structure')
@click.option('--ai-provider', type=click.Choice(['openai', 'anthropic', 'local']), help='AI provider for enhanced analysis')
@click.option('--ai-model', help='AI model to use (e.g., gpt-4, claude-3)')
@click.option('--no-ai', is_flag=True, help='Disable AI-powered analysis')
@click.option('--language', type=click.Choice(['typescript', 'javascript', 'python', 'java', 'csharp', 'go', 'rust', 'swift', 'kotlin']), default='typescript', help='Primary language template (default: typescript)')
@click.option('--interface-naming', type=click.Choice(['snake_case', 'camelCase', 'PascalCase', 'kebab-case', 'SCREAMING_SNAKE', 'lowercase']), default='PascalCase', help='Primary interface naming convention (default: PascalCase)')
@click.option('--property-naming', type=click.Choice(['snake_case', 'camelCase', 'PascalCase', 'kebab-case', 'SCREAMING_SNAKE', 'lowercase']), default='camelCase', help='Primary property naming convention (default: camelCase)')
@click.option('--preserve-django-names', is_flag=True, help='Keep original Django field names without transformation')
@click.option('--single-language-only', is_flag=True, help='Generate only the primary language (disables multi-language generation)')
@click.option('--exclude-languages', multiple=True, type=click.Choice(['python', 'java', 'csharp', 'go', 'rust', 'swift', 'kotlin']), help='Languages to exclude from generation')
@click.option('--single-naming-only', is_flag=True, help='Generate only the primary naming convention (disables variants)')
@click.option('--exclude-naming', multiple=True, type=click.Choice(['snake_case', 'camelCase', 'PascalCase', 'kebab-case', 'SCREAMING_SNAKE', 'lowercase']), help='Naming conventions to exclude from generation')
@click.version_option(version='1.0.0', prog_name='easy-sdk')
def cli(
    ctx: click.Context,
    project_path: Optional[str],
    config: Optional[str],
    output_dir: Optional[str],
    apps: List[str],
    exclude_apps: List[str],
    verbose: bool,
    dry_run: bool,
    typescript_only: bool,
    sphinx_only: bool,
    docusaurus_only: bool,
    format: str,
    extend_existing: bool,
    force_create_new: bool,
    ai_provider: Optional[str],
    ai_model: Optional[str],
    no_ai: bool,
    language: str,
    interface_naming: str,
    property_naming: str,
    preserve_django_names: bool,
    single_language_only: bool,
    exclude_languages: List[str],
    single_naming_only: bool,
    exclude_naming: List[str],
) -> None:
    """
    Django API Documentation & SDK Generator
    
    Generate comprehensive API documentation and client SDKs from Django REST Framework projects
    using AI-powered analysis and structural code understanding.
    
    Examples:
        easy-sdk /path/to/django/project
        easy-sdk /path/to/project --config config.toml
        easy-sdk /path/to/project generate-sdk --language python --language typescript
        easy-sdk /path/to/project --format docusaurus
    """
    # Setup logging
    setup_logging(verbose)
    
    # If no command is specified and project_path is provided, run generate
    if ctx.invoked_subcommand is None:
        if project_path:
            ctx.invoke(generate, 
                project_path=project_path,
                config=config,
                output_dir=output_dir,
                apps=apps,
                exclude_apps=exclude_apps,
                verbose=verbose,
                dry_run=dry_run,
                typescript_only=typescript_only,
                sphinx_only=sphinx_only,
                docusaurus_only=docusaurus_only,
                format=format,
                extend_existing=extend_existing,
                force_create_new=force_create_new,
                ai_provider=ai_provider,
                ai_model=ai_model,
                no_ai=no_ai,
                language=language,
                interface_naming=interface_naming,
                property_naming=property_naming,
                preserve_django_names=preserve_django_names,
                single_language_only=single_language_only,
                exclude_languages=exclude_languages,
                single_naming_only=single_naming_only,
                exclude_naming=exclude_naming)
        else:
            console.print("❌ Please provide a Django project path or use a subcommand.", style="red")
            console.print("Run 'easy-sdk --help' for more information.")
            sys.exit(1)


@cli.command()
@click.argument('project_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--config', '-c', type=click.Path(exists=True), help='Path to configuration file')
@click.option('--output-dir', '-o', type=click.Path(), help='Output directory for generated documentation')
@click.option('--apps', '-a', multiple=True, help='Specific Django apps to include (default: all)')
@click.option('--exclude-apps', multiple=True, help='Django apps to exclude')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--dry-run', is_flag=True, help='Perform analysis without generating files')
@click.option('--typescript-only', is_flag=True, help='Generate only TypeScript definitions')
@click.option('--sphinx-only', is_flag=True, help='Generate only Sphinx documentation')
@click.option('--docusaurus-only', is_flag=True, help='Generate only Docusaurus documentation')
@click.option('--format', '-f', type=click.Choice(['sphinx', 'docusaurus']), default='sphinx', help='Documentation format (default: sphinx)')
@click.option('--extend-existing/--no-extend-existing', default=True, help='Extend existing documentation setups (default: true)')
@click.option('--force-create-new', is_flag=True, help='Force creation of new documentation structure')
@click.option('--ai-provider', type=click.Choice(['openai', 'anthropic', 'local']), help='AI provider for enhanced analysis')
@click.option('--ai-model', help='AI model to use (e.g., gpt-4, claude-3)')
@click.option('--no-ai', is_flag=True, help='Disable AI-powered analysis')
@click.option('--language', '-l', type=click.Choice(['typescript', 'javascript', 'python', 'java', 'csharp', 'go', 'rust', 'swift', 'kotlin']), default='typescript', help='Primary language template (default: typescript)')
@click.option('--interface-naming', type=click.Choice(['snake_case', 'camelCase', 'PascalCase', 'kebab-case', 'SCREAMING_SNAKE', 'lowercase']), default='PascalCase', help='Primary interface naming convention (default: PascalCase)')
@click.option('--property-naming', type=click.Choice(['snake_case', 'camelCase', 'PascalCase', 'kebab-case', 'SCREAMING_SNAKE', 'lowercase']), default='camelCase', help='Primary property naming convention (default: camelCase)')
@click.option('--preserve-django-names', is_flag=True, help='Keep original Django field names without transformation')
@click.option('--single-language-only', is_flag=True, help='Generate only the primary language (disables multi-language generation)')
@click.option('--exclude-languages', multiple=True, type=click.Choice(['python', 'java', 'csharp', 'go', 'rust', 'swift', 'kotlin']), help='Languages to exclude from generation')
@click.option('--single-naming-only', is_flag=True, help='Generate only the primary naming convention (disables variants)')
@click.option('--exclude-naming', multiple=True, type=click.Choice(['snake_case', 'camelCase', 'PascalCase', 'kebab-case', 'SCREAMING_SNAKE', 'lowercase']), help='Naming conventions to exclude from generation')
def generate(
    project_path: str,
    config: Optional[str],
    output_dir: Optional[str],
    apps: List[str],
    exclude_apps: List[str],
    verbose: bool,
    dry_run: bool,
    typescript_only: bool,
    sphinx_only: bool,
    docusaurus_only: bool,
    format: str,
    extend_existing: bool,
    force_create_new: bool,
    ai_provider: Optional[str],
    ai_model: Optional[str],
    no_ai: bool,
    language: str,
    interface_naming: str,
    property_naming: str,
    preserve_django_names: bool,
    single_language_only: bool,
    exclude_languages: List[str],
    single_naming_only: bool,
    exclude_naming: List[str],
) -> None:
    """Generate API documentation for a Django project"""
    try:
        console.print(f"🚀 Starting Django API documentation generation for: {project_path}")
        
        # Load or create configuration
        django_config = _create_config(
            project_path=project_path,
            config_file=config,
            output_dir=output_dir,
            apps=apps,
            exclude_apps=exclude_apps,
            verbose=verbose,
            dry_run=dry_run,
            format=format,
            extend_existing=extend_existing,
            force_create_new=force_create_new,
            ai_provider=ai_provider,
            ai_model=ai_model,
            no_ai=no_ai,
            language=language,
            interface_naming=interface_naming,
            property_naming=property_naming,
            preserve_django_names=preserve_django_names,
            single_language_only=single_language_only,
            exclude_languages=exclude_languages,
            single_naming_only=single_naming_only,
            exclude_naming=exclude_naming,
        )
        
        # Validate project
        generator = DjangoDocsGenerator(project_path, config=django_config)
        validation_errors = generator.validate_project()
        
        if validation_errors:
            console.print("❌ Project validation failed:", style="red")
            for error in validation_errors:
                console.print(f"  • {error}", style="red")
            sys.exit(1)
        
        # Generate documentation
        if typescript_only:
            console.print("📝 Generating TypeScript definitions only...")
            result = generator.generate_typescript_types()
        elif sphinx_only:
            console.print("📚 Generating Sphinx documentation only...")
            result = generator.generate_sphinx_docs()
        elif docusaurus_only:
            console.print("📚 Generating Docusaurus documentation only...")
            result = generator.generate_docusaurus_docs()
        else:
            doc_format = django_config.generation.documentation_format
            console.print(f"📖 Generating complete API documentation ({doc_format})...")
            result = generator.generate_all()
        
        # Display results
        result.print_summary(console)
        
        if result.success:
            console.print("✅ Documentation generation completed successfully!", style="green")
            sys.exit(0)
        else:
            console.print("❌ Documentation generation failed!", style="red")
            sys.exit(1)
    
    except KeyboardInterrupt:
        console.print("\n⚠️ Operation cancelled by user", style="yellow")
        sys.exit(1)
    except Exception as e:
        console.print(f"💥 Unexpected error: {str(e)}", style="red")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument('project_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--config', '-c', type=click.Path(exists=True), help='Path to configuration file')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def analyze(
    project_path: str,
    config: Optional[str],
    verbose: bool,
) -> None:
    """Analyze Django project structure without generating documentation"""
    try:
        console.print(f"🔍 Analyzing Django project: {project_path}")
        
        # Load configuration
        django_config = _create_config(
            project_path=project_path,
            config_file=config,
            verbose=verbose,
            dry_run=True,  # Analysis mode
        )
        
        # Create generator and validate
        generator = DjangoDocsGenerator(project_path, config=django_config)
        validation_errors = generator.validate_project()
        
        if validation_errors:
            console.print("❌ Project validation failed:", style="red")
            for error in validation_errors:
                console.print(f"  • {error}", style="red")
            return
        
        # Perform analysis
        console.print("📊 Running Django project analysis...")
        
        # Scan the project
        scan_result = generator.scanner.scan_project(Path(project_path))
        
        if not scan_result.success:
            console.print("❌ Project scanning failed:", style="red")
            for error in scan_result.errors:
                console.print(f"  • {error}", style="red")
            return
        
        # Display analysis results
        _display_analysis_results(scan_result, console)
        
    except Exception as e:
        console.print(f"💥 Analysis failed: {str(e)}", style="red")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument('output_path', type=click.Path())
@click.option('--project-name', default='My Django API', help='Project name')
@click.option('--ai-provider', type=click.Choice(['openai', 'anthropic', 'local']), default='openai', help='AI provider')
@click.option('--include-examples', is_flag=True, default=True, help='Include usage examples in config')
def init_config(
    output_path: str,
    project_name: str,
    ai_provider: str,
    include_examples: bool,
) -> None:
    """Initialize a configuration file with default settings"""
    try:
        config_path = Path(output_path)
        
        if config_path.exists():
            if not click.confirm(f"Configuration file {config_path} already exists. Overwrite?"):
                console.print("❌ Configuration file creation cancelled.", style="yellow")
                return
        
        # Create default configuration
        default_config = DjangoDocsConfig(
            project_path=Path.cwd(),
            project_name=project_name,
        )
        default_config.ai.provider = ai_provider
        default_config.generation.include_examples = include_examples
        
        # Save configuration
        default_config.save_to_file(config_path)
        
        console.print(f"✅ Configuration file created: {config_path}", style="green")
        
        if include_examples:
            console.print("\n📋 Example configuration created with common settings.")
            console.print("Edit the file to customize for your project.")
    
    except Exception as e:
        console.print(f"❌ Failed to create configuration file: {str(e)}", style="red")
        sys.exit(1)


@cli.command()
@click.argument('project_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
def validate(project_path: str) -> None:
    """Validate that a Django project is compatible"""
    try:
        console.print(f"🔍 Validating Django project: {project_path}")
        
        # Create minimal config for validation
        config = DjangoDocsConfig(project_path=Path(project_path))
        generator = DjangoDocsGenerator(project_path, config=config)
        
        validation_errors = generator.validate_project()
        
        if validation_errors:
            console.print("❌ Project validation failed:", style="red")
            for error in validation_errors:
                console.print(f"  • {error}", style="red")
            sys.exit(1)
        else:
            console.print("✅ Project validation passed!", style="green")
            console.print("The Django project is compatible with the documentation generator.")
    
    except Exception as e:
        console.print(f"❌ Validation failed: {str(e)}", style="red")
        sys.exit(1)


def _create_config(
    project_path: str,
    config_file: Optional[str] = None,
    output_dir: Optional[str] = None,
    apps: List[str] = None,
    exclude_apps: List[str] = None,
    verbose: bool = False,
    dry_run: bool = False,
    format: str = "sphinx",
    extend_existing: bool = True,
    force_create_new: bool = False,
    ai_provider: Optional[str] = None,
    ai_model: Optional[str] = None,
    no_ai: bool = False,
    language: str = "typescript",
    interface_naming: str = "PascalCase",
    property_naming: str = "camelCase",
    preserve_django_names: bool = False,
    single_language_only: bool = False,
    exclude_languages: List[str] = None,
    single_naming_only: bool = False,
    exclude_naming: List[str] = None,
) -> DjangoDocsConfig:
    """Create configuration from CLI options"""
    
    # Load from file if provided
    if config_file:
        config = DjangoDocsConfig.from_file(config_file)
        # Override project path
        config.project_path = Path(project_path)
    else:
        # Create default config
        config = DjangoDocsConfig(project_path=Path(project_path))
    
    # Override with CLI options
    if output_dir:
        config.output.base_output_dir = Path(output_dir)
        config.output.sphinx_output_dir = Path(output_dir) / "docs"
        config.output.typescript_output_dir = Path(output_dir) / "types"
    
    if apps:
        config.include_apps = list(apps)
    
    if exclude_apps:
        config.exclude_apps.extend(exclude_apps)
    
    if verbose:
        config.verbose = True
    
    if dry_run:
        config.dry_run = True
    
    # Set documentation format
    config.generation.documentation_format = format
    
    # Set extension behavior
    config.generation.extend_existing_docs = extend_existing
    config.generation.force_create_new = force_create_new
    
    if ai_provider:
        config.ai.provider = ai_provider
    
    if ai_model:
        config.ai.model = ai_model
    
    if no_ai:
        config.ai.provider = 'local'  # Disable external AI
    
    # Set language template options with comprehensive defaults
    config.generation.language_template = language
    config.generation.interface_naming_convention = interface_naming
    config.generation.property_naming_convention = property_naming
    config.generation.preserve_django_field_names = preserve_django_names
    
    # Multi-language generation (default enabled, but can be disabled)
    config.generation.generate_multiple_languages = not single_language_only
    
    # Build additional languages list (default: python, java, but can exclude some)
    all_languages = ["python", "java", "csharp", "go", "rust", "swift", "kotlin"]
    if single_language_only:
        config.generation.additional_languages = []
    else:
        excluded = set(exclude_languages) if exclude_languages else set()
        config.generation.additional_languages = [lang for lang in all_languages if lang not in excluded]
    
    # Multi-naming generation (default enabled, but can be disabled)  
    config.generation.generate_all_naming_variants = not single_naming_only
    
    # Build naming variants list (default: camelCase, snake_case, PascalCase, but can exclude some)
    all_naming = ["camelCase", "snake_case", "PascalCase", "kebab-case", "SCREAMING_SNAKE", "lowercase"]
    if single_naming_only:
        config.generation.naming_variants = [interface_naming, property_naming]
    else:
        excluded_naming = set(exclude_naming) if exclude_naming else set()
        config.generation.naming_variants = [naming for naming in all_naming if naming not in excluded_naming]
    
    return config


def _display_analysis_results(scan_result, console: Console) -> None:
    """Display analysis results in a formatted way"""
    from rich.table import Table
    from rich.panel import Panel
    
    # Project overview
    project_info = scan_result.project_info
    console.print(Panel(
        f"[bold]Project:[/bold] {project_info.get('name', 'Unknown')}\n"
        f"[bold]Path:[/bold] {project_info.get('path', 'Unknown')}\n"
        f"[bold]Apps Found:[/bold] {len(scan_result.discovered_apps)}",
        title="Django Project Overview"
    ))
    
    # Apps table
    if scan_result.discovered_apps:
        table = Table(title="Discovered Django Apps")
        table.add_column("App Name", style="cyan", no_wrap=True)
        table.add_column("Serializers", justify="center", style="green")
        table.add_column("Views", justify="center", style="blue")
        table.add_column("Models", justify="center", style="magenta")
        table.add_column("URLs", justify="center", style="yellow")
        table.add_column("DRF", justify="center", style="red")
        
        for app_name, app_info in scan_result.discovered_apps.items():
            serializer_count = len(app_info.get('serializers', []))
            view_count = len(app_info.get('views', []))
            model_count = len(app_info.get('models', []))
            url_count = len(app_info.get('urls', []))
            has_drf = "✓" if app_info.get('has_rest_framework', False) else "✗"
            
            table.add_row(
                app_name,
                str(serializer_count) if serializer_count else "-",
                str(view_count) if view_count else "-",
                str(model_count) if model_count else "-",
                str(url_count) if url_count else "-",
                has_drf
            )
        
        console.print(table)
    
    # Warnings
    if scan_result.warnings:
        console.print("\n⚠️  Warnings:", style="yellow")
        for warning in scan_result.warnings:
            console.print(f"  • {warning}", style="yellow")


@cli.command()
@click.option('--language', '-l', multiple=True, type=click.Choice(['python', 'typescript', 'javascript', 'ts', 'js']), help='SDK language(s) to generate')
@click.option('--output-dir', '-o', type=click.Path(), help='Output directory for generated SDKs')
@click.option('--library-name', help='Custom library name for generated SDKs')
@click.option('--config', '-c', type=click.Path(exists=True), help='Path to configuration file')
@click.option('--apps', '-a', multiple=True, help='Specific Django apps to include (default: all)')
@click.option('--exclude-apps', multiple=True, help='Django apps to exclude')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--preview-only', is_flag=True, help='Preview SDK structure without generating files')
@click.option('--ai-provider', type=click.Choice(['openai', 'anthropic', 'local']), help='AI provider for enhanced analysis')
@click.option('--ai-model', help='AI model to use (e.g., gpt-4, claude-3)')
@click.option('--no-ai', is_flag=True, help='Disable AI-powered analysis')
@click.pass_context
def generate_sdk(
    ctx: click.Context,
    language: List[str],
    output_dir: Optional[str],
    library_name: Optional[str],
    config: Optional[str],
    apps: List[str],
    exclude_apps: List[str],
    verbose: bool,
    preview_only: bool,
    ai_provider: Optional[str],
    ai_model: Optional[str],
    no_ai: bool,
) -> None:
    """Generate client SDKs for Django REST API"""
    try:
        # Get project path from parent context
        project_path = ctx.parent.params.get('project_path')
        
        if not project_path:
            console.print("❌ Please provide a Django project path.", style="red")
            sys.exit(1)
        
        setup_logging(verbose)
        console.print(f"🚀 Starting SDK generation for: {project_path}")
        
        # Default to Python and TypeScript if no languages specified
        if not language:
            language = ['python', 'typescript']
            console.print(f"📦 No languages specified, generating: {', '.join(language)}")
        
        # Load configuration
        django_config = _create_config(
            project_path=project_path,
            config_file=config,
            output_dir=output_dir,
            apps=apps,
            exclude_apps=exclude_apps,
            verbose=verbose,
            ai_provider=ai_provider,
            ai_model=ai_model,
            no_ai=no_ai,
        )
        
        # Validate project
        generator = DjangoDocsGenerator(project_path, config=django_config)
        validation_errors = generator.validate_project()
        
        if validation_errors:
            console.print("❌ Project validation failed:", style="red")
            for error in validation_errors:
                console.print(f"  • {error}", style="red")
            sys.exit(1)
        
        # Analyze Django project
        console.print("📊 Analyzing Django project...")
        scan_result = generator.scanner.scan_project(Path(project_path))
        
        if not scan_result.success:
            console.print("❌ Project analysis failed:", style="red")
            for error in scan_result.errors:
                console.print(f"  • {error}", style="red")
            sys.exit(1)
        
        # Create SDK manager
        sdk_manager = SDKManager(django_config)
        
        # Validate analysis for SDK generation
        if not sdk_manager.validate_analysis_result(scan_result.discovered_apps):
            console.print("❌ Analysis result not suitable for SDK generation", style="red")
            sys.exit(1)
        
        # Preview mode
        if preview_only:
            console.print("\n🔍 SDK Structure Previews:")
            for lang in language:
                try:
                    preview = sdk_manager.preview_sdk_structure(
                        scan_result.discovered_apps,
                        lang,
                        library_name
                    )
                    _display_sdk_preview(preview, console)
                except Exception as e:
                    console.print(f"❌ Preview failed for {lang}: {e}", style="red")
            return
        
        # Generate SDKs
        console.print(f"🔧 Generating SDKs for {len(language)} language(s)...")
        
        if len(language) == 1:
            # Single language generation
            lang = language[0]
            generated_files = sdk_manager.generate_sdk(
                analysis_result=scan_result.discovered_apps,
                language=lang,
                library_name=library_name
            )
            
            console.print(f"✅ {lang.upper()} SDK generated: {len(generated_files)} files")
            _display_generated_files(generated_files, console)
            
        else:
            # Multiple language generation
            results = sdk_manager.generate_multiple_sdks(
                analysis_result=scan_result.discovered_apps,
                languages=language,
                library_name=library_name
            )
            
            total_files = 0
            for lang, files in results.items():
                if files:
                    console.print(f"✅ {lang.upper()} SDK: {len(files)} files")
                    total_files += len(files)
                else:
                    console.print(f"❌ {lang.upper()} SDK: Generation failed", style="red")
            
            console.print(f"\n🎉 SDK generation completed: {total_files} total files")
        
        console.print("✅ SDK generation completed successfully!", style="green")
    
    except KeyboardInterrupt:
        console.print("\n⚠️ Operation cancelled by user", style="yellow")
        sys.exit(1)
    except Exception as e:
        console.print(f"💥 SDK generation failed: {str(e)}", style="red")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
def list_sdk_languages() -> None:
    """List supported SDK programming languages"""
    try:
        # Create minimal config
        config = DjangoDocsConfig(project_path=Path.cwd())
        sdk_manager = SDKManager(config)
        
        languages = sdk_manager.list_supported_languages()
        
        console.print("🔧 Supported SDK Languages:", style="bold")
        for lang in languages:
            try:
                info = sdk_manager.get_language_info(lang)
                console.print(f"\n• {lang.upper()}")
                console.print(f"  Generator: {info['generator']}")
                if info['description']:
                    console.print(f"  Description: {info['description']}")
                if info['features']:
                    console.print(f"  Features: {', '.join(info['features'][:3])}...")
            except Exception:
                console.print(f"\n• {lang.upper()}")
        
        console.print(f"\nTotal: {len(languages)} languages supported")
        
    except Exception as e:
        console.print(f"❌ Failed to list languages: {str(e)}", style="red")
        sys.exit(1)


def _display_sdk_preview(preview: Dict[str, Any], console: Console) -> None:
    """Display SDK structure preview"""
    from rich.panel import Panel
    from rich.table import Table
    
    # Main info panel
    console.print(Panel(
        f"[bold]Language:[/bold] {preview['language'].upper()}\n"
        f"[bold]Library:[/bold] {preview['library_name']}\n"
        f"[bold]Package:[/bold] {preview.get('package_name', 'N/A')}\n"
        f"[bold]Apps:[/bold] {preview['total_apps']}\n"
        f"[bold]Endpoints:[/bold] {preview['total_endpoints']}\n"
        f"[bold]Est. Files:[/bold] {preview['estimated_files']}\n"
        f"[bold]Auth:[/bold] {preview.get('auth_strategy', 'token')}",
        title=f"{preview['language'].upper()} SDK Preview"
    ))
    
    # Apps table
    if preview['apps']:
        table = Table(title="App Structure")
        table.add_column("App", style="cyan")
        table.add_column("Endpoints", justify="center", style="green")
        table.add_column("Models", justify="center", style="blue")
        table.add_column("Operations", style="magenta")
        
        for app in preview['apps']:
            table.add_row(
                app['name'],
                str(app['endpoints']),
                str(app['models']),
                ', '.join(app['operations'][:2]) + ('...' if len(app['operations']) > 2 else '')
            )
        
        console.print(table)


def _display_generated_files(files: List[Path], console: Console, limit: int = 10) -> None:
    """Display list of generated files"""
    console.print(f"\n📁 Generated Files:")
    
    for i, file_path in enumerate(files[:limit]):
        relative_path = file_path.relative_to(file_path.parts[0])
        console.print(f"  • {relative_path}")
    
    if len(files) > limit:
        console.print(f"  ... and {len(files) - limit} more files")


def main() -> None:
    """Main entry point for the CLI"""
    cli()


if __name__ == '__main__':
    main()