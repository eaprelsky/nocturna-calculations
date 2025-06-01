from setuptools import setup, find_packages

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Core dependencies - minimal set for library functionality
CORE_DEPS = [
    "pyswisseph>=2.10.0",
    "numpy>=1.21.0",
    "pydantic>=2.0.0",
    "pytz>=2023.3",
]

# API server dependencies
API_DEPS = [
    "fastapi>=0.100.0",
    "uvicorn>=0.23.0",
    "python-multipart>=0.0.6",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "bcrypt>=4.0.0",
    "email-validator>=2.0.0",
    "pydantic-settings>=2.0.0",
    "sqlalchemy>=2.0.0",
    "alembic>=1.11.0",
    "psycopg2-binary>=2.9.0",
    "redis>=4.6.0",
    "prometheus-client>=0.17.0",
    "httpx>=0.24.0",
    "websockets>=11.0.0",
    "python-dotenv>=1.0.0",
    "tenacity>=8.2.0",
    "structlog>=23.1.0",
]

# Development dependencies
DEV_DEPS = [
    "black>=23.7.0",
    "flake8>=6.0.0",
    "mypy>=1.4.1",
    "isort>=5.12.0",
    "pre-commit>=3.3.3",
    "ipython>=8.14.0",
    "jupyter>=1.0.0",
    "jupyterlab>=4.0.0",
    "notebook>=7.0.0",
]

# Testing dependencies
TEST_DEPS = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.21.0",
    "pytest-xdist>=3.3.1",
    "httpx>=0.24.1",
    "coverage>=7.3.0",
    "pytest-benchmark>=4.0.0",
    "pytest-regressions>=2.5.0",
    "pytest-timeout>=2.2.0",
    "pytest-datadir>=1.4.1",
    "pytest-mock>=3.12.0",
    "gevent>=23.9.1",
    "PyJWT>=2.8.0",
    "bandit>=1.7.5",
    "safety>=2.3.5",
]

# Performance analysis dependencies
PERF_DEPS = [
    "memory-profiler>=0.61.0",
    "line-profiler>=4.1.0",
    "py-spy>=0.3.14",
]

setup(
    name="nocturna-calculations",
    version="1.0.0",
    packages=find_packages(),
    install_requires=CORE_DEPS,
    extras_require={
        "api": API_DEPS,
        "dev": DEV_DEPS + TEST_DEPS + PERF_DEPS,
        "test": TEST_DEPS,
        "perf": PERF_DEPS,
        "all": API_DEPS + DEV_DEPS + TEST_DEPS + PERF_DEPS,
    },
    author="Yegor Aprelsky",
    author_email="yegor.aprelsky@gmail.com",
    description="Astrological calculations library and REST API service based on Swiss Ephemeris",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eaprelsky/nocturna-calculations",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "nocturna-api=nocturna_calculations.api.__main__:main",
            "nocturna-migrate=nocturna_calculations.api.migrations:main",
        ],
    },
) 