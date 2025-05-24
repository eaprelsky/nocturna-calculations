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
    author="Yegor Aprelsky",
    author_email="yegor.aprelsky@gmail.com",
    description="Astrological calculations library based on Swiss Ephemeris",
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
        "Topic :: Scientific/Engineering :: Astronomy",
    ],
    python_requires=">=3.8",
) 