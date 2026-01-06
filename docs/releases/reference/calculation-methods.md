# Calculation Methods

This document describes the various calculation methods implemented in the Nocturna Calculations library.

## Planetary Positions

### Ephemeris Calculations

The library uses the Swiss Ephemeris for high-precision planetary position calculations. The calculations include:

- Geocentric positions
- Topocentric positions
- Apparent positions (including light-time correction)
- True positions (excluding light-time correction)
- Fixed star positions
- Asteroid positions
- Lunar node positions
- Arabic parts positions

### Coordinate Systems

The library supports multiple coordinate systems:

1. **Ecliptic Coordinates**
   - Longitude (0-360°)
   - Latitude (-90° to +90°)

2. **Equatorial Coordinates**
   - Right Ascension (0-24h)
   - Declination (-90° to +90°)

3. **Horizontal Coordinates**
   - Altitude (-90° to +90°)
   - Azimuth (0-360°)

4. **Galactic Coordinates**
   - Longitude (0-360°)
   - Latitude (-90° to +90°)

## Aspects

### Aspect Types

The library calculates the following aspects:

1. **Major Aspects**
   - Conjunction (0°)
   - Opposition (180°)
   - Trine (120°)
   - Square (90°)
   - Sextile (60°)

2. **Minor Aspects**
   - Semi-sextile (30°)
   - Semi-square (45°)
   - Sesquisquare (135°)
   - Quincunx (150°)
   - Quintile (72°)
   - Biquintile (144°)
   - Septile (51.43°)
   - Biseptile (102.86°)
   - Triseptile (154.29°)
   - Novile (40°)
   - Binovile (80°)
   - Quadrinovile (160°)

3. **Declination Aspects**
   - Parallel (0°)
   - Contraparallel (180°)

### Orb Calculations

- Default orbs for each aspect type
- Custom orb settings
- Orb calculations based on planet combinations
- Dynamic orbs based on planet speeds
- Harmonic orbs

## House Systems

The library supports multiple house systems:

1. **Placidus**
   - Time-based system
   - Most common in modern astrology

2. **Koch**
   - Space-based system
   - Popular in German-speaking countries

3. **Equal House**
   - Simple division of the ecliptic
   - 30° per house

4. **Whole Sign**
   - Each sign is a house
   - Traditional system

5. **Campanus**
   - Space-based system
   - Uses prime vertical

6. **Regiomontanus**
   - Space-based system
   - Uses celestial equator

7. **Meridian**
   - Time-based system
   - Uses local meridian

8. **Morinus**
   - Space-based system
   - Uses prime vertical

## Direction Methods

### Primary Directions

1. **Calculation Methods**
   - Semi-arc method
   - Placidus method
   - Regiomontanus method
   - Naibod method
   - Ptolemy method

2. **Key Points**
   - Promissor and significator
   - Mundane and zodiacal aspects
   - Direct and converse directions
   - Parallel and contraparallel directions
   - Antiscia directions

### Secondary Progressions

1. **Day-for-a-Year Method**
   - One day = one year
   - Most common progression method

2. **Month-for-a-Year Method**
   - One month = one year
   - Alternative progression method

3. **Calculation Steps**
   - Calculate progressed date
   - Determine planetary positions
   - Calculate aspects
   - Calculate house positions

### Solar Arc Directions

1. **Calculation Methods**
   - Standard method (1° = 1 year)
   - Naibod method (0.9856° = 1 year)
   - Custom arc rate

2. **Key Features**
   - Simple calculation
   - Direct correlation with age
   - Easy to understand
   - Multiple calculation methods

## Return Methods

### Solar Return

1. **Calculation Steps**
   - Find Sun's return to natal position
   - Calculate chart for return moment
   - Determine house positions
   - Calculate aspects

2. **Key Points**
   - Annual cycle
   - Personal year chart
   - House emphasis
   - Location options

### Lunar Return

1. **Calculation Steps**
   - Find Moon's return to natal position
   - Calculate chart for return moment
   - Determine house positions
   - Calculate aspects

2. **Key Points**
   - Monthly cycle
   - Emotional patterns
   - Daily activities
   - Location options

### Planetary Returns

1. **Supported Planets**
   - Mercury
   - Venus
   - Mars
   - Jupiter
   - Saturn
   - Uranus
   - Neptune
   - Pluto

2. **Calculation Features**
   - Return to natal position
   - Return to natal house
   - Return aspects
   - Location options

## Advanced Methods

### Harmonics

1. **Calculation Types**
   - Harmonic positions
   - Harmonic aspects
   - Harmonic patterns
   - Harmonic returns

2. **Features**
   - Any harmonic number
   - Multiple calculation methods
   - Pattern recognition
   - Aspect analysis

### Antiscia

1. **Calculation Types**
   - Antiscia points
   - Contra-antiscia points
   - Antiscia aspects
   - Antiscia patterns

2. **Features**
   - Multiple calculation methods
   - Pattern recognition
   - Aspect analysis
   - Return calculations

### Declinations

1. **Calculation Types**
   - Parallel aspects
   - Contraparallel aspects
   - Declination patterns
   - Declination returns

2. **Features**
   - Multiple calculation methods
   - Pattern recognition
   - Aspect analysis
   - Return calculations

## Utility Calculations

### Time Conversions

1. **Julian Day**
   - Standard astronomical time
   - Continuous count of days
   - Basis for calculations

2. **Sidereal Time**
   - Star time
   - Basis for house calculations
   - Varies with longitude

3. **Ephemeris Time**
   - Dynamical time
   - Used for ephemeris calculations
   - Accounts for Earth's rotation

### Coordinate Transformations

1. **Ecliptic to Equatorial**
   - Uses obliquity of ecliptic
   - Accounts for precession
   - Standard conversion

2. **Equatorial to Horizontal**
   - Uses local sidereal time
   - Accounts for latitude
   - Time-dependent

3. **Ecliptic to Galactic**
   - Uses galactic pole
   - Accounts for precession
   - Standard conversion

## Accuracy and Precision

### Calculation Precision

- Planetary positions: 0.01 arcsecond
- House cusps: 0.1 degree
- Aspects: 0.1 degree
- Returns: 1 minute of time
- Fixed stars: 0.1 arcsecond
- Arabic parts: 0.1 degree

### Validation Methods

1. **Ephemeris Comparison**
   - Swiss Ephemeris
   - NASA JPL
   - Historical data
   - Multiple sources

2. **Known Events**
   - Eclipses
   - Planetary stations
   - Special configurations
   - Historical events

3. **Cross-Validation**
   - Multiple calculation methods
   - Different coordinate systems
   - Various time scales
   - Different house systems

## Rectification Methods

### Single Event Rectification

1. **Event-Based Method**
   - Calculate directions for time window
   - Compare with event timing
   - Score potential times
   - Validate results

2. **Pattern-Based Method**
   - Identify key patterns
   - Calculate pattern timing
   - Compare with events
   - Score matches

3. **Calculation Features**
   - Multiple direction methods
   - Aspect analysis
   - House emphasis
   - Pattern recognition

### Multiple Events Rectification

1. **Event Collection**
   - Major life events
   - Career milestones
   - Relationship events
   - Health events
   - Location changes

2. **Analysis Methods**
   - Statistical analysis
   - Pattern frequency
   - Timing correlations
   - House emphasis
   - Aspect strength

3. **Result Aggregation**
   - Time window scoring
   - Confidence levels
   - Pattern identification
   - Cross-validation

### Advanced Rectification Techniques

1. **Harmonic Analysis**
   - Harmonic charts
   - Harmonic aspects
   - Harmonic patterns
   - Time harmonics

2. **Midpoint Analysis**
   - Planetary midpoints
   - House midpoints
   - Special point midpoints
   - Pattern midpoints

3. **Validation Methods**
   - Cross-reference events
   - Pattern consistency
   - House system verification
   - Method comparison

### Rectification Calculation Engine

1. **Core Components**
   - Time window generator
   - Chart calculator
   - Pattern analyzer
   - Score calculator

2. **Optimization Features**
   - Parallel processing
   - Result caching
   - Memory management
   - Performance tuning

3. **Result Processing**
   - Time windows
   - Confidence scores
   - Pattern matches
   - Recommendations 