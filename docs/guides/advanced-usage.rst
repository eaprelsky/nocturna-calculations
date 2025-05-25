Advanced Usage Guide
=================

This guide covers advanced features and techniques for using Nocturna Calculations.

Custom Adapters
-------------

You can create custom adapters for different ephemeris sources:

.. code-block:: python

   from nocturna_calculations.adapters import BaseEphemerisAdapter

   class CustomEphemerisAdapter(BaseEphemerisAdapter):
       def get_planet_position(self, planet: str, julian_day: float) -> dict:
           # Implement custom position calculation
           return {
               "longitude": calculated_longitude,
               "latitude": calculated_latitude,
               "distance": calculated_distance
           }

   # Use custom adapter
   calculator = ChartCalculator(adapter=CustomEphemerisAdapter())

Advanced Chart Calculations
-------------------------

Complex chart calculations with multiple systems:

.. code-block:: python

   # Calculate chart with multiple house systems
   chart = calculator.calculate_natal_chart(
       date="2024-03-20",
       time="12:00:00",
       latitude=55.7558,
       longitude=37.6173,
       house_systems=["Placidus", "Koch", "Whole Sign"]
   )

   # Get houses for specific system
   placidus_houses = chart.get_houses("Placidus")
   koch_houses = chart.get_houses("Koch")

Advanced Progressions
------------------

Complex progression calculations:

.. code-block:: python

   # Calculate multiple progression types
   progressed_chart = calculator.calculate_progressions(
       chart=chart,
       days=365,
       progression_types=["primary", "secondary", "tertiary"]
   )

   # Get specific progression
   primary_progressed = progressed_chart.get_progression("primary")
   secondary_progressed = progressed_chart.get_progression("secondary")

Eclipse Calculations
-----------------

Calculate solar and lunar eclipses:

.. code-block:: python

   # Find next solar eclipse
   next_solar_eclipse = calculator.find_next_solar_eclipse(
       start_date="2024-03-20",
       location={
           "latitude": 55.7558,
           "longitude": 37.6173
       }
   )

   # Calculate eclipse details
   eclipse_details = calculator.calculate_eclipse_details(
       eclipse=next_solar_eclipse,
       location={
           "latitude": 55.7558,
           "longitude": 37.6173
       }
   )

Advanced Aspect Calculations
-------------------------

Complex aspect calculations with custom orbs and aspects:

.. code-block:: python

   # Define custom aspects
   custom_aspects = {
       "conjunction": {"angle": 0, "orb": 10},
       "sextile": {"angle": 60, "orb": 6},
       "square": {"angle": 90, "orb": 8},
       "trine": {"angle": 120, "orb": 8},
       "opposition": {"angle": 180, "orb": 10}
   }

   # Calculate aspects with custom settings
   aspects = chart.calculate_aspects(
       aspects=custom_aspects,
       planets=["Sun", "Moon", "Mercury", "Venus", "Mars"],
       apply_harmonics=True
   )

Harmonics and Midpoints
---------------------

Calculate harmonics and midpoints:

.. code-block:: python

   # Calculate harmonic positions
   harmonic_chart = calculator.calculate_harmonics(
       chart=chart,
       harmonic=5  # 5th harmonic
   )

   # Calculate midpoints
   midpoints = calculator.calculate_midpoints(
       chart=chart,
       planets=["Sun", "Moon", "Mercury"]
   )

Advanced Returns
--------------

Complex return calculations:

.. code-block:: python

   # Calculate multiple returns
   returns = calculator.calculate_returns(
       chart=chart,
       year=2024,
       return_types=["solar", "lunar", "mercury", "venus"]
   )

   # Get specific return
   solar_return = returns.get_return("solar")
   mercury_return = returns.get_return("mercury")

Custom Calculations
----------------

Create custom calculation methods:

.. code-block:: python

   from nocturna_calculations.calculations import BaseCalculation

   class CustomCalculation(BaseCalculation):
       def calculate(self, chart, **kwargs):
           # Implement custom calculation
           return result

   # Use custom calculation
   result = calculator.calculate(
       calculation=CustomCalculation(),
       chart=chart,
       **custom_params
   )

Performance Optimization
---------------------

Tips for optimizing performance:

1. Use batch calculations when possible:

   .. code-block:: python

      # Batch calculate multiple charts
      charts = calculator.calculate_natal_charts([
          {"date": "2024-03-20", "time": "12:00:00", "lat": 55.7558, "lon": 37.6173},
          {"date": "2024-03-21", "time": "12:00:00", "lat": 55.7558, "lon": 37.6173}
      ])

2. Cache frequently used calculations:

   .. code-block:: python

      # Enable caching
      calculator.enable_caching()
      
      # Use cached results
      positions = calculator.get_cached_positions(planet="Sun", date="2024-03-20")

3. Use parallel processing for multiple calculations:

   .. code-block:: python

      # Enable parallel processing
      calculator.enable_parallel_processing()
      
      # Calculate multiple aspects in parallel
      aspects = calculator.calculate_aspects(parallel=True)

For more detailed information about specific features, refer to the :doc:`../api-reference`. 