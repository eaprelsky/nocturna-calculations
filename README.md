# Nocturna Calculations

A Python library for astrological calculations based on Swiss Ephemeris. This library provides a comprehensive set of tools for calculating various astrological elements including planetary positions, house systems, aspects, and more.

## Features

- Natal chart calculations
- Planetary positions and movements
- House system calculations (Placidus, Koch, etc.)
- Aspect calculations
- Primary and secondary progressions
- Solar and lunar returns
- Eclipse calculations
- And more...

## Installation

```bash
pip install nocturna-calculations
```

## Quick Start

```python
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
```

## Documentation

Full documentation is available at [ReadTheDocs](https://nocturna-calculations.readthedocs.io/).

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to submit pull requests, report issues, and more.

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/eaprelsky/nocturna-calculations.git
cd nocturna-calculations

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

- Author: Yegor Aprelsky
- Email: yegor.aprelsky@gmail.com
- GitHub: [eaprelsky](https://github.com/eaprelsky) 