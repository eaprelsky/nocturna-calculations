Best Practices Guide
=================

This guide provides recommendations for using Nocturna Calculations effectively and efficiently.

Code Organization
--------------

1. **Use Type Hints**
   
   Always use type hints for better code maintainability and IDE support:

   .. code-block:: python

      from typing import List, Dict, Optional
      from nocturna_calculations import ChartCalculator, Chart

      def calculate_multiple_charts(
          dates: List[str],
          location: Dict[str, float]
      ) -> List[Chart]:
          calculator = ChartCalculator()
          return [
              calculator.calculate_natal_chart(
                  date=date,
                  latitude=location["latitude"],
                  longitude=location["longitude"]
              )
              for date in dates
          ]

2. **Error Handling**
   
   Implement proper error handling:

   .. code-block:: python

      from nocturna_calculations.exceptions import CalculationError

      try:
          chart = calculator.calculate_natal_chart(
              date="2024-03-20",
              time="12:00:00",
              latitude=55.7558,
              longitude=37.6173
          )
      except CalculationError as e:
          logger.error(f"Failed to calculate chart: {e}")
          # Handle error appropriately

Performance Optimization
--------------------

1. **Use Caching**
   
   Enable caching for frequently used calculations:

   .. code-block:: python

      # Enable caching at the start of your application
      calculator.enable_caching()

      # Use cached results
      positions = calculator.get_cached_positions(
          planet="Sun",
          date="2024-03-20"
      )

2. **Batch Processing**
   
   Use batch processing for multiple calculations:

   .. code-block:: python

      # Calculate multiple charts at once
      charts = calculator.calculate_natal_charts([
          {"date": "2024-03-20", "time": "12:00:00", "lat": 55.7558, "lon": 37.6173},
          {"date": "2024-03-21", "time": "12:00:00", "lat": 55.7558, "lon": 37.6173}
      ])

3. **Parallel Processing**
   
   Use parallel processing for CPU-intensive calculations:

   .. code-block:: python

      # Enable parallel processing
      calculator.enable_parallel_processing()

      # Calculate aspects in parallel
      aspects = chart.calculate_aspects(parallel=True)

Data Validation
-------------

1. **Input Validation**
   
   Validate input data before calculations:

   .. code-block:: python

      from pydantic import BaseModel, validator

      class ChartInput(BaseModel):
          date: str
          time: str
          latitude: float
          longitude: float

          @validator('latitude')
          def validate_latitude(cls, v):
              if not -90 <= v <= 90:
                  raise ValueError('Latitude must be between -90 and 90')
              return v

          @validator('longitude')
          def validate_longitude(cls, v):
              if not -180 <= v <= 180:
                  raise ValueError('Longitude must be between -180 and 180')
              return v

2. **Result Validation**
   
   Validate calculation results:

   .. code-block:: python

      def validate_planet_position(position: dict) -> bool:
          return (
              0 <= position["longitude"] <= 360 and
              -90 <= position["latitude"] <= 90
          )

Memory Management
--------------

1. **Resource Cleanup**
   
   Properly clean up resources:

   .. code-block:: python

      from contextlib import contextmanager

      @contextmanager
      def calculator_context():
          calculator = ChartCalculator()
          try:
              yield calculator
          finally:
              calculator.cleanup()

      # Usage
      with calculator_context() as calculator:
          chart = calculator.calculate_natal_chart(...)

2. **Memory-Efficient Calculations**
   
   Use generators for large datasets:

   .. code-block:: python

      def calculate_progressions_generator(chart, days):
          for day in range(days):
              yield calculator.calculate_progressions(
                  chart=chart,
                  days=day
              )

Testing
------

1. **Unit Tests**
   
   Write comprehensive unit tests:

   .. code-block:: python

      import pytest
      from nocturna_calculations import ChartCalculator

      def test_natal_chart_calculation():
          calculator = ChartCalculator()
          chart = calculator.calculate_natal_chart(
              date="2024-03-20",
              time="12:00:00",
              latitude=55.7558,
              longitude=37.6173
          )
          assert chart is not None
          assert chart.get_planet_position("Sun") is not None

2. **Integration Tests**
   
   Test complex calculations:

   .. code-block:: python

      def test_complex_calculations():
          calculator = ChartCalculator()
          chart = calculator.calculate_natal_chart(...)
          
          # Test multiple features
          aspects = chart.calculate_aspects()
          houses = chart.calculate_houses()
          progressions = calculator.calculate_progressions(chart)
          
          assert all([aspects, houses, progressions])

Documentation
-----------

1. **Code Documentation**
   
   Document your code thoroughly:

   .. code-block:: python

      def calculate_aspects(
          chart: Chart,
          planets: Optional[List[str]] = None,
          aspects: Optional[Dict] = None
      ) -> List[Aspect]:
          """
          Calculate aspects between planets in a chart.

          Args:
              chart: The chart to calculate aspects for
              planets: Optional list of planets to calculate aspects for
              aspects: Optional dictionary of aspect definitions

          Returns:
              List of Aspect objects representing the aspects found

          Raises:
              CalculationError: If the calculation fails
          """
          pass

2. **Usage Examples**
   
   Include usage examples in documentation:

   .. code-block:: python

      """
      Example usage:

      >>> calculator = ChartCalculator()
      >>> chart = calculator.calculate_natal_chart(
      ...     date="2024-03-20",
      ...     time="12:00:00",
      ...     latitude=55.7558,
      ...     longitude=37.6173
      ... )
      >>> aspects = chart.calculate_aspects()
      >>> print(f"Found {len(aspects)} aspects")
      """

Security
-------

1. **Input Sanitization**
   
   Sanitize user input:

   .. code-block:: python

      import re

      def sanitize_date(date: str) -> str:
          # Ensure date is in YYYY-MM-DD format
          if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
              raise ValueError('Invalid date format')
          return date

2. **Error Messages**
   
   Use safe error messages:

   .. code-block:: python

      try:
          chart = calculator.calculate_natal_chart(...)
      except CalculationError as e:
          # Log detailed error internally
          logger.error(f"Calculation failed: {e}")
          # Return safe error message to user
          raise CalculationError("Failed to calculate chart. Please try again.")

For more detailed information about specific features, refer to the :doc:`../api-reference`. 