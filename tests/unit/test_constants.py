import pytest
from nocturna_calculations.core.constants import (
    PLANETS,
    SIGNS,
    HOUSES,
    ASPECTS,
    DIGNITIES,
    HOUSE_SYSTEMS
)

class TestConstants:
    def test_planets(self):
        """Test planet constants."""
        assert PLANETS is not None
        assert isinstance(PLANETS, dict)
        assert 'Sun' in PLANETS
        assert 'Moon' in PLANETS
        assert 'Mercury' in PLANETS
        assert 'Venus' in PLANETS
        assert 'Mars' in PLANETS
        assert 'Jupiter' in PLANETS
        assert 'Saturn' in PLANETS
        assert 'Uranus' in PLANETS
        assert 'Neptune' in PLANETS
        assert 'Pluto' in PLANETS

    def test_signs(self):
        """Test zodiac sign constants."""
        assert SIGNS is not None
        assert isinstance(SIGNS, dict)
        assert len(SIGNS) == 12
        assert 'Aries' in SIGNS
        assert 'Taurus' in SIGNS
        assert 'Gemini' in SIGNS
        assert 'Cancer' in SIGNS
        assert 'Leo' in SIGNS
        assert 'Virgo' in SIGNS
        assert 'Libra' in SIGNS
        assert 'Scorpio' in SIGNS
        assert 'Sagittarius' in SIGNS
        assert 'Capricorn' in SIGNS
        assert 'Aquarius' in SIGNS
        assert 'Pisces' in SIGNS

    def test_houses(self):
        """Test house constants."""
        assert HOUSES is not None
        assert isinstance(HOUSES, dict)
        assert len(HOUSES) == 12
        for i in range(1, 13):
            assert f'House_{i}' in HOUSES

    def test_aspects(self):
        """Test aspect constants."""
        assert ASPECTS is not None
        assert isinstance(ASPECTS, dict)
        assert 'Conjunction' in ASPECTS
        assert 'Opposition' in ASPECTS
        assert 'Trine' in ASPECTS
        assert 'Square' in ASPECTS
        assert 'Sextile' in ASPECTS

    def test_dignities(self):
        """Test dignity constants."""
        assert DIGNITIES is not None
        assert isinstance(DIGNITIES, dict)
        assert 'Rulership' in DIGNITIES
        assert 'Exaltation' in DIGNITIES
        assert 'Fall' in DIGNITIES
        assert 'Detriment' in DIGNITIES

    def test_house_systems(self):
        """Test house system constants."""
        assert HOUSE_SYSTEMS is not None
        assert isinstance(HOUSE_SYSTEMS, dict)
        assert 'P' in HOUSE_SYSTEMS  # Placidus
        assert 'K' in HOUSE_SYSTEMS  # Koch
        assert 'O' in HOUSE_SYSTEMS  # Porphyrius
        assert 'R' in HOUSE_SYSTEMS  # Regiomontanus
        assert 'C' in HOUSE_SYSTEMS  # Campanus
        assert 'A' in HOUSE_SYSTEMS  # Equal
        assert 'W' in HOUSE_SYSTEMS  # Whole Sign

    def test_planet_properties(self):
        """Test planet properties in constants."""
        for planet, props in PLANETS.items():
            assert 'number' in props
            assert 'type' in props
            assert 'gender' in props
            assert 'element' in props
            assert 'modality' in props

    def test_sign_properties(self):
        """Test sign properties in constants."""
        for sign, props in SIGNS.items():
            assert 'number' in props
            assert 'element' in props
            assert 'modality' in props
            assert 'ruler' in props
            assert 'degrees' in props

    def test_aspect_properties(self):
        """Test aspect properties in constants."""
        for aspect, props in ASPECTS.items():
            assert 'angle' in props
            assert 'orb' in props
            assert 'nature' in props 