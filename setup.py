from setuptools import setup, find_packages

setup(
    name="nocturna-calculations",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pyswisseph>=2.10.0",
        "numpy>=1.21.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "api": [
            "fastapi>=0.100.0",
            "uvicorn>=0.23.0",
            "sqlalchemy>=2.0.0",
            "alembic>=1.11.0",
            "redis>=4.6.0",
            "python-jose[cryptography]>=3.3.0",
            "passlib[bcrypt]>=1.7.4",
            "python-multipart>=0.0.6",
            "httpx>=0.24.0",
            "prometheus-client>=0.17.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    author="Yegor Aprelsky",
    author_email="yegor.aprelsky@gmail.com",
    description="Astrological calculations library and REST API service based on Swiss Ephemeris",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/eaprelsky/nocturna-calculations",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "nocturna-api=nocturna_calculations.api.__main__:main",
        ],
    },
) 