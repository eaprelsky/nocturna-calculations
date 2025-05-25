# Nocturna Calculations Architecture

## Overview

Nocturna Calculations is designed as a modular, extensible library for astrological calculations. The architecture follows SOLID principles and is built with maintainability and extensibility in mind.

## Core Components

### 1. Chart Class
The central class that represents an astrological chart. It contains:
- Date and time information
- Geographic coordinates
- Calculation methods
- Result caching

### 2. Calculation Modules

#### Planetary Calculations
- Position calculations
- Aspect calculations
- House system calculations
- Coordinate system transformations

#### Direction Methods
- Primary directions
- Secondary progressions
- Solar arc directions
- Transits

#### Return Methods
- Solar returns
- Lunar returns
- Progressed returns

#### Rectification Methods
- Single event rectification
- Multiple events rectification
- Result aggregation

### 3. Utility Modules

#### Astronomical Calculations
- Ephemeris calculations
- Coordinate transformations
- Time calculations

#### Data Structures
- Custom types for angles, coordinates
- Result containers
- Configuration objects

## Design Patterns

### Factory Pattern
Used for creating different types of calculations and charts.

### Strategy Pattern
Implemented for different calculation methods and house systems.

### Observer Pattern
Used for progress tracking and result updates.

### Builder Pattern
For constructing complex calculation configurations.

## Dependencies

- **Flatpack:** Core astronomical calculations
- **NumPy:** Numerical computations
- **Pandas:** Data manipulation
- **Pydantic:** Data validation
- **Pytest:** Testing framework

## Code Organization

For a detailed breakdown of modules, classes, and public interfaces, see the [API Reference](./api-reference.md).

## Error Handling

The library implements a comprehensive error handling system:
- Custom exception classes
- Validation at input boundaries
- Graceful degradation
- Detailed error messages

## Performance Considerations

- Caching of intermediate results
- Optimized algorithms for common calculations
- Parallel processing for complex operations
- Memory-efficient data structures

## Testing Strategy

- Unit tests for all calculation methods
- Integration tests for complex scenarios
- Performance benchmarks
- Accuracy validation against known results 