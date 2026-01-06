# Quickstart Guide

This guide will help you get started with Nocturna Calculations quickly.

## Basic Usage

First, import the necessary components:

```python
from nocturna_calculations import ChartCalculator
from nocturna_calculations.adapters import SwissEphAdapter
```

## Creating a Chart

To create a natal chart:

```python
# Create calculator instance
calculator = ChartCalculator(adapter=SwissEphAdapter())

# Calculate natal chart
chart = calculator.calculate_natal_chart(
    date="2024-03-20",
    time="12:00:00",
    latitude=55.7558,  # Moscow
    longitude=37.6173
)
```

## Getting Planetary Positions

To get planetary positions:

```python
# Get all planetary positions
planets = chart.get_planetary_positions()

# Get position of a specific planet
sun_position = chart.get_planet_position("Sun")

# Print the results
print(f"Sun position: {sun_position.longitude}° {sun_position.sign}")
```

## Calculating Aspects

To calculate aspects between planets:

```python
# Calculate all aspects
aspects = chart.calculate_aspects()

# Calculate aspects for specific planets
sun_moon_aspects = chart.calculate_aspects(planets=["Sun", "Moon"])

# Print the results
for aspect in aspects:
    print(f"{aspect.planet1} {aspect.aspect_type} {aspect.planet2}")
```

## House System Calculations

To calculate house cusps:

```python
# Calculate houses using Placidus system
houses = chart.calculate_houses(system="Placidus")

# Get specific house cusp
ascendant = houses.get_cusp(1)
print(f"Ascendant: {ascendant.longitude}° {ascendant.sign}")
```

## Progressions

To calculate progressions:

```python
# Calculate primary progressions
progressed_chart = calculator.calculate_progressions(
    chart=chart,
    days=365,  # One year of progression
    progression_type="primary"
)

# Get progressed positions
progressed_positions = progressed_chart.get_planetary_positions()
```

## Returns

To calculate returns:

```python
# Calculate solar return
solar_return = calculator.calculate_solar_return(
    chart=chart,
    year=2024
)

# Calculate lunar return
lunar_return = calculator.calculate_lunar_return(
    chart=chart,
    month=3  # March
)
```

## Next Steps

Now that you've learned the basics, you can:

1. Explore more advanced features in the [Advanced Usage Guide](advanced-usage.md)
2. Learn about best practices in the [Best Practices Guide](best-practices.md)
3. Check the [API Reference](../api/reference.md) for detailed API documentation
4. Read about calculation methods in [Calculation Methods](../reference/calculation-methods.md) 