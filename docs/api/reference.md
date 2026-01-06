# Nocturna Calculations API Reference

## Core Classes

### Chart

The main class for creating and managing astrological charts.

```python
class Chart:
    def __init__(
        self,
        date: str | datetime,
        time: str | time,
        latitude: float,
        longitude: float,
        timezone: str = "UTC",
        config: Config = None
    ):
        """
        Initialize a new chart.
        
        Args:
            date: Date in YYYY-MM-DD format or datetime object
            time: Time in HH:MM:SS format or time object
            latitude: Geographic latitude in degrees
            longitude: Geographic longitude in degrees
            timezone: Timezone string (default: "UTC")
            config: Configuration object for calculation settings
        """
        pass

    def calculate_planetary_positions(self) -> Dict[str, Position]:
        """Calculate positions of all planets."""
        pass

    def calculate_aspects(self) -> List[Aspect]:
        """Calculate aspects between planets."""
        pass

    def calculate_houses(self, system: str = "Placidus") -> Dict[str, float]:
        """Calculate house cusps."""
        pass

    def calculate_fixed_stars(self) -> Dict[str, Position]:
        """Calculate positions of fixed stars."""
        pass

    def calculate_arabic_parts(self) -> Dict[str, float]:
        """Calculate Arabic parts."""
        pass

    def calculate_dignities(self) -> Dict[str, Dignity]:
        """Calculate planetary dignities."""
        pass

    def calculate_antiscia(self) -> Dict[str, Position]:
        """Calculate antiscia points."""
        pass

    def calculate_declinations(self) -> Dict[str, float]:
        """Calculate declinations of all points."""
        pass

    def calculate_harmonics(self, harmonic: int) -> Dict[str, Position]:
        """Calculate harmonic positions."""
        pass

    def calculate_rectification(
        self,
        events: List[Event],
        time_window: Tuple[datetime, datetime],
        method: str = "event-based"
    ) -> RectificationResult:
        """
        Calculate rectification for the chart.
        
        Args:
            events: List of events to use for rectification
            time_window: Tuple of (start_time, end_time) for the search window
            method: Rectification method ("event-based", "pattern-based")
        
        Returns:
            RectificationResult object
        """
        pass

    def calculate_harmonic_rectification(
        self,
        events: List[Event],
        time_window: Tuple[datetime, datetime],
        harmonic: int
    ) -> RectificationResult:
        """
        Calculate rectification using harmonic analysis.
        
        Args:
            events: List of events to use for rectification
            time_window: Tuple of (start_time, end_time) for the search window
            harmonic: Harmonic number to use
        
        Returns:
            RectificationResult object
        """
        pass

    def calculate_midpoint_rectification(
        self,
        events: List[Event],
        time_window: Tuple[datetime, datetime]
    ) -> RectificationResult:
        """
        Calculate rectification using midpoint analysis.
        
        Args:
            events: List of events to use for rectification
            time_window: Tuple of (start_time, end_time) for the search window
        
        Returns:
            RectificationResult object
        """
        pass
```

### Position

Represents a celestial body's position.

```python
class Position:
    def __init__(
        self,
        longitude: float,
        latitude: float = 0.0,
        distance: float = 1.0,
        declination: float = None
    ):
        """
        Initialize a new position.
        
        Args:
            longitude: Longitude in degrees
            latitude: Latitude in degrees (default: 0.0)
            distance: Distance in AU (default: 1.0)
            declination: Declination in degrees (optional)
        """
        pass
```

### Aspect

Represents an aspect between two celestial bodies.

```python
class Aspect:
    def __init__(
        self,
        planet1: str,
        planet2: str,
        angle: float,
        orb: float,
        aspect_type: str,
        applying: bool = None
    ):
        """
        Initialize a new aspect.
        
        Args:
            planet1: First planet name
            planet2: Second planet name
            angle: Aspect angle in degrees
            orb: Orb in degrees
            aspect_type: Type of aspect (e.g., "conjunction", "trine")
            applying: Whether the aspect is applying (optional)
        """
        pass
```

### Dignity

Represents planetary dignity information.

```python
class Dignity:
    def __init__(
        self,
        planet: str,
        rulership: int = 0,
        exaltation: int = 0,
        detriment: int = 0,
        fall: int = 0,
        triplicity: int = 0,
        term: int = 0,
        face: int = 0
    ):
        """
        Initialize dignity information.
        
        Args:
            planet: Planet name
            rulership: Rulership score (-5 to +5)
            exaltation: Exaltation score (-5 to +5)
            detriment: Detriment score (-5 to +5)
            fall: Fall score (-5 to +5)
            triplicity: Triplicity score (-5 to +5)
            term: Term score (-5 to +5)
            face: Face score (-5 to +5)
        """
        pass
```

## Calculation Methods

### Primary Directions

```python
def calculate_primary_directions(
    chart: Chart,
    target_date: str | datetime,
    planets: List[str] = None,
    method: str = "semi-arc"
) -> List[Direction]:
    """
    Calculate primary directions.
    
    Args:
        chart: Source chart
        target_date: Target date
        planets: List of planets to calculate (default: all)
        method: Calculation method ("semi-arc", "placidus", "regiomontanus")
    
    Returns:
        List of Direction objects
    """
    pass
```

### Secondary Progressions

```python
def calculate_secondary_progressions(
    chart: Chart,
    target_date: str | datetime,
    planets: List[str] = None,
    method: str = "day-for-year"
) -> List[Position]:
    """
    Calculate secondary progressions.
    
    Args:
        chart: Source chart
        target_date: Target date
        planets: List of planets to calculate (default: all)
        method: Calculation method ("day-for-year", "month-for-year")
    
    Returns:
        List of Position objects
    """
    pass
```

### Solar Arc Directions

```python
def calculate_solar_arc(
    chart: Chart,
    target_date: str | datetime,
    planets: List[str] = None,
    method: str = "standard"
) -> List[Position]:
    """
    Calculate solar arc directions.
    
    Args:
        chart: Source chart
        target_date: Target date
        planets: List of planets to calculate (default: all)
        method: Calculation method ("standard", "naibod")
    
    Returns:
        List of Position objects
    """
    pass
```

### Returns

```python
def calculate_solar_return(
    chart: Chart,
    target_date: str | datetime,
    location: Optional[Tuple[float, float]] = None
) -> Chart:
    """
    Calculate solar return chart.
    
    Args:
        chart: Source chart
        target_date: Target date
        location: Optional location (lat, lon) for the return
    
    Returns:
        New Chart object for the return
    """
    pass

def calculate_lunar_return(
    chart: Chart,
    target_date: str | datetime,
    location: Optional[Tuple[float, float]] = None
) -> Chart:
    """
    Calculate lunar return chart.
    
    Args:
        chart: Source chart
        target_date: Target date
        location: Optional location (lat, lon) for the return
    
    Returns:
        New Chart object for the return
    """
    pass

def calculate_planetary_return(
    chart: Chart,
    planet: str,
    target_date: str | datetime,
    location: Optional[Tuple[float, float]] = None
) -> Chart:
    """
    Calculate planetary return chart.
    
    Args:
        chart: Source chart
        planet: Planet to calculate return for
        target_date: Target date
        location: Optional location (lat, lon) for the return
    
    Returns:
        New Chart object for the return
    """
    pass
```

### Harmonics

```python
def calculate_harmonic_chart(
    chart: Chart,
    harmonic: int,
    planets: List[str] = None
) -> Dict[str, Position]:
    """
    Calculate harmonic chart.
    
    Args:
        chart: Source chart
        harmonic: Harmonic number
        planets: List of planets to calculate (default: all)
    
    Returns:
        Dictionary of planet positions in the harmonic
    """
    pass

def calculate_harmonic_aspects(
    chart: Chart,
    harmonic: int,
    planets: List[str] = None
) -> List[Aspect]:
    """
    Calculate aspects in harmonic chart.
    
    Args:
        chart: Source chart
        harmonic: Harmonic number
        planets: List of planets to calculate (default: all)
    
    Returns:
        List of aspects in the harmonic
    """
    pass
```

### Antiscia

```python
def calculate_antiscia_points(
    chart: Chart,
    planets: List[str] = None
) -> Dict[str, Position]:
    """
    Calculate antiscia points.
    
    Args:
        chart: Source chart
        planets: List of planets to calculate (default: all)
    
    Returns:
        Dictionary of antiscia positions
    """
    pass

def calculate_antiscia_aspects(
    chart: Chart,
    planets: List[str] = None
) -> List[Aspect]:
    """
    Calculate aspects to antiscia points.
    
    Args:
        chart: Source chart
        planets: List of planets to calculate (default: all)
    
    Returns:
        List of aspects to antiscia points
    """
    pass
```

### Declinations

```python
def calculate_parallels(
    chart: Chart,
    planets: List[str] = None
) -> List[Parallel]:
    """
    Calculate declination parallels.
    
    Args:
        chart: Source chart
        planets: List of planets to calculate (default: all)
    
    Returns:
        List of parallel aspects
    """
    pass

def calculate_contraparallels(
    chart: Chart,
    planets: List[str] = None
) -> List[Parallel]:
    """
    Calculate declination contraparallels.
    
    Args:
        chart: Source chart
        planets: List of planets to calculate (default: all)
    
    Returns:
        List of contraparallel aspects
    """
    pass
```

## Rectification Methods

### Event-Based Rectification

```python
def calculate_event_based_rectification(
    chart: Chart,
    event: Event,
    time_window: Tuple[datetime, datetime],
    direction_method: str = "semi-arc"
) -> RectificationResult:
    """
    Calculate rectification using a single event.
    
    Args:
        chart: Source chart
        event: Event to use for rectification
        time_window: Tuple of (start_time, end_time) for the search window
        direction_method: Direction calculation method
    
    Returns:
        RectificationResult object
    """
    pass
```

### Pattern-Based Rectification

```python
def calculate_pattern_based_rectification(
    chart: Chart,
    events: List[Event],
    time_window: Tuple[datetime, datetime],
    pattern_types: List[str] = None
) -> RectificationResult:
    """
    Calculate rectification using pattern analysis.
    
    Args:
        chart: Source chart
        events: List of events to use for rectification
        time_window: Tuple of (start_time, end_time) for the search window
        pattern_types: List of pattern types to look for
    
    Returns:
        RectificationResult object
    """
    pass
```

### Multiple Events Rectification

```python
def calculate_multiple_events_rectification(
    chart: Chart,
    events: List[Event],
    time_window: Tuple[datetime, datetime],
    weights: Dict[str, float] = None
) -> RectificationResult:
    """
    Calculate rectification using multiple events.
    
    Args:
        chart: Source chart
        events: List of events to use for rectification
        time_window: Tuple of (start_time, end_time) for the search window
        weights: Dictionary of event weights
    
    Returns:
        RectificationResult object
    """
    pass
```

### Rectification Result Classes

```python
class Event:
    def __init__(
        self,
        date: datetime,
        description: str,
        location: Optional[Tuple[float, float]] = None,
        weight: float = 1.0,
        type: str = "general"
    ):
        """
        Initialize a new event.
        
        Args:
            date: Event date and time
            description: Event description
            location: Optional (latitude, longitude) tuple
            weight: Event weight for calculations
            type: Event type (e.g., "career", "relationship", "health")
        """
        pass

class RectificationResult:
    def __init__(
        self,
        suggested_time: datetime,
        confidence: float,
        time_windows: List[Tuple[datetime, datetime]],
        scores: Dict[str, float],
        patterns: List[Pattern],
        validation_results: List[ValidationResult]
    ):
        """
        Initialize a rectification result.
        
        Args:
            suggested_time: Suggested birth time
            confidence: Confidence score (0-1)
            time_windows: List of valid time windows
            scores: Dictionary of method-specific scores
            patterns: List of identified patterns
            validation_results: List of validation results
        """
        pass

class Pattern:
    def __init__(
        self,
        type: str,
        planets: List[str],
        aspects: List[Aspect],
        score: float
    ):
        """
        Initialize a pattern.
        
        Args:
            type: Pattern type
            planets: List of planets involved
            aspects: List of aspects in the pattern
            score: Pattern strength score
        """
        pass

class ValidationResult:
    def __init__(
        self,
        method: str,
        passed: bool,
        score: float,
        details: Dict[str, Any]
    ):
        """
        Initialize a validation result.
        
        Args:
            method: Validation method name
            passed: Whether validation passed
            score: Validation score
            details: Additional validation details
        """
        pass
```

### Rectification Configuration

```python
class RectificationConfig:
    def __init__(
        self,
        direction_methods: List[str] = None,
        pattern_types: List[str] = None,
        validation_methods: List[str] = None,
        min_confidence: float = 0.7,
        time_step: timedelta = timedelta(minutes=1),
        max_iterations: int = 1000
    ):
        """
        Initialize rectification configuration.
        
        Args:
            direction_methods: List of direction methods to use
            pattern_types: List of pattern types to look for
            validation_methods: List of validation methods to use
            min_confidence: Minimum confidence threshold
            time_step: Time step for calculations
            max_iterations: Maximum number of iterations
        """
        pass
```

## Utility Functions

### Coordinate Transformations

```python
def ecliptic_to_equatorial(
    longitude: float,
    latitude: float,
    date: datetime
) -> Tuple[float, float]:
    """
    Convert ecliptic coordinates to equatorial.
    
    Args:
        longitude: Ecliptic longitude in degrees
        latitude: Ecliptic latitude in degrees
        date: Date for the conversion
    
    Returns:
        Tuple of (right ascension, declination) in degrees
    """
    pass

def equatorial_to_ecliptic(
    ra: float,
    dec: float,
    date: datetime
) -> Tuple[float, float]:
    """
    Convert equatorial coordinates to ecliptic.
    
    Args:
        ra: Right ascension in degrees
        dec: Declination in degrees
        date: Date for the conversion
    
    Returns:
        Tuple of (longitude, latitude) in degrees
    """
    pass

def ecliptic_to_horizontal(
    longitude: float,
    latitude: float,
    date: datetime,
    location: Tuple[float, float]
) -> Tuple[float, float]:
    """
    Convert ecliptic coordinates to horizontal.
    
    Args:
        longitude: Ecliptic longitude in degrees
        latitude: Ecliptic latitude in degrees
        date: Date for the conversion
        location: (latitude, longitude) in degrees
    
    Returns:
        Tuple of (altitude, azimuth) in degrees
    """
    pass
```

### Time Calculations

```python
def calculate_julian_day(
    date: str | datetime,
    time: str | time = None
) -> float:
    """
    Calculate Julian Day.
    
    Args:
        date: Date in YYYY-MM-DD format or datetime object
        time: Time in HH:MM:SS format or time object (optional)
    
    Returns:
        Julian Day as float
    """
    pass

def calculate_sidereal_time(
    jd: float,
    longitude: float
) -> float:
    """
    Calculate Local Sidereal Time.
    
    Args:
        jd: Julian Day
        longitude: Geographic longitude in degrees
    
    Returns:
        LST in degrees
    """
    pass

def calculate_obliquity(
    jd: float
) -> float:
    """
    Calculate obliquity of ecliptic.
    
    Args:
        jd: Julian Day
    
    Returns:
        Obliquity in degrees
    """
    pass
```

## Configuration

### Config

```python
class Config:
    def __init__(
        self,
        orbs: Dict[str, float] = None,
        aspects: List[str] = None,
        house_system: str = "Placidus",
        fixed_stars: List[str] = None,
        arabic_parts: List[str] = None,
        calculation_methods: Dict[str, str] = None
    ):
        """
        Initialize configuration.
        
        Args:
            orbs: Dictionary of aspect orbs
            aspects: List of aspects to calculate
            house_system: Default house system
            fixed_stars: List of fixed stars to include
            arabic_parts: List of Arabic parts to calculate
            calculation_methods: Dictionary of calculation method preferences
        """
        pass
```

# Test Coverage Plan

This section outlines the comprehensive set of tests required to achieve 100% test coverage for the Nocturna Calculations API. The tests are organized by class and function, ensuring that all features, edge cases, and error conditions are validated.

## Chart Class
- **Initialization**
  - Test initialization with valid and invalid date/time formats.
  - Test initialization with missing or invalid latitude/longitude.
  - Test initialization with and without timezone and config.
- **calculate_planetary_positions**
  - Test correct calculation for all supported planets.
  - Test with custom configuration (e.g., orbs, aspects).
  - Test error handling for invalid chart data.
- **calculate_aspects**
  - Test detection of all major and minor aspects.
  - Test aspect calculation with custom orbs.
  - Test empty and edge-case charts (e.g., no planets).
- **calculate_houses**
  - Test house cusp calculation for all supported systems.
  - Test with invalid or unsupported house system.
- **calculate_fixed_stars**
  - Test calculation for all configured fixed stars.
  - Test with empty or custom fixed star lists.
- **calculate_arabic_parts**
  - Test calculation for all standard Arabic parts.
  - Test with custom Arabic part definitions.
- **calculate_dignities**
  - Test correct dignity assignment for all planets.
  - Test with custom dignity tables.
- **calculate_antiscia**
  - Test antiscia point calculation for all planets.
- **calculate_declinations**
  - Test declination calculation for all points.
- **calculate_harmonics**
  - Test harmonic position calculation for various harmonics.
  - Test with invalid harmonic numbers.
- **calculate_rectification**
  - Test event-based and pattern-based rectification methods.
  - Test with empty, single, and multiple events.
  - Test with invalid time windows and methods.
- **calculate_harmonic_rectification**
  - Test harmonic rectification with valid/invalid harmonics.
- **calculate_midpoint_rectification**
  - Test midpoint rectification with various event sets.

## Position Class
- **Initialization**
  - Test with valid and invalid longitude, latitude, distance, and declination values.
  - Test default values for optional parameters.

## Aspect Class
- **Initialization**
  - Test with valid and invalid planet names, angles, orbs, and aspect types.
  - Test optional applying parameter.

## Dignity Class
- **Initialization**
  - Test with valid and invalid planet names and dignity scores.
  - Test default values for all parameters.

## Calculation Methods
- **calculate_primary_directions**
  - Test calculation for all supported methods and planets.
  - Test with invalid method names and empty planet lists.
- **calculate_secondary_progressions**
  - Test for both day-for-year and month-for-year methods.
  - Test with invalid method names.
- **calculate_solar_arc**
  - Test standard and naibod methods.
  - Test with invalid method names.
- **calculate_solar_return / calculate_lunar_return / calculate_planetary_return**
  - Test return chart calculation for all supported planets and locations.
  - Test with missing or invalid location data.
- **calculate_harmonic_chart / calculate_harmonic_aspects**
  - Test for various harmonics and planet lists.
  - Test with invalid harmonic numbers.
- **calculate_antiscia_points / calculate_antiscia_aspects**
  - Test for all planets and with custom planet lists.
- **calculate_parallels / calculate_contraparallels**
  - Test for all planets and with custom planet lists.

## Rectification Methods
- **calculate_event_based_rectification**
  - Test with valid/invalid events, time windows, and direction methods.
- **calculate_pattern_based_rectification**
  - Test with various event sets and pattern types.
- **calculate_multiple_events_rectification**
  - Test with weighted and unweighted event lists.
  - Test with invalid weights.

## Rectification Result Classes
- **Event Class**
  - Test initialization with all parameter combinations.
  - Test with invalid dates, locations, and weights.
- **RectificationResult Class**
  - Test initialization with all parameter combinations.
  - Test with empty and populated lists/dictionaries.
- **Pattern Class**
  - Test initialization with valid/invalid types, planets, aspects, and scores.
- **ValidationResult Class**
  - Test initialization with all parameter combinations.
  - Test with invalid method names and details.

## Rectification Configuration
- **RectificationConfig Class**
  - Test initialization with all parameter combinations.
  - Test with invalid values for confidence, time_step, and max_iterations.

## Utility Functions
- **ecliptic_to_equatorial / equatorial_to_ecliptic / ecliptic_to_horizontal**
  - Test with valid and invalid coordinates and dates.
  - Test edge cases (e.g., poles, equator).
- **calculate_julian_day**
  - Test with string and datetime inputs, with and without time.
  - Test invalid date/time formats.
- **calculate_sidereal_time**
  - Test with valid/invalid Julian Day and longitude values.
- **calculate_obliquity**
  - Test with valid/invalid Julian Day values.

## Additional Test Categories & Enhancements

To ensure the highest quality and robustness, the following additional test categories are recommended:

### Boundary and Extreme Value Testing
- Explicitly test for astronomical boundary values (e.g., maximum/minimum declinations, longitudes, latitudes).
- Test calculations at the poles, equator, and for extreme dates (e.g., leap years, far past/future).

### Performance and Stress Testing
- Test performance with very large event lists and long time windows.
- Test rectification and calculation methods with high iteration counts (e.g., max_iterations in RectificationConfig).
- Ensure calculations complete within reasonable time and resource limits.

### Concurrency and Thread Safety (if applicable)
- Test API behavior under concurrent access (e.g., multiple threads or async calls).
- Check for race conditions or data corruption when used in parallel environments.

### Serialization and Deserialization
- Test saving and loading of all major objects (Chart, Event, RectificationResult, etc.) to/from common formats (e.g., JSON, pickle).
- Ensure no data loss or corruption during serialization cycles.

### Integration and End-to-End Testing
- Test full calculation flows from input data to final output (e.g., create chart, calculate positions, aspects, returns, etc.).
- Validate that all components work together as expected in real-world scenarios.

### Negative and Exception Path Testing
- Explicitly test for correct exception raising, error messages, and recovery for all invalid inputs and failure modes.
- Ensure API fails gracefully and provides useful feedback.

### Documentation and Example Validation
- Validate that all docstrings, usage examples, and API documentation match actual behavior and outputs.
- Test that example code in documentation runs without errors and produces expected results. 