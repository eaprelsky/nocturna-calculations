import pytest
import asyncio
import time
from datetime import datetime, timedelta
import pytz
from nocturna_calculations.calculations.chart import Chart
from nocturna_calculations.calculations.position import Position
from nocturna_calculations.calculations.constants import CoordinateSystem
from nocturna_calculations.exceptions import RateLimitExceeded

class TestRateLimiting:
    @pytest.fixture
    def test_chart_data(self):
        return {
            "date": datetime(2000, 1, 1, 12, 0, 0, tzinfo=pytz.UTC),
            "location": Position(0.0, 51.5, 0.0, CoordinateSystem.GEOGRAPHIC)  # London coordinates
        }

    @pytest.fixture
    def test_user_data(self):
        return {
            "email": f"test_{int(time.time())}@example.com",
            "username": f"testuser_{int(time.time())}",
            "password": "Test123!@#",
            "first_name": "Test",
            "last_name": "User"
        }

    def test_per_user_rate_limit(self, test_chart_data):
        """Test per-user rate limiting"""
        chart = Chart(**test_chart_data)
        user_id = "test_user_123"
        
        # Set rate limit: 10 requests per minute
        chart.set_rate_limit(user_id, requests=10, period=60)
        
        # Make requests within limit
        for _ in range(10):
            result = chart.calculate(user_id=user_id)
            assert result is not None
        
        # Try to exceed limit
        with pytest.raises(RateLimitExceeded):
            chart.calculate(user_id=user_id)

    def test_global_rate_limit(self, test_chart_data):
        """Test global rate limiting"""
        chart = Chart(**test_chart_data)
        
        # Set global rate limit: 100 requests per minute
        chart.set_global_rate_limit(requests=100, period=60)
        
        # Make requests within limit
        for _ in range(100):
            result = chart.calculate()
            assert result is not None
        
        # Try to exceed limit
        with pytest.raises(RateLimitExceeded):
            chart.calculate()

    def test_rate_limit_reset(self, test_chart_data):
        """Test rate limit reset after period"""
        chart = Chart(**test_chart_data)
        user_id = "test_user_123"
        
        # Set rate limit: 5 requests per 2 seconds
        chart.set_rate_limit(user_id, requests=5, period=2)
        
        # Make requests within limit
        for _ in range(5):
            result = chart.calculate(user_id=user_id)
            assert result is not None
        
        # Wait for rate limit to reset
        time.sleep(2.1)
        
        # Should be able to make requests again
        for _ in range(5):
            result = chart.calculate(user_id=user_id)
            assert result is not None

    def test_different_endpoint_limits(self, test_chart_data):
        """Test different rate limits for different endpoints"""
        chart = Chart(**test_chart_data)
        user_id = "test_user_123"
        
        # Set different limits for different operations
        chart.set_rate_limit(user_id, requests=10, period=60, operation="calculate")
        chart.set_rate_limit(user_id, requests=5, period=60, operation="aspects")
        
        # Test calculation limit
        for _ in range(10):
            result = chart.calculate(user_id=user_id)
            assert result is not None
        
        with pytest.raises(RateLimitExceeded):
            chart.calculate(user_id=user_id)
        
        # Test aspects limit
        for _ in range(5):
            result = chart.calculate_aspects(user_id=user_id)
            assert result is not None
        
        with pytest.raises(RateLimitExceeded):
            chart.calculate_aspects(user_id=user_id)

    def test_concurrent_rate_limiting(self, test_chart_data):
        """Test rate limiting under concurrent load"""
        chart = Chart(**test_chart_data)
        user_id = "test_user_123"
        
        # Set rate limit: 20 requests per 5 seconds
        chart.set_rate_limit(user_id, requests=20, period=5)
        
        async def make_request():
            try:
                return await chart.calculate(user_id=user_id)
            except RateLimitExceeded:
                return "rate_limited"
        
        # Make 30 concurrent requests
        tasks = [make_request() for _ in range(30)]
        results = asyncio.run(asyncio.gather(*tasks))
        
        # Verify rate limiting
        success_count = sum(1 for r in results if r != "rate_limited")
        limited_count = sum(1 for r in results if r == "rate_limited")
        
        assert success_count == 20  # Should only allow 20 requests
        assert limited_count == 10  # Should limit 10 requests

    def test_rate_limit_headers(self, test_chart_data):
        """Test rate limit headers in responses"""
        chart = Chart(**test_chart_data)
        user_id = "test_user_123"
        
        # Set rate limit: 10 requests per minute
        chart.set_rate_limit(user_id, requests=10, period=60)
        
        # Make a request and check headers
        response = chart.calculate(user_id=user_id, return_headers=True)
        headers = response.get("headers", {})
        
        assert "X-RateLimit-Limit" in headers
        assert "X-RateLimit-Remaining" in headers
        assert "X-RateLimit-Reset" in headers
        
        assert int(headers["X-RateLimit-Limit"]) == 10
        assert int(headers["X-RateLimit-Remaining"]) == 9

    def test_rate_limit_by_ip(self, test_chart_data):
        """Test rate limiting by IP address"""
        chart = Chart(**test_chart_data)
        ip_address = "192.168.1.1"
        
        # Set rate limit: 50 requests per minute per IP
        chart.set_ip_rate_limit(ip_address, requests=50, period=60)
        
        # Make requests within limit
        for _ in range(50):
            result = chart.calculate(ip_address=ip_address)
            assert result is not None
        
        # Try to exceed limit
        with pytest.raises(RateLimitExceeded):
            chart.calculate(ip_address=ip_address)

    def test_rate_limit_by_subscription(self, test_chart_data):
        """Test rate limiting by subscription tier"""
        chart = Chart(**test_chart_data)
        user_id = "test_user_123"
        
        # Set different limits for different subscription tiers
        chart.set_subscription_rate_limit("free", requests=10, period=60)
        chart.set_subscription_rate_limit("premium", requests=100, period=60)
        
        # Test free tier limit
        chart.set_user_subscription(user_id, "free")
        for _ in range(10):
            result = chart.calculate(user_id=user_id)
            assert result is not None
        
        with pytest.raises(RateLimitExceeded):
            chart.calculate(user_id=user_id)
        
        # Test premium tier limit
        chart.set_user_subscription(user_id, "premium")
        for _ in range(100):
            result = chart.calculate(user_id=user_id)
            assert result is not None
        
        with pytest.raises(RateLimitExceeded):
            chart.calculate(user_id=user_id)

    def test_rate_limit_grace_period(self, test_chart_data):
        """Test rate limit grace period"""
        chart = Chart(**test_chart_data)
        user_id = "test_user_123"
        
        # Set rate limit with grace period
        chart.set_rate_limit(user_id, requests=5, period=60, grace_period=3)
        
        # Make requests within limit
        for _ in range(5):
            result = chart.calculate(user_id=user_id)
            assert result is not None
        
        # Should get warning but not error for first 3 requests
        for _ in range(3):
            result = chart.calculate(user_id=user_id)
            assert result is not None
            assert chart.get_rate_limit_warnings(user_id) > 0
        
        # Should get error after grace period
        with pytest.raises(RateLimitExceeded):
            chart.calculate(user_id=user_id)

    def test_rate_limit_by_endpoint_complexity(self, test_chart_data):
        """Test rate limiting based on endpoint complexity"""
        chart = Chart(**test_chart_data)
        user_id = "test_user_123"
        
        # Set different limits based on complexity
        chart.set_complexity_rate_limit("simple", requests=100, period=60)
        chart.set_complexity_rate_limit("complex", requests=10, period=60)
        
        # Test simple endpoint limit
        for _ in range(100):
            result = chart.calculate_simple(user_id=user_id)
            assert result is not None
        
        with pytest.raises(RateLimitExceeded):
            chart.calculate_simple(user_id=user_id)
        
        # Test complex endpoint limit
        for _ in range(10):
            result = chart.calculate_complex(user_id=user_id)
            assert result is not None
        
        with pytest.raises(RateLimitExceeded):
            chart.calculate_complex(user_id=user_id) 