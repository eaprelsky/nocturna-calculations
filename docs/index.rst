Welcome to Nocturna Calculations documentation!
============================================

Nocturna Calculations is a Python library for astrological calculations based on Swiss Ephemeris. This library provides a comprehensive set of tools for calculating various astrological elements including planetary positions, house systems, aspects, and more.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   README
   guides/index
   api-reference
   calculation-methods
   rectification
   architecture

Features
--------

* Natal chart calculations
* Planetary positions and movements
* House system calculations (Placidus, Koch, etc.)
* Aspect calculations
* Primary and secondary progressions
* Solar and lunar returns
* Eclipse calculations

Installation
-----------

You can install Nocturna Calculations using pip:

.. code-block:: bash

   pip install nocturna-calculations

Quick Start
----------

.. code-block:: python

   from nocturna_calculations import ChartCalculator
   from nocturna_calculations.adapters import SwissEphAdapter

   # Create calculator instance
   calculator = ChartCalculator(adapter=SwissEphAdapter())

   # Calculate natal chart
   chart = calculator.calculate_natal_chart(
       date="2024-03-20",
       time="12:00:00",
       latitude=55.7558,
       longitude=37.6173
   )

   # Get planetary positions
   planets = chart.get_planetary_positions()

   # Calculate aspects
   aspects = chart.calculate_aspects()

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 