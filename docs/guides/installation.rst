Installation Guide
================

This guide will help you install Nocturna Calculations and its dependencies.

System Requirements
-----------------

* Python 3.8 or higher
* pip (Python package installer)
* Git (optional, for development)

Basic Installation
----------------

The simplest way to install Nocturna Calculations is using pip:

.. code-block:: bash

   pip install nocturna-calculations

This will install the package and all its required dependencies.

Development Installation
----------------------

If you want to contribute to the project or need the latest development version:

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/eaprelsky/nocturna-calculations.git
      cd nocturna-calculations

2. Create and activate a virtual environment:

   .. code-block:: bash

      # On Windows
      python -m venv venv
      venv\Scripts\activate

      # On Unix or MacOS
      python -m venv venv
      source venv/bin/activate

3. Install development dependencies:

   .. code-block:: bash

      pip install -e ".[dev]"

Dependencies
-----------

Nocturna Calculations requires the following main dependencies:

* pyswisseph (>=2.10.0) - Swiss Ephemeris Python bindings
* numpy (>=1.21.0) - Numerical computing
* pydantic (>=2.0.0) - Data validation

Optional dependencies for development:

* pytest - Testing framework
* black - Code formatting
* flake8 - Code linting
* mypy - Type checking

Verifying Installation
--------------------

To verify that the installation was successful, you can run:

.. code-block:: python

   from nocturna_calculations import ChartCalculator
   from nocturna_calculations.adapters import SwissEphAdapter

   # Create calculator instance
   calculator = ChartCalculator(adapter=SwissEphAdapter())

   # If no error occurs, the installation was successful

Troubleshooting
-------------

Common installation issues and their solutions:

1. **Swiss Ephemeris Files Missing**
   
   If you encounter errors about missing Swiss Ephemeris files, ensure that the files are properly installed in your system's ephemeris directory.

2. **Version Conflicts**
   
   If you encounter dependency conflicts, try creating a fresh virtual environment and installing the package again.

3. **Permission Issues**
   
   If you encounter permission errors during installation, try using:

   .. code-block:: bash

      pip install --user nocturna-calculations

For more detailed troubleshooting, see the :doc:`troubleshooting` guide. 