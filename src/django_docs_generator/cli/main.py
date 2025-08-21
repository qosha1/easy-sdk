"""
Main CLI entry point for Django API Documentation Generator
"""

import logging
import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.logging import RichHandler

from ..core.config import DjangoDocsConfig
from ..core.generator import DjangoDocsGenerator


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
@click.option('--ai-provider', type=click.Choice(['openai', 'anthropic', 'local']), help='AI provider for enhanced analysis')
@click.option('--ai-model', help='AI model to use (e.g., gpt-4, claude-3)')
@click.option('--no-ai', is_flag=True, help='Disable AI-powered analysis')
@click.version_option(version='0.1.0', prog_name='django-docs-generator')
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
    ai_provider: Optional[str],
    ai_model: Optional[str],
    no_ai: bool,
) -> None:
    """
    Django API Documentation Generator
    
    Generate comprehensive API documentation from Django REST Framework projects
    using AI-powered analysis and structural code understanding.
    
    Examples:
        django-docs-generator /path/to/django/project
        django-docs-generator /path/to/project --config config.toml
        django-docs-generator /path/to/project --apps api users --typescript-only
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
                ai_provider=ai_provider,
                ai_model=ai_model,
                no_ai=no_ai)
        else:
            console.print("❌ Please provide a Django project path or use a subcommand.", style="red")
            console.print("Run 'django-docs-generator --help' for more information.")
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
@click.option('--ai-provider', type=click.Choice(['openai', 'anthropic', 'local']), help='AI provider for enhanced analysis')
@click.option('--ai-model', help='AI model to use (e.g., gpt-4, claude-3)')
@click.option('--no-ai', is_flag=True, help='Disable AI-powered analysis')
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
    ai_provider: Optional[str],
    ai_model: Optional[str],
    no_ai: bool,
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
        
        # Generate documentation
        if typescript_only:
            console.print("📝 Generating TypeScript definitions only...")
            result = generator.generate_typescript_types()
        elif sphinx_only:
            console.print("📚 Generating Sphinx documentation only...")
            result = generator.generate_sphinx_docs()
        else:
            console.print("📖 Generating complete API documentation...")
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
    ai_provider: Optional[str] = None,
    ai_model: Optional[str] = None,
    no_ai: bool = False,
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
    
    if ai_provider:
        config.ai.provider = ai_provider
    
    if ai_model:
        config.ai.model = ai_model
    
    if no_ai:
        config.ai.provider = 'local'  # Disable external AI
    
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


def main() -> None:
    """Main entry point for the CLI"""
    cli()


if __name__ == '__main__':
    main()