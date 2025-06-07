#!/usr/bin/env python3
"""
API Test Runner

This script runs the live API integration tests against a running server.
Make sure your server is running on localhost:8000 before running this script.

Usage:
    python run_api_tests.py                    # Run all API tests
    python run_api_tests.py --auth             # Run only auth tests
    python run_api_tests.py --charts           # Run only chart tests
    python run_api_tests.py --calculations     # Run only calculation tests
    python run_api_tests.py --performance      # Run performance tests
    python run_api_tests.py --verbose          # Run with verbose output
"""

import sys
import subprocess
import requests
import time
import argparse
import os
from pathlib import Path


def check_test_environment():
    """Check if the nocturna-test environment is active"""
    conda_env = os.environ.get('CONDA_DEFAULT_ENV', '')
    
    if conda_env == 'nocturna-test':
        print("✅ Running in nocturna-test environment")
        return True
    
    print(f"⚠️  Current environment: {conda_env or 'base'}")
    print("🧪 API tests should run in the nocturna-test environment")
    print()
    print("To set up and activate the test environment:")
    print("  make setup-test")
    print("  conda activate nocturna-test")
    print()
    
    if conda_env == 'nocturna-dev':
        print("ℹ️  You're in the dev environment. Tests might work but test env is recommended.")
        response = input("Continue anyway? [y/N]: ")
        return response.lower() in ['y', 'yes']
    else:
        print("❌ Please activate nocturna-test environment first")
        return False


def check_server_running(base_url="http://localhost:8000"):
    """Check if the API server is running"""
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Server is running at {base_url}")
            return True
    except requests.exceptions.RequestException:
        pass
    
    print(f"❌ Server is not running at {base_url}")
    print("Please start the server first:")
    print("  conda activate nocturna-dev")
    print("  make dev")
    print()
    print("Then run tests in a separate terminal:")
    print("  conda activate nocturna-test")
    print("  python run_api_tests.py")
    return False


def run_tests(test_filter=None, verbose=False, skip_env_check=False):
    """Run the API tests with specified filter"""
    
    if not skip_env_check and not check_test_environment():
        return False
    
    if not check_server_running():
        return False
    
    # Base pytest command - avoid problematic config by using minimal options
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
    
    print(f"🧪 Running API tests...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)
    
    # Run the tests
    try:
        # Change to project root directory (two levels up from scripts/testing/)
        project_root = Path(__file__).parent.parent.parent
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
    parser = argparse.ArgumentParser(description="Run API integration tests")
    parser.add_argument("--auth", action="store_true", help="Run only authentication tests")
    parser.add_argument("--charts", action="store_true", help="Run only chart tests")
    parser.add_argument("--calculations", action="store_true", help="Run only calculation tests")
    parser.add_argument("--performance", action="store_true", help="Run only performance tests")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--skip-env-check", action="store_true", help="Skip environment check (for make targets)")
    
    args = parser.parse_args()
    
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
    
    print("🚀 Nocturna API Test Runner")
    print("=" * 60)
    
    success = run_tests(test_filter=test_filter, verbose=args.verbose, skip_env_check=args.skip_env_check)
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 