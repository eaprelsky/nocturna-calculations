import pytest
from nocturna_calculations.core.dignity import Dignity

class TestDignity:
    @pytest.fixture
    def valid_dignity(self):
        return Dignity(
            planet="Sun",
            rulership=5,
            exaltation=4,
            detriment=-5,
            fall=-4,
            triplicity=3,
            term=2,
            face=1
        )

    def test_dignity_initialization(self):
        """Test basic dignity initialization with all parameters"""
        dignity = Dignity(
            planet="Sun",
            rulership=5,
            exaltation=4,
            detriment=-5,
            fall=-4,
            triplicity=3,
            term=2,
            face=1
        )
        assert dignity.planet == "Sun"
        assert dignity.rulership == 5
        assert dignity.exaltation == 4
        assert dignity.detriment == -5
        assert dignity.fall == -4
        assert dignity.triplicity == 3
        assert dignity.term == 2
        assert dignity.face == 1

    def test_dignity_default_values(self):
        """Test dignity initialization with default values"""
        dignity = Dignity(planet="Sun")
        assert dignity.planet == "Sun"
        assert dignity.rulership == 0
        assert dignity.exaltation == 0
        assert dignity.detriment == 0
        assert dignity.fall == 0
        assert dignity.triplicity == 0
        assert dignity.term == 0
        assert dignity.face == 0

    def test_dignity_score_validation(self):
        """Test dignity score validation for all fields"""
        # Test valid scores
        valid_scores = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
        for score in valid_scores:
            dignity = Dignity(
                planet="Sun",
                rulership=score,
                exaltation=score,
                detriment=score,
                fall=score,
                triplicity=score,
                term=score,
                face=score
            )
            assert dignity.rulership == score
            assert dignity.exaltation == score
            assert dignity.detriment == score
            assert dignity.fall == score
            assert dignity.triplicity == score
            assert dignity.term == score
            assert dignity.face == score

        # Test invalid scores
        invalid_scores = [-6, 6, -10, 10]
        for score in invalid_scores:
            with pytest.raises(ValueError):
                Dignity(
                    planet="Sun",
                    rulership=score
                )
            with pytest.raises(ValueError):
                Dignity(
                    planet="Sun",
                    exaltation=score
                )
            with pytest.raises(ValueError):
                Dignity(
                    planet="Sun",
                    detriment=score
                )
            with pytest.raises(ValueError):
                Dignity(
                    planet="Sun",
                    fall=score
                )
            with pytest.raises(ValueError):
                Dignity(
                    planet="Sun",
                    triplicity=score
                )
            with pytest.raises(ValueError):
                Dignity(
                    planet="Sun",
                    term=score
                )
            with pytest.raises(ValueError):
                Dignity(
                    planet="Sun",
                    face=score
                )

    def test_dignity_immutability(self, valid_dignity):
        """Test that dignity attributes are immutable"""
        with pytest.raises(AttributeError):
            valid_dignity.planet = "Moon"

        with pytest.raises(AttributeError):
            valid_dignity.rulership = 4

        with pytest.raises(AttributeError):
            valid_dignity.exaltation = 3

        with pytest.raises(AttributeError):
            valid_dignity.detriment = -4

        with pytest.raises(AttributeError):
            valid_dignity.fall = -3

        with pytest.raises(AttributeError):
            valid_dignity.triplicity = 2

        with pytest.raises(AttributeError):
            valid_dignity.term = 1

        with pytest.raises(AttributeError):
            valid_dignity.face = 0

    def test_dignity_equality(self):
        """Test dignity equality comparison"""
        dignity1 = Dignity(
            planet="Sun",
            rulership=5,
            exaltation=4,
            detriment=-5,
            fall=-4,
            triplicity=3,
            term=2,
            face=1
        )
        dignity2 = Dignity(
            planet="Sun",
            rulership=5,
            exaltation=4,
            detriment=-5,
            fall=-4,
            triplicity=3,
            term=2,
            face=1
        )
        dignity3 = Dignity(
            planet="Moon",
            rulership=5,
            exaltation=4,
            detriment=-5,
            fall=-4,
            triplicity=3,
            term=2,
            face=1
        )

        assert dignity1 == dignity2
        assert dignity1 != dignity3
        assert dignity2 != dignity3

    def test_dignity_string_representation(self, valid_dignity):
        """Test dignity string representation"""
        expected_str = "Dignity(Sun: Rulership=5, Exaltation=4, Detriment=-5, Fall=-4, Triplicity=3, Term=2, Face=1)"
        assert str(valid_dignity) == expected_str

    def test_dignity_total_score(self, valid_dignity):
        """Test total dignity score calculation"""
        # Sum of all scores: 5 + 4 + (-5) + (-4) + 3 + 2 + 1 = 6
        assert valid_dignity.total_score() == 6

    def test_dignity_essential_score(self, valid_dignity):
        """Test essential dignity score calculation"""
        # Sum of rulership and exaltation: 5 + 4 = 9
        assert valid_dignity.essential_score() == 9

    def test_dignity_accidental_score(self, valid_dignity):
        """Test accidental dignity score calculation"""
        # Sum of triplicity, term, and face: 3 + 2 + 1 = 6
        assert valid_dignity.accidental_score() == 6

    def test_dignity_debilitated_score(self, valid_dignity):
        """Test debilitated dignity score calculation"""
        # Sum of detriment and fall: (-5) + (-4) = -9
        assert valid_dignity.debilitated_score() == -9 