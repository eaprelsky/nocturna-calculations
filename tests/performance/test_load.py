import pytest
import asyncio
import time
from datetime import datetime, timedelta
import pytz
from locust import HttpUser, task, between
from nocturna.calculations.chart import Chart
from nocturna.calculations.position import Position
from nocturna.calculations.constants import CoordinateSystem

class TestLoad:
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

    class ChartCalculationUser(HttpUser):
        wait_time = between(1, 3)

        @task(3)
        def calculate_chart(self):
            """Test chart calculation endpoint"""
            response = self.client.post(
                "/api/calculations/chart",
                json={
                    "date": "2000-01-01T12:00:00Z",
                    "latitude": 51.5,
                    "longitude": 0.0
                }
            )
            assert response.status_code == 200
            assert "planets" in response.json()
            assert "houses" in response.json()

        @task(2)
        def calculate_aspects(self):
            """Test aspects calculation endpoint"""
            response = self.client.post(
                "/api/calculations/aspects",
                json={
                    "date": "2000-01-01T12:00:00Z",
                    "latitude": 51.5,
                    "longitude": 0.0,
                    "orb_settings": {
                        "conjunction": 8.0,
                        "opposition": 8.0,
                        "trine": 8.0
                    }
                }
            )
            assert response.status_code == 200
            assert "aspects" in response.json()

        @task(1)
        def calculate_houses(self):
            """Test houses calculation endpoint"""
            response = self.client.post(
                "/api/calculations/houses",
                json={
                    "date": "2000-01-01T12:00:00Z",
                    "latitude": 51.5,
                    "longitude": 0.0,
                    "house_system": "PLACIDUS"
                }
            )
            assert response.status_code == 200
            assert "houses" in response.json()

    def test_concurrent_chart_calculations(self, test_chart_data):
        """Test concurrent chart calculations"""
        async def calculate_chart():
            chart = Chart(**test_chart_data)
            return await chart.calculate()

        # Run 100 concurrent calculations
        tasks = [calculate_chart() for _ in range(100)]
        results = asyncio.run(asyncio.gather(*tasks))
        
        # Verify all calculations completed successfully
        assert len(results) == 100
        for result in results:
            assert result is not None
            assert "planets" in result
            assert "houses" in result

    def test_concurrent_user_registrations(self, test_user_data):
        """Test concurrent user registrations"""
        async def register_user():
            response = await self.client.post("/api/auth/register", json=test_user_data)
            return response

        # Run 50 concurrent registrations
        tasks = [register_user() for _ in range(50)]
        results = asyncio.run(asyncio.gather(*tasks))
        
        # Verify all registrations completed successfully
        assert len(results) == 50
        for result in results:
            assert result.status_code == 200
            assert "user_id" in result.json()

    def test_sustained_load(self, test_chart_data):
        """Test sustained load over time"""
        start_time = time.time()
        duration = 300  # 5 minutes
        request_count = 0
        error_count = 0

        while time.time() - start_time < duration:
            try:
                chart = Chart(**test_chart_data)
                result = chart.calculate()
                request_count += 1
            except Exception:
                error_count += 1

        # Verify performance metrics
        total_time = time.time() - start_time
        requests_per_second = request_count / total_time
        error_rate = error_count / request_count if request_count > 0 else 0

        assert requests_per_second >= 10  # Minimum 10 requests per second
        assert error_rate < 0.01  # Less than 1% error rate

    def test_memory_usage(self, test_chart_data):
        """Test memory usage under load"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Create and calculate 1000 charts
        charts = []
        for _ in range(1000):
            chart = Chart(**test_chart_data)
            result = chart.calculate()
            charts.append(result)

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Verify memory usage
        assert memory_increase < 100 * 1024 * 1024  # Less than 100MB increase

    def test_database_connection_pool(self, test_user_data):
        """Test database connection pool under load"""
        async def perform_database_operation():
            # Simulate database operations
            await asyncio.sleep(0.1)
            return True

        # Run 200 concurrent database operations
        tasks = [perform_database_operation() for _ in range(200)]
        results = asyncio.run(asyncio.gather(*tasks))
        
        # Verify all operations completed successfully
        assert len(results) == 200
        assert all(results)

    def test_cache_performance(self, test_chart_data):
        """Test cache performance under load"""
        chart = Chart(**test_chart_data)
        
        # First calculation (cache miss)
        start_time = time.time()
        result1 = chart.calculate()
        first_calculation_time = time.time() - start_time

        # Second calculation (cache hit)
        start_time = time.time()
        result2 = chart.calculate()
        second_calculation_time = time.time() - start_time

        # Verify cache performance
        assert second_calculation_time < first_calculation_time * 0.1  # 90% faster with cache

    def test_error_handling_under_load(self, test_chart_data):
        """Test error handling under load"""
        async def calculate_with_error():
            try:
                # Simulate error condition
                if time.time() % 2 == 0:
                    raise ValueError("Simulated error")
                chart = Chart(**test_chart_data)
                return await chart.calculate()
            except Exception as e:
                return str(e)

        # Run 100 concurrent calculations with potential errors
        tasks = [calculate_with_error() for _ in range(100)]
        results = asyncio.run(asyncio.gather(*tasks))
        
        # Verify error handling
        error_count = sum(1 for r in results if isinstance(r, str))
        assert error_count > 0  # Some errors should occur
        assert error_count < len(results) * 0.6  # Less than 60% error rate

    def test_resource_cleanup(self, test_chart_data):
        """Test resource cleanup under load"""
        import gc

        # Force garbage collection
        gc.collect()
        initial_objects = len(gc.get_objects())

        # Create and calculate 1000 charts
        for _ in range(1000):
            chart = Chart(**test_chart_data)
            result = chart.calculate()
            del chart
            del result

        # Force garbage collection again
        gc.collect()
        final_objects = len(gc.get_objects())

        # Verify resource cleanup
        assert final_objects - initial_objects < 1000  # Less than 1000 objects leaked 