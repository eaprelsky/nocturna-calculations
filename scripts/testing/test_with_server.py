#!/usr/bin/env python3
"""
Integrated API Test Runner with Server Management

This script automatically:
1. Starts the development server in the background
2. Waits for it to be ready
3. Runs the API tests
4. Stops the server and cleans up

Usage:
    python test_with_server.py                 # Run all API tests with auto server
    python test_with_server.py --auth          # Run only auth tests
    python test_with_server.py --charts        # Run only chart tests
    python test_with_server.py --calculations  # Run only calculation tests
    python test_with_server.py --timeout 60    # Custom server startup timeout
"""

import sys
import subprocess
import requests
import time
import argparse
import os
import signal
import atexit
from pathlib import Path
from contextlib import contextmanager


class ServerManager:
    """Manages development server lifecycle for testing"""
    
    def __init__(self, host="localhost", port=8000, timeout=30):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{host}:{port}"
        self.server_process = None
        self.original_env = None
        
        # Register cleanup handler
        atexit.register(self.cleanup)
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle signals for clean shutdown"""
        print(f"\n🛑 Received signal {signum}, cleaning up...")
        self.cleanup()
        sys.exit(1)
    
    def check_server_running(self):
        """Check if server is already running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def wait_for_server(self):
        """Wait for server to become ready"""
        print(f"⏳ Waiting for server at {self.base_url}...")
        
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            if self.check_server_running():
                print(f"✅ Server is ready at {self.base_url}")
                return True
            
            time.sleep(1)
            print(".", end="", flush=True)
        
        print(f"\n❌ Server failed to start within {self.timeout} seconds")
        return False
    
    def start_server(self):
        """Start the development server"""
        if self.check_server_running():
            print(f"ℹ️  Server already running at {self.base_url}")
            return True
        
        print("🚀 Starting development server...")
        
        # Prepare environment for dev server
        env = os.environ.copy()
        
        # Change to nocturna-dev environment for server
        if 'CONDA_DEFAULT_ENV' in env:
            self.original_env = env['CONDA_DEFAULT_ENV']
        
        # Start server process
        try:
            cmd = [
                "uvicorn",
                "nocturna_calculations.api.app:app",
                "--host", self.host,
                "--port", str(self.port),
                "--reload",
                "--log-level", "warning"  # Reduce log noise during testing
            ]
            
            print(f"📡 Starting: {' '.join(cmd)}")
            
            # Start server in background
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=Path(__file__).parent.parent.parent  # Project root
            )
            
            # Wait for server to be ready
            if self.wait_for_server():
                print("✅ Server started successfully")
                return True
            else:
                self.cleanup()
                return False
                
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            self.cleanup()
            return False
    
    def stop_server(self):
        """Stop the development server"""
        if self.server_process:
            print("🛑 Stopping development server...")
            try:
                self.server_process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.server_process.wait(timeout=5)
                    print("✅ Server stopped gracefully")
                except subprocess.TimeoutExpired:
                    print("⚠️  Server didn't stop gracefully, forcing...")
                    self.server_process.kill()
                    self.server_process.wait()
                    print("✅ Server stopped forcefully")
                    
            except Exception as e:
                print(f"⚠️  Error stopping server: {e}")
            finally:
                self.server_process = None
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_server()
    
    @contextmanager
    def managed_server(self):
        """Context manager for server lifecycle"""
        try:
            if not self.start_server():
                raise RuntimeError("Failed to start server")
            yield self.base_url
        finally:
            self.cleanup()


def check_test_environment():
    """Check if we're in the right environment for testing"""
    conda_env = os.environ.get('CONDA_DEFAULT_ENV', '')
    
    if conda_env == 'nocturna-test':
        print("✅ Running in nocturna-test environment")
        return True
    
    print(f"⚠️  Current environment: {conda_env or 'base'}")
    print("🧪 Tests should run in nocturna-test environment")
    
    if conda_env in ['nocturna-dev', 'base', '']:
        print("ℹ️  Will attempt to run tests anyway...")
        return True
    
    return False


def run_api_tests(test_filter=None, verbose=False, server_url=None):
    """Run API tests against the server"""
    
    print("🧪 Running API tests against managed server...")
    print("-" * 60)
    
    # Base pytest command - run from project root
    cmd = [
        "python", "-m", "pytest",
        "tests/api/test_live_api.py",
        "-m", "api",
        "--tb=short",
        "--no-cov"  # Disable coverage for integration tests
    ]
    
    # Add verbose flag
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add test filter
    if test_filter:
        if test_filter == "auth":
            cmd.extend(["-k", "test_user_ or test_refresh_ or test_logout or test_unauthorized or test_invalid_token"])
        elif test_filter == "charts":
            cmd.extend(["-k", "test_get_user_charts or test_create_natal or test_get_chart_by_id or test_update_chart or test_delete_chart"])
        elif test_filter == "calculations":
            cmd.extend(["-k", "test_planetary_positions or test_aspects_calculation or test_houses_calculation"])
        elif test_filter == "performance":
            cmd.extend(["-m", "performance"])
    
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)
    
    # Run the tests from project root
    try:
        project_root = Path(__file__).parent.parent.parent  # Go up from scripts/testing/ to project root
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run API tests with automatic server management")
    parser.add_argument("--auth", action="store_true", help="Run only authentication tests")
    parser.add_argument("--charts", action="store_true", help="Run only chart tests")
    parser.add_argument("--calculations", action="store_true", help="Run only calculation tests")
    parser.add_argument("--performance", action="store_true", help="Run only performance tests")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--timeout", type=int, default=30, help="Server startup timeout in seconds")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--host", default="localhost", help="Server host")
    
    args = parser.parse_args()
    
    # Check environment
    if not check_test_environment():
        print("❌ Environment check failed")
        sys.exit(1)
    
    # Determine test filter
    test_filter = None
    if args.auth:
        test_filter = "auth"
    elif args.charts:
        test_filter = "charts"
    elif args.calculations:
        test_filter = "calculations"
    elif args.performance:
        test_filter = "performance"
    
    print("🚀 Nocturna API Test Runner with Managed Server")
    print("=" * 60)
    
    # Create server manager
    server_manager = ServerManager(
        host=args.host,
        port=args.port,
        timeout=args.timeout
    )
    
    try:
        # Run tests with managed server
        with server_manager.managed_server() as server_url:
            success = run_api_tests(
                test_filter=test_filter,
                verbose=args.verbose,
                server_url=server_url
            )
            
            if success:
                print("\n✅ All API tests passed!")
                sys.exit(0)
            else:
                print("\n❌ Some API tests failed!")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 