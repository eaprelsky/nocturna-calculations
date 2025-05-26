import pytest
import asyncio
import time
import psutil
import os
from datetime import datetime, timedelta
import pytz
from nocturna_calculations.calculations.chart import Chart
from nocturna_calculations.calculations.position import Position
from nocturna_calculations.calculations.constants import CoordinateSystem
from nocturna_calculations.exceptions import PerformanceError

class TestExtendedPerformance:
    @pytest.fixture
    def test_chart_data(self):
        return {
            "date": datetime(2000, 1, 1, 12, 0, 0, tzinfo=pytz.UTC),
            "location": Position(0.0, 51.5, 0.0, CoordinateSystem.GEOGRAPHIC)  # London coordinates
        }

    def test_large_batch_calculations(self, test_chart_data):
        """Test performance of large batch calculations"""
        start_time = time.time()
        charts = []
        
        # Create and calculate 1000 charts
        for i in range(1000):
            date = test_chart_data["date"] + timedelta(days=i)
            chart = Chart(date=date, location=test_chart_data["location"])
            result = chart.calculate()
            charts.append(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify performance
        assert total_time < 60  # Should complete within 60 seconds
        assert len(charts) == 1000
        assert all(chart is not None for chart in charts)

    def test_memory_optimization(self, test_chart_data):
        """Test memory optimization during calculations"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform memory-intensive operations
        charts = []
        for i in range(5000):
            date = test_chart_data["date"] + timedelta(days=i)
            chart = Chart(date=date, location=test_chart_data["location"])
            result = chart.calculate()
            charts.append(result)
            
            # Force garbage collection every 1000 charts
            if i % 1000 == 0:
                import gc
                gc.collect()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Verify memory usage
        assert memory_increase < 500 * 1024 * 1024  # Less than 500MB increase
        assert len(charts) == 5000

    def test_cpu_utilization(self, test_chart_data):
        """Test CPU utilization during calculations"""
        process = psutil.Process(os.getpid())
        cpu_percentages = []
        
        # Monitor CPU usage during calculations
        for i in range(100):
            start_cpu = process.cpu_percent()
            chart = Chart(**test_chart_data)
            result = chart.calculate()
            end_cpu = process.cpu_percent()
            cpu_percentages.append(end_cpu - start_cpu)
        
        # Verify CPU usage
        avg_cpu = sum(cpu_percentages) / len(cpu_percentages)
        assert avg_cpu < 80  # Average CPU usage should be less than 80%

    def test_disk_io_performance(self, test_chart_data):
        """Test disk I/O performance"""
        import tempfile
        import shutil
        
        # Create temporary directory for testing
        temp_dir = tempfile.mkdtemp()
        try:
            start_time = time.time()
            
            # Perform disk I/O operations
            for i in range(1000):
                chart = Chart(**test_chart_data)
                result = chart.calculate()
                
                # Save results to disk
                file_path = os.path.join(temp_dir, f"chart_{i}.json")
                with open(file_path, 'w') as f:
                    f.write(str(result))
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Verify disk I/O performance
            assert total_time < 30  # Should complete within 30 seconds
            assert len(os.listdir(temp_dir)) == 1000
            
        finally:
            # Clean up
            shutil.rmtree(temp_dir)

    def test_network_performance(self, test_chart_data):
        """Test network performance for API calls"""
        import aiohttp
        import asyncio
        
        async def make_request(session, i):
            async with session.post(
                "http://localhost:8000/api/calculations/chart",
                json={
                    "date": (test_chart_data["date"] + timedelta(days=i)).isoformat(),
                    "latitude": test_chart_data["location"].latitude,
                    "longitude": test_chart_data["location"].longitude
                }
            ) as response:
                return await response.json()
        
        async def run_test():
            async with aiohttp.ClientSession() as session:
                tasks = [make_request(session, i) for i in range(100)]
                start_time = time.time()
                results = await asyncio.gather(*tasks)
                end_time = time.time()
                return results, end_time - start_time
        
        results, total_time = asyncio.run(run_test())
        
        # Verify network performance
        assert total_time < 20  # Should complete within 20 seconds
        assert len(results) == 100
        assert all(result is not None for result in results)

    def test_cache_efficiency(self, test_chart_data):
        """Test cache efficiency"""
        chart = Chart(**test_chart_data)
        
        # First calculation (cache miss)
        start_time = time.time()
        result1 = chart.calculate()
        first_calculation_time = time.time() - start_time
        
        # Subsequent calculations (cache hits)
        cache_times = []
        for _ in range(100):
            start_time = time.time()
            result = chart.calculate()
            cache_times.append(time.time() - start_time)
        
        # Verify cache efficiency
        avg_cache_time = sum(cache_times) / len(cache_times)
        assert avg_cache_time < first_calculation_time * 0.1  # 90% faster with cache

    def test_concurrent_resource_usage(self, test_chart_data):
        """Test resource usage under concurrent load"""
        async def calculate_chart():
            chart = Chart(**test_chart_data)
            return await chart.calculate()
        
        # Monitor system resources during concurrent calculations
        process = psutil.Process(os.getpid())
        initial_cpu = process.cpu_percent()
        initial_memory = process.memory_info().rss
        
        # Run 100 concurrent calculations
        tasks = [calculate_chart() for _ in range(100)]
        results = asyncio.run(asyncio.gather(*tasks))
        
        final_cpu = process.cpu_percent()
        final_memory = process.memory_info().rss
        
        # Verify resource usage
        assert final_cpu - initial_cpu < 50  # CPU increase less than 50%
        assert final_memory - initial_memory < 100 * 1024 * 1024  # Memory increase less than 100MB
        assert len(results) == 100

    def test_database_performance(self, test_chart_data):
        """Test database performance"""
        import sqlite3
        
        # Create test database
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # Create test table
        cursor.execute('''
            CREATE TABLE test_charts (
                id INTEGER PRIMARY KEY,
                date TEXT,
                latitude REAL,
                longitude REAL,
                result TEXT
            )
        ''')
        
        start_time = time.time()
        
        # Perform database operations
        for i in range(1000):
            chart = Chart(**test_chart_data)
            result = chart.calculate()
            cursor.execute(
                'INSERT INTO test_charts (date, latitude, longitude, result) VALUES (?, ?, ?, ?)',
                (
                    test_chart_data["date"].isoformat(),
                    test_chart_data["location"].latitude,
                    test_chart_data["location"].longitude,
                    str(result)
                )
            )
        
        conn.commit()
        end_time = time.time()
        
        # Verify database performance
        assert end_time - start_time < 30  # Should complete within 30 seconds
        cursor.execute('SELECT COUNT(*) FROM test_charts')
        assert cursor.fetchone()[0] == 1000
        
        conn.close()

    def test_error_handling_performance(self, test_chart_data):
        """Test performance of error handling"""
        chart = Chart(**test_chart_data)
        
        # Test error handling performance
        start_time = time.time()
        error_count = 0
        
        for i in range(1000):
            try:
                # Simulate error condition
                if i % 10 == 0:
                    raise ValueError("Simulated error")
                chart.calculate()
            except Exception:
                error_count += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify error handling performance
        assert total_time < 30  # Should complete within 30 seconds
        assert error_count == 100  # Should catch all errors

    def test_serialization_performance(self, test_chart_data):
        """Test performance of data serialization"""
        import json
        import pickle
        
        chart = Chart(**test_chart_data)
        result = chart.calculate()
        
        # Test JSON serialization
        start_time = time.time()
        for _ in range(1000):
            json_str = json.dumps(result)
            json.loads(json_str)
        json_time = time.time() - start_time
        
        # Test pickle serialization
        start_time = time.time()
        for _ in range(1000):
            pickle_str = pickle.dumps(result)
            pickle.loads(pickle_str)
        pickle_time = time.time() - start_time
        
        # Verify serialization performance
        assert json_time < 10  # JSON serialization should complete within 10 seconds
        assert pickle_time < 5  # Pickle serialization should complete within 5 seconds 