# Nocturna Calculations

An open-source Python library for astrological calculations.

## Overview

Nocturna Calculations is a comprehensive library for performing various astrological calculations, including:

- Planetary positions and aspects
- Primary directions
- Secondary progressions
- Solar arc directions
- Transits
- Solar and Lunar returns
- Progressed charts
- Lunar node calculations
- Rectification methods

## Core Features

- High-precision astronomical calculations
- Support for multiple calculation methods
- Extensible architecture for adding new methods
- Comprehensive test coverage
- Well-documented API

## Installation

```bash
pip install nocturna-calculations
```

## Quick Start

```python
from nocturna_calculations import Chart

# Create a new chart
chart = Chart(
    date="2024-03-20",
    time="12:00:00",
    latitude=55.7558,
    longitude=37.6173
)

# Calculate planetary positions
positions = chart.calculate_planetary_positions()

# Calculate aspects
aspects = chart.calculate_aspects()
```

## Documentation

For detailed documentation, please refer to the following sections:

- [Architecture](architecture.md)
- [API Reference](api-reference.md)
- [Calculation Methods](calculation-methods.md)
- [Rectification](rectification.md)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 