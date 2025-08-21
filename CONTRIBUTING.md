# Contributing to Django API Documentation Generator

Thank you for your interest in contributing to the Django API Documentation Generator! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Development Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/easy-sdk/django-api-docs-generator.git
   cd django-api-docs-generator
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks** (recommended)
   ```bash
   pre-commit install
   ```

5. **Verify installation**
   ```bash
   pytest
   easy-sdk --version
   ```

## 📋 Development Workflow

### Code Style and Quality

We use several tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking
- **pytest** for testing

Run all quality checks:
```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type check
mypy src/

# Run tests
pytest --cov=src/easy_sdk
```

### Testing

We maintain comprehensive test coverage:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src/easy_sdk --cov-report=html

# Run specific test file
pytest tests/unit/test_config.py

# Run tests with verbose output
pytest -v

# Run only integration tests
pytest tests/integration/
```

### Creating New Features

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write tests first** (TDD approach recommended)
   - Add unit tests in `tests/unit/`
   - Add integration tests in `tests/integration/` if needed
   - Ensure tests fail before implementing the feature

3. **Implement the feature**
   - Follow existing code patterns and architecture
   - Add type hints for all new functions and classes
   - Include comprehensive docstrings

4. **Update documentation**
   - Update README.md if adding user-facing features
   - Add/update docstrings
   - Update configuration examples if needed

5. **Test your changes**
   ```bash
   pytest
   # Test CLI functionality
   easy-sdk tests/fixtures/sample_project --dry-run
   ```

## 🏗️ Architecture Guidelines

### Code Organization

```
src/easy_sdk/
├── core/              # Core functionality
│   ├── config.py      # Configuration management
│   └── generator.py   # Main generator class
├── analyzers/         # Code analysis components
│   ├── django_scanner.py      # Project scanning
│   ├── serializer_analyzer.py # Serializer analysis
│   └── view_analyzer.py       # View analysis
├── ai/                # AI integration
│   ├── engine.py      # AI analysis engine
│   └── prompts.py     # AI prompt templates
├── generators/        # Documentation generators
│   ├── sphinx_generator.py    # Sphinx documentation
│   └── typescript_generator.py # TypeScript types
└── cli/               # Command-line interface
    └── main.py        # CLI implementation
```

### Design Principles

1. **Separation of Concerns**: Each module has a single responsibility
2. **Configuration-Driven**: All behavior should be configurable
3. **Error Resilience**: Graceful handling of malformed Django code
4. **Extensibility**: Easy to add new AI providers, generators, etc.
5. **Type Safety**: Comprehensive type hints throughout

### Adding New Components

#### New AI Provider

1. Extend `AIAnalysisEngine` in `src/easy_sdk/ai/engine.py`
2. Add provider-specific client initialization
3. Implement the API call method following existing patterns
4. Add configuration options to `AIConfig`
5. Update CLI options and documentation

#### New Documentation Generator

1. Create new generator class in `src/easy_sdk/generators/`
2. Follow the interface pattern established by existing generators
3. Add generator to main `DjangoDocsGenerator` class
4. Add CLI options for the new generator
5. Include comprehensive tests

#### New Analyzer

1. Create analyzer class in `src/easy_sdk/analyzers/`
2. Follow existing analyzer patterns for data structures
3. Integrate with the main scanning workflow
4. Add configuration options if needed
5. Include thorough testing

## 🧪 Testing Guidelines

### Test Structure

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test complete workflows
- **Fixtures**: Reusable test data in `tests/conftest.py`

### Writing Good Tests

```python
class TestYourFeature:
    """Test your feature functionality"""
    
    def test_basic_functionality(self, test_config):
        """Test basic feature operation"""
        # Arrange
        feature = YourFeature(test_config)
        input_data = {"test": "data"}
        
        # Act
        result = feature.process(input_data)
        
        # Assert
        assert result.success is True
        assert result.data["test"] == "data"
    
    def test_error_handling(self, test_config):
        """Test error conditions"""
        feature = YourFeature(test_config)
        
        with pytest.raises(ValueError, match="Invalid input"):
            feature.process(None)
```

### Test Coverage

Maintain high test coverage:
- Aim for >90% line coverage
- Test both success and error paths
- Include edge cases and boundary conditions
- Mock external dependencies (AI APIs, file system operations)

## 📝 Documentation Guidelines

### Code Documentation

```python
def analyze_serializer(self, serializer_path: Path) -> SerializerInfo:
    """
    Analyze a Django REST framework serializer file.
    
    Args:
        serializer_path: Path to the serializer Python file
        
    Returns:
        SerializerInfo object containing analysis results
        
    Raises:
        FileNotFoundError: If serializer file doesn't exist
        SyntaxError: If serializer file has invalid Python syntax
        
    Example:
        >>> analyzer = SerializerAnalyzer(config)
        >>> info = analyzer.analyze_serializer(Path("api/serializers.py"))
        >>> print(f"Found {len(info.fields)} fields")
    """
```

### Configuration Documentation

When adding new configuration options:

1. Add to the appropriate Pydantic model
2. Include validation and defaults
3. Document in docstrings and README
4. Add to example configuration files

## 🐛 Bug Reports and Issues

### Reporting Bugs

When reporting bugs, please include:

1. **Environment information**:
   ```
   - Python version
   - Django version
   - DRF version
   - Operating system
   ```

2. **Reproduction steps**:
   - Minimal code example
   - Command line used
   - Expected vs actual behavior

3. **Additional context**:
   - Error messages and stack traces
   - Configuration files
   - Sample Django project structure (if relevant)

### Issue Templates

Use the provided issue templates for:
- 🐛 Bug reports
- ✨ Feature requests
- 📚 Documentation improvements
- ❓ Questions and support

## 🔄 Pull Request Process

### Before Submitting

1. **Update documentation**
2. **Add/update tests**
3. **Run all quality checks**
4. **Test manually with sample Django projects**
5. **Update changelog if significant**

### PR Checklist

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Type hints are included
- [ ] Changelog is updated (if needed)
- [ ] PR description explains the changes

### Review Process

1. **Automated checks**: CI runs tests and quality checks
2. **Code review**: Maintainers review for quality and design
3. **Testing**: Manual testing with various Django projects
4. **Approval**: At least one maintainer approval required
5. **Merge**: Squash and merge to main branch

## 🎯 Areas for Contribution

### High-Impact Areas

1. **AI Provider Support**
   - Add support for local/offline models
   - Implement caching for AI responses
   - Add model-specific optimizations

2. **Django Feature Support**
   - Generic foreign keys
   - Custom field types
   - Advanced serializer methods
   - Websocket endpoints

3. **Documentation Generators**
   - OpenAPI/Swagger spec generation
   - Postman collection export
   - PDF documentation export
   - Interactive API explorer

4. **Performance Optimization**
   - Parallel processing for large projects
   - Incremental analysis updates
   - Memory usage optimization

### Good First Issues

Look for issues labeled `good-first-issue`:
- Documentation improvements
- Test coverage increases
- Small feature additions
- Bug fixes with clear reproduction steps

## 📞 Getting Help

- **Discussions**: Use GitHub Discussions for questions
- **Discord**: Join our community Discord server
- **Email**: Contact maintainers directly for sensitive issues

## 🏆 Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes for significant contributions
- Annual contributor appreciation posts

## 📜 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). Please read and follow these guidelines in all interactions.

---

Thank you for contributing to Django API Documentation Generator! 🎉