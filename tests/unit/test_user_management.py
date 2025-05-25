import pytest
from datetime import datetime, timedelta
import pytz
from nocturna.models.user import User, UserProfile, UserSettings
from nocturna.models.subscription import SubscriptionType, SubscriptionStatus
from nocturna.exceptions import UserError, ValidationError

class TestUserManagement:
    @pytest.fixture
    def test_user_data(self):
        return {
            "email": "test@example.com",
            "username": "testuser",
            "password": "Test123!@#",
            "first_name": "Test",
            "last_name": "User",
            "created_at": datetime.now(pytz.UTC)
        }

    @pytest.fixture
    def test_settings_data(self):
        return {
            "default_house_system": "PLACIDUS",
            "default_orbs": {
                "conjunction": 8.0,
                "opposition": 8.0,
                "trine": 8.0,
                "square": 8.0,
                "sextile": 6.0
            },
            "timezone": "UTC",
            "language": "en",
            "theme": "light"
        }

    @pytest.fixture
    def test_subscription_data(self):
        return {
            "type": SubscriptionType.PREMIUM,
            "status": SubscriptionStatus.ACTIVE,
            "start_date": datetime.now(pytz.UTC),
            "end_date": datetime.now(pytz.UTC) + timedelta(days=30),
            "credits": 1000,
            "auto_renew": True
        }

    def test_user_creation(self, test_user_data):
        """Test user creation and validation"""
        # Test valid user creation
        user = User(**test_user_data)
        assert user.email == test_user_data["email"]
        assert user.username == test_user_data["username"]
        assert user.first_name == test_user_data["first_name"]
        assert user.last_name == test_user_data["last_name"]
        assert user.is_active is True
        assert user.is_verified is False

        # Test invalid email
        with pytest.raises(ValidationError):
            User(**{**test_user_data, "email": "invalid-email"})

        # Test invalid username
        with pytest.raises(ValidationError):
            User(**{**test_user_data, "username": "a"})  # Too short

        # Test invalid password
        with pytest.raises(ValidationError):
            User(**{**test_user_data, "password": "weak"})

    def test_user_profile(self, test_user_data):
        """Test user profile management"""
        user = User(**test_user_data)
        profile = UserProfile(user=user)

        # Test profile update
        profile.bio = "Test bio"
        profile.location = "Test Location"
        profile.website = "https://example.com"
        assert profile.bio == "Test bio"
        assert profile.location == "Test Location"
        assert profile.website == "https://example.com"

        # Test invalid website
        with pytest.raises(ValidationError):
            profile.website = "invalid-url"

        # Test profile completion
        assert profile.is_complete() is False
        profile.bio = "Test bio"
        profile.location = "Test Location"
        assert profile.is_complete() is True

    def test_user_settings(self, test_user_data, test_settings_data):
        """Test user settings management"""
        user = User(**test_user_data)
        settings = UserSettings(user=user, **test_settings_data)

        # Test default settings
        assert settings.default_house_system == test_settings_data["default_house_system"]
        assert settings.default_orbs == test_settings_data["default_orbs"]
        assert settings.timezone == test_settings_data["timezone"]
        assert settings.language == test_settings_data["language"]
        assert settings.theme == test_settings_data["theme"]

        # Test settings update
        settings.default_house_system = "KOCH"
        settings.timezone = "America/New_York"
        assert settings.default_house_system == "KOCH"
        assert settings.timezone == "America/New_York"

        # Test invalid house system
        with pytest.raises(ValidationError):
            settings.default_house_system = "INVALID"

        # Test invalid timezone
        with pytest.raises(ValidationError):
            settings.timezone = "Invalid/Timezone"

    def test_user_subscription(self, test_user_data, test_subscription_data):
        """Test user subscription management"""
        user = User(**test_user_data)
        user.subscription = test_subscription_data

        # Test subscription status
        assert user.subscription.status == SubscriptionStatus.ACTIVE
        assert user.subscription.type == SubscriptionType.PREMIUM
        assert user.subscription.credits == 1000

        # Test credit management
        user.subscription.credits -= 100
        assert user.subscription.credits == 900

        # Test subscription expiration
        user.subscription.end_date = datetime.now(pytz.UTC) - timedelta(days=1)
        assert user.subscription.is_expired() is True

        # Test subscription renewal
        user.subscription.renew()
        assert user.subscription.status == SubscriptionStatus.ACTIVE
        assert user.subscription.is_expired() is False

    def test_user_authentication(self, test_user_data):
        """Test user authentication"""
        user = User(**test_user_data)

        # Test password verification
        assert user.verify_password(test_user_data["password"]) is True
        assert user.verify_password("wrong_password") is False

        # Test password change
        new_password = "NewTest123!@#"
        user.change_password(new_password)
        assert user.verify_password(new_password) is True
        assert user.verify_password(test_user_data["password"]) is False

        # Test account verification
        assert user.is_verified is False
        user.verify()
        assert user.is_verified is True

    def test_user_deactivation(self, test_user_data):
        """Test user account deactivation"""
        user = User(**test_user_data)

        # Test account deactivation
        assert user.is_active is True
        user.deactivate()
        assert user.is_active is False

        # Test account reactivation
        user.activate()
        assert user.is_active is True

    def test_user_data_validation(self, test_user_data):
        """Test user data validation"""
        # Test email validation
        with pytest.raises(ValidationError):
            User(**{**test_user_data, "email": "invalid@email"})

        # Test username validation
        with pytest.raises(ValidationError):
            User(**{**test_user_data, "username": "user@name"})  # Invalid characters

        # Test name validation
        with pytest.raises(ValidationError):
            User(**{**test_user_data, "first_name": "123"})  # Invalid characters

        # Test password strength
        with pytest.raises(ValidationError):
            User(**{**test_user_data, "password": "weak"})

    def test_user_preferences(self, test_user_data, test_settings_data):
        """Test user preferences management"""
        user = User(**test_user_data)
        settings = UserSettings(user=user, **test_settings_data)

        # Test preference updates
        settings.update_preferences({
            "theme": "dark",
            "language": "es",
            "notifications": {
                "email": True,
                "push": False
            }
        })
        assert settings.theme == "dark"
        assert settings.language == "es"
        assert settings.notifications["email"] is True
        assert settings.notifications["push"] is False

        # Test invalid preference values
        with pytest.raises(ValidationError):
            settings.update_preferences({
                "theme": "invalid_theme"
            })

    def test_user_statistics(self, test_user_data):
        """Test user statistics tracking"""
        user = User(**test_user_data)

        # Test chart count
        assert user.get_chart_count() == 0
        user.increment_chart_count()
        assert user.get_chart_count() == 1

        # Test calculation count
        assert user.get_calculation_count() == 0
        user.increment_calculation_count()
        assert user.get_calculation_count() == 1

        # Test last activity
        assert user.last_activity is None
        user.update_last_activity()
        assert user.last_activity is not None 