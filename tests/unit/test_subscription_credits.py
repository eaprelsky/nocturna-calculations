import pytest
from datetime import datetime, timedelta
import pytz
from nocturna_calculations.models.subscription import Subscription, SubscriptionType, SubscriptionStatus, CreditTransaction
from nocturna_calculations.models.user import User
from nocturna_calculations.exceptions import SubscriptionError, CreditError, ValidationError

class TestSubscriptionCredits:
    @pytest.fixture
    def test_user(self):
        return User(
            email="test@example.com",
            username="testuser",
            password="Test123!@#",
            first_name="Test",
            last_name="User",
            created_at=datetime.now(pytz.UTC)
        )

    @pytest.fixture
    def test_subscription_data(self):
        return {
            "type": SubscriptionType.PREMIUM,
            "status": SubscriptionStatus.ACTIVE,
            "start_date": datetime.now(pytz.UTC),
            "end_date": datetime.now(pytz.UTC) + timedelta(days=30),
            "credits": 1000,
            "auto_renew": True,
            "monthly_credits": 500,
            "credit_rollover": True,
            "max_rollover": 2000
        }

    def test_subscription_creation(self, test_user, test_subscription_data):
        """Test subscription creation and validation"""
        # Test valid subscription creation
        subscription = Subscription(user=test_user, **test_subscription_data)
        assert subscription.type == test_subscription_data["type"]
        assert subscription.status == test_subscription_data["status"]
        assert subscription.credits == test_subscription_data["credits"]
        assert subscription.auto_renew == test_subscription_data["auto_renew"]

        # Test invalid subscription type
        with pytest.raises(ValidationError):
            Subscription(user=test_user, **{**test_subscription_data, "type": "INVALID"})

        # Test invalid credit amount
        with pytest.raises(ValidationError):
            Subscription(user=test_user, **{**test_subscription_data, "credits": -100})

    def test_credit_management(self, test_user, test_subscription_data):
        """Test credit management operations"""
        subscription = Subscription(user=test_user, **test_subscription_data)

        # Test credit addition
        subscription.add_credits(500)
        assert subscription.credits == 1500

        # Test credit deduction
        subscription.deduct_credits(200)
        assert subscription.credits == 1300

        # Test insufficient credits
        with pytest.raises(CreditError):
            subscription.deduct_credits(2000)

        # Test credit rollover
        subscription.credits = subscription.max_rollover
        subscription.add_credits(500)
        assert subscription.credits == subscription.max_rollover

    def test_subscription_renewal(self, test_user, test_subscription_data):
        """Test subscription renewal process"""
        subscription = Subscription(user=test_user, **test_subscription_data)

        # Test auto-renewal
        subscription.end_date = datetime.now(pytz.UTC) - timedelta(days=1)
        subscription.process_renewal()
        assert subscription.status == SubscriptionStatus.ACTIVE
        assert subscription.credits == test_subscription_data["monthly_credits"]

        # Test manual renewal
        subscription.auto_renew = False
        subscription.end_date = datetime.now(pytz.UTC) - timedelta(days=1)
        subscription.renew()
        assert subscription.status == SubscriptionStatus.ACTIVE
        assert subscription.end_date > datetime.now(pytz.UTC)

    def test_credit_transactions(self, test_user, test_subscription_data):
        """Test credit transaction tracking"""
        subscription = Subscription(user=test_user, **test_subscription_data)

        # Test transaction creation
        transaction = CreditTransaction(
            subscription=subscription,
            amount=100,
            type="ADD",
            description="Monthly credit allocation"
        )
        assert transaction.amount == 100
        assert transaction.type == "ADD"

        # Test transaction history
        subscription.add_credits(100, "Test credit addition")
        subscription.deduct_credits(50, "Test credit deduction")
        assert len(subscription.get_transaction_history()) == 2

    def test_subscription_upgrades(self, test_user, test_subscription_data):
        """Test subscription upgrade process"""
        subscription = Subscription(user=test_user, **test_subscription_data)

        # Test upgrade to higher tier
        subscription.upgrade(SubscriptionType.PROFESSIONAL)
        assert subscription.type == SubscriptionType.PROFESSIONAL
        assert subscription.monthly_credits > test_subscription_data["monthly_credits"]

        # Test downgrade
        with pytest.raises(SubscriptionError):
            subscription.downgrade(SubscriptionType.BASIC)

    def test_credit_expiration(self, test_user, test_subscription_data):
        """Test credit expiration handling"""
        subscription = Subscription(user=test_user, **test_subscription_data)

        # Test credit expiration
        subscription.credits = 1000
        subscription.process_credit_expiration()
        assert subscription.credits == test_subscription_data["monthly_credits"]

        # Test credit rollover with expiration
        subscription.credits = 2000
        subscription.credit_rollover = False
        subscription.process_credit_expiration()
        assert subscription.credits == test_subscription_data["monthly_credits"]

    def test_subscription_cancellation(self, test_user, test_subscription_data):
        """Test subscription cancellation"""
        subscription = Subscription(user=test_user, **test_subscription_data)

        # Test cancellation
        subscription.cancel()
        assert subscription.auto_renew is False
        assert subscription.status == SubscriptionStatus.ACTIVE

        # Test cancellation with immediate effect
        subscription.cancel(immediate=True)
        assert subscription.status == SubscriptionStatus.CANCELLED

    def test_credit_usage_tracking(self, test_user, test_subscription_data):
        """Test credit usage tracking"""
        subscription = Subscription(user=test_user, **test_subscription_data)

        # Test usage tracking
        subscription.track_credit_usage("chart_calculation", 10)
        subscription.track_credit_usage("aspect_analysis", 5)
        usage_stats = subscription.get_credit_usage_stats()
        assert usage_stats["chart_calculation"] == 10
        assert usage_stats["aspect_analysis"] == 5

        # Test usage limits
        with pytest.raises(CreditError):
            subscription.track_credit_usage("chart_calculation", subscription.credits + 1)

    def test_subscription_validation(self, test_user, test_subscription_data):
        """Test subscription validation rules"""
        # Test invalid dates
        with pytest.raises(ValidationError):
            Subscription(
                user=test_user,
                **{
                    **test_subscription_data,
                    "start_date": datetime.now(pytz.UTC) + timedelta(days=1),
                    "end_date": datetime.now(pytz.UTC)
                }
            )

        # Test invalid credit limits
        with pytest.raises(ValidationError):
            Subscription(
                user=test_user,
                **{
                    **test_subscription_data,
                    "monthly_credits": 0
                }
            )

        # Test invalid rollover settings
        with pytest.raises(ValidationError):
            Subscription(
                user=test_user,
                **{
                    **test_subscription_data,
                    "max_rollover": 100,
                    "monthly_credits": 200
                }
            ) 