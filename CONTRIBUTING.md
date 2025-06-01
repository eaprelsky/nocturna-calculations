# Contributing to Nocturna Calculations

We love your input! We want to make contributing to Nocturna Calculations as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Project Structure

Nocturna Calculations is both a Python library and a REST API service. Contributions can be made to either component:

- **Library**: Core astrological calculation functionality
- **API**: REST endpoints, authentication, and service features

## We Develop with GitHub
We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## We Use [Github Flow](https://guides.github.com/introduction/flow/index.html)
Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Development Setup

### Library Development
```bash
# Clone the repository
git clone https://github.com/eaprelsky/nocturna-calculations.git
cd nocturna-calculations

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run library tests
pytest tests/library/
```

### API Development
```bash
# Install API dependencies
pip install -e ".[api,dev]"

# Run API tests
pytest tests/api/

# Start development server
uvicorn nocturna_calculations.api:app --reload
```

## Testing Guidelines

### Library Tests
- Write unit tests for all calculation methods
- Include edge cases and error conditions
- Validate accuracy against known astronomical data
- Test file location: `tests/library/`

### API Tests
- Test all endpoints with valid and invalid data
- Include authentication and authorization tests
- Test rate limiting and error responses
- Test file location: `tests/api/`

## Code Style

### Python Code
* Use [black](https://github.com/psf/black) for code formatting
* Use [flake8](https://flake8.pycqa.org/) for linting
* Use [mypy](https://mypy.readthedocs.io/) for type checking
* Follow PEP 8 guidelines
* Add type hints to all function signatures

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Documentation

### Library Documentation
- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Include usage examples
- Update `docs/api-reference.md` for new features

### API Documentation
- Update OpenAPI specs for new endpoints
- Document request/response schemas
- Include authentication requirements
- Update `docs/api/reference.md` for new features

## Any contributions you make will be under the MIT Software License
In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using GitHub's [issue tracker](https://github.com/eaprelsky/nocturna-calculations/issues)
We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/eaprelsky/nocturna-calculations/issues/new); it's that easy!

## Bug Reports

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
  - Specify if it's a library or API issue
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)
- Environment details (Python version, OS, etc.)

## Feature Requests

When proposing new features:

- Explain the use case
- Specify if it's for the library, API, or both
- Provide examples of how it would work
- Consider backward compatibility

## Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update the documentation with any new functionality
3. Add tests for new features
4. Ensure all tests pass: `pytest`
5. Ensure code is formatted: `black .`
6. Ensure code passes linting: `flake8`
7. Update the version numbers following [SemVer](http://semver.org/)

## Release Process

Releases are managed by maintainers and include:

1. Library release to PyPI
2. API Docker image release
3. Documentation updates
4. Changelog updates

## License
By contributing, you agree that your contributions will be licensed under its MIT License. 