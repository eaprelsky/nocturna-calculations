import pytest
import os
from nocturna_calculations.core.config import Config

class TestConfig:
    @pytest.fixture
    def config(self):
        """Create a config instance for testing."""
        return Config()

    def test_config_initialization(self, config):
        """Test config initialization."""
        assert config is not None
        assert hasattr(config, 'get')
        assert hasattr(config, 'set')

    def test_default_values(self, config):
        """Test default configuration values."""
        assert config.get('ephemeris_path') is not None
        assert config.get('house_system') is not None
        assert config.get('aspect_orb') is not None

    def test_set_get_values(self, config):
        """Test setting and getting configuration values."""
        test_value = "test_value"
        config.set('test_key', test_value)
        assert config.get('test_key') == test_value

    def test_invalid_key(self, config):
        """Test behavior with invalid configuration key."""
        with pytest.raises(KeyError):
            config.get('non_existent_key')

    def test_environment_variables(self, config):
        """Test configuration with environment variables."""
        test_value = "test_env_value"
        os.environ['NOCTURNA_TEST_VAR'] = test_value
        config.set('test_env_key', os.environ.get('NOCTURNA_TEST_VAR'))
        assert config.get('test_env_key') == test_value
        del os.environ['NOCTURNA_TEST_VAR']

    def test_config_persistence(self, config):
        """Test configuration persistence."""
        test_value = "persistent_value"
        config.set('persistent_key', test_value)
        new_config = Config()
        assert new_config.get('persistent_key') == test_value

    def test_config_validation(self, config):
        """Test configuration value validation."""
        # Test invalid house system
        with pytest.raises(ValueError):
            config.set('house_system', 'invalid_system')

        # Test invalid aspect orb
        with pytest.raises(ValueError):
            config.set('aspect_orb', -1)

    def test_config_reset(self, config):
        """Test configuration reset to defaults."""
        config.set('test_key', 'test_value')
        config.reset()
        with pytest.raises(KeyError):
            config.get('test_key')
        assert config.get('house_system') is not None  # Default value should exist

    def test_config_update(self, config):
        """Test bulk configuration update."""
        updates = {
            'house_system': 'P',
            'aspect_orb': 8.0,
            'test_key': 'test_value'
        }
        config.update(updates)
        assert config.get('house_system') == 'P'
        assert config.get('aspect_orb') == 8.0
        assert config.get('test_key') == 'test_value' 