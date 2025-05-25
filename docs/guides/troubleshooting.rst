Troubleshooting Guide
==================

This guide helps you resolve common issues when using Nocturna Calculations.

Installation Issues
----------------

1. **Swiss Ephemeris Files Missing**
   
   **Symptoms:**
   - Error message about missing Swiss Ephemeris files
   - Calculations fail with "File not found" errors

   **Solution:**
   
   a. Check if Swiss Ephemeris files are installed:
   
   .. code-block:: python

      from pyswisseph import swe_set_ephe_path
      import os

      # Set the path to your Swiss Ephemeris files
      swe_set_ephe_path('/path/to/ephemeris/files')

   b. Download and install Swiss Ephemeris files:
   
   .. code-block:: bash

      # Create directory for ephemeris files
      mkdir -p ~/.nocturna/ephemeris
      
      # Download files (example)
      wget https://www.astro.com/swisseph/ephe.zip
      unzip ephe.zip -d ~/.nocturna/ephemeris

2. **Dependency Conflicts**
   
   **Symptoms:**
   - Package installation fails
   - Import errors for dependencies

   **Solution:**
   
   a. Create a fresh virtual environment:
   
   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate
      pip install --upgrade pip
      pip install nocturna-calculations

   b. Check dependency versions:
   
   .. code-block:: bash

      pip freeze | grep -E "pyswisseph|numpy|pydantic"

Calculation Issues
---------------

1. **Incorrect Planetary Positions**
   
   **Symptoms:**
   - Positions don't match known ephemeris data
   - Large discrepancies in calculations

   **Solution:**
   
   a. Verify ephemeris files:
   
   .. code-block:: python

      from pyswisseph import swe_calc_ut
      import datetime

      # Test calculation
      date = datetime.datetime(2024, 3, 20, 12, 0)
      julian_day = swe_julday(date.year, date.month, date.day, date.hour)
      result = swe_calc_ut(julian_day, 0)  # Sun
      print(f"Sun position: {result[0]}")

   b. Check timezone handling:
   
   .. code-block:: python

      from datetime import datetime
      import pytz

      # Convert to UTC
      local_time = datetime(2024, 3, 20, 12, 0)
      utc_time = pytz.timezone('UTC').localize(local_time)

2. **House System Calculation Errors**
   
   **Symptoms:**
   - House cusps are incorrect
   - Different house systems give same results

   **Solution:**
   
   a. Verify house system implementation:
   
   .. code-block:: python

      # Test different house systems
      chart = calculator.calculate_natal_chart(
          date="2024-03-20",
          time="12:00:00",
          latitude=55.7558,
          longitude=37.6173,
          house_systems=["Placidus", "Koch", "Whole Sign"]
      )

      # Compare results
      for system in ["Placidus", "Koch", "Whole Sign"]:
          houses = chart.get_houses(system)
          print(f"{system} Ascendant: {houses.get_cusp(1)}")

Performance Issues
--------------

1. **Slow Calculations**
   
   **Symptoms:**
   - Calculations take longer than expected
   - High CPU usage

   **Solution:**
   
   a. Enable caching:
   
   .. code-block:: python

      calculator.enable_caching()
      
      # Use cached results
      positions = calculator.get_cached_positions(
          planet="Sun",
          date="2024-03-20"
      )

   b. Use batch processing:
   
   .. code-block:: python

      # Calculate multiple charts at once
      charts = calculator.calculate_natal_charts([
          {"date": "2024-03-20", "time": "12:00:00", "lat": 55.7558, "lon": 37.6173},
          {"date": "2024-03-21", "time": "12:00:00", "lat": 55.7558, "lon": 37.6173}
      ])

2. **Memory Usage**
   
   **Symptoms:**
   - High memory consumption
   - Out of memory errors

   **Solution:**
   
   a. Use generators for large datasets:
   
   .. code-block:: python

      def calculate_progressions_generator(chart, days):
          for day in range(days):
              yield calculator.calculate_progressions(
                  chart=chart,
                  days=day
              )

   b. Clean up resources:
   
   .. code-block:: python

      from contextlib import contextmanager

      @contextmanager
      def calculator_context():
          calculator = ChartCalculator()
          try:
              yield calculator
          finally:
              calculator.cleanup()

API Issues
--------

1. **Authentication Errors**
   
   **Symptoms:**
   - API requests fail with 401 errors
   - Token validation failures

   **Solution:**
   
   a. Check API key:
   
   .. code-block:: python

      from nocturna_calculations.api import APIClient

      client = APIClient(api_key="your-api-key")
      # Test connection
      client.test_connection()

   b. Verify token expiration:
   
   .. code-block:: python

      # Check token expiration
      if client.is_token_expired():
          client.refresh_token()

2. **Rate Limiting**
   
   **Symptoms:**
   - API requests fail with 429 errors
   - Throttling messages

   **Solution:**
   
   a. Implement rate limiting:
   
   .. code-block:: python

      from ratelimit import limits, sleep_and_retry

      @sleep_and_retry
      @limits(calls=100, period=60)
      def make_api_request():
          # Your API request here
          pass

   b. Use batch requests:
   
   .. code-block:: python

      # Batch multiple requests
      results = client.batch_request([
          {"method": "calculate_chart", "params": {...}},
          {"method": "calculate_aspects", "params": {...}}
      ])

Debugging
--------

1. **Enable Debug Logging**
   
   .. code-block:: python

      import logging

      # Configure logging
      logging.basicConfig(
          level=logging.DEBUG,
          format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
      )

      # Create logger
      logger = logging.getLogger('nocturna_calculations')

2. **Use Debug Mode**
   
   .. code-block:: python

      calculator = ChartCalculator(debug=True)
      
      # Enable detailed logging
      calculator.enable_debug_logging()

Getting Help
----------

If you're still experiencing issues:

1. Check the :doc:`../api-reference` for detailed API documentation
2. Review the :doc:`best-practices` guide for optimization tips
3. Search for similar issues in the `GitHub Issues <https://github.com/eaprelsky/nocturna-calculations/issues>`_
4. Create a new issue with:
   - Detailed description of the problem
   - Steps to reproduce
   - Error messages and logs
   - Environment information 