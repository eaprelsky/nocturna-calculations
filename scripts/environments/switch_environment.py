#!/usr/bin/env python3
"""
Environment switching utility for Nocturna Calculations project.

This script helps switch between different conda environments (dev, test, prod)
and validates the switch was successful.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(command, check=True, capture_output=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            capture_output=capture_output,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Exit code: {e.returncode}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return None


def get_current_environment():
    """Get the currently active conda environment."""
    result = run_command("conda info --json")
    if result and result.returncode == 0:
        import json
        info = json.loads(result.stdout)
        active_env = info.get("active_prefix", "")
        if active_env:
            return os.path.basename(active_env)
    return None


def list_environments():
    """List all available conda environments."""
    result = run_command("conda env list")
    if result and result.returncode == 0:
        environments = []
        for line in result.stdout.splitlines():
            if line and not line.startswith("#"):
                parts = line.split()
                if parts:
                    env_name = parts[0]
                    if env_name.startswith("nocturna-"):
                        environments.append(env_name)
        return environments
    return []


def environment_exists(env_name):
    """Check if a conda environment exists."""
    full_env_name = f"nocturna-{env_name}" if not env_name.startswith("nocturna-") else env_name
    environments = list_environments()
    return full_env_name in environments


def validate_environment(env_name):
    """Validate that an environment is properly configured."""
    full_env_name = f"nocturna-{env_name}" if not env_name.startswith("nocturna-") else env_name
    
    print(f"Validating environment: {full_env_name}")
    
    # Check if environment exists
    if not environment_exists(env_name):
        print(f"❌ Environment {full_env_name} does not exist")
        return False
    
    # Activate environment and check Python version
    activate_cmd = f"conda activate {full_env_name} && python --version"
    result = run_command(activate_cmd)
    
    if result and result.returncode == 0:
        python_version = result.stdout.strip()
        print(f"✅ Python version: {python_version}")
        
        # Check expected Python version based on environment
        if env_name in ["dev", "development"]:
            expected = "3.11"
        elif env_name in ["test", "testing"]:
            expected = "3.9"
        elif env_name in ["prod", "production"]:
            expected = "3.11"
        else:
            expected = None
        
        if expected and expected in python_version:
            print(f"✅ Python version matches expected ({expected})")
        elif expected:
            print(f"⚠️  Python version {python_version} doesn't match expected {expected}")
        
        return True
    else:
        print(f"❌ Failed to activate environment {full_env_name}")
        return False


def switch_environment(env_name):
    """Switch to the specified environment."""
    # Map short names to full names
    env_mapping = {
        "dev": "nocturna-dev",
        "development": "nocturna-dev", 
        "test": "nocturna-test",
        "testing": "nocturna-test",
        "prod": "nocturna-prod",
        "production": "nocturna-prod"
    }
    
    full_env_name = env_mapping.get(env_name, env_name)
    
    # Ensure it starts with nocturna-
    if not full_env_name.startswith("nocturna-"):
        full_env_name = f"nocturna-{full_env_name}"
    
    print(f"Switching to environment: {full_env_name}")
    
    # Check if environment exists
    if not environment_exists(full_env_name):
        print(f"❌ Environment {full_env_name} does not exist")
        print("Available environments:")
        for env in list_environments():
            print(f"  - {env}")
        
        # Offer to create environment
        env_type = full_env_name.replace("nocturna-", "")
        env_file = f"environments/{env_type}.yml"
        if Path(env_file).exists():
            create = input(f"Would you like to create {full_env_name} from {env_file}? (y/N): ")
            if create.lower() in ['y', 'yes']:
                print(f"Creating environment from {env_file}...")
                result = run_command(f"conda env create -f {env_file}")
                if result and result.returncode == 0:
                    print(f"✅ Environment {full_env_name} created successfully")
                else:
                    print(f"❌ Failed to create environment {full_env_name}")
                    return False
            else:
                return False
        else:
            print(f"❌ Environment file {env_file} not found")
            return False
    
    # Get current environment
    current_env = get_current_environment()
    if current_env == full_env_name:
        print(f"✅ Already in environment {full_env_name}")
        return True
    
    # Switch environment
    print(f"Switching from {current_env or 'base'} to {full_env_name}")
    
    # Provide instructions since we can't directly activate in parent shell
    print("\n" + "="*60)
    print("ENVIRONMENT SWITCH INSTRUCTIONS")
    print("="*60)
    print(f"Run the following command to activate the environment:")
    print(f"\n    conda activate {full_env_name}\n")
    
    if current_env and current_env != "base":
        print("Or if you prefer, first deactivate current environment:")
        print(f"    conda deactivate")
        print(f"    conda activate {full_env_name}")
    
    print("="*60)
    
    # Validate the target environment
    return validate_environment(full_env_name)


def show_environment_info():
    """Show information about all available environments."""
    print("Nocturna Calculations - Environment Information")
    print("=" * 50)
    
    current_env = get_current_environment()
    print(f"Current environment: {current_env or 'base'}")
    print()
    
    environments = list_environments()
    if environments:
        print("Available Nocturna environments:")
        for env in environments:
            status = "✅ (active)" if env == current_env else "  "
            
            # Show purpose
            if "dev" in env:
                purpose = "Development work, debugging, feature development"
            elif "test" in env:
                purpose = "Testing, benchmarking, compatibility testing"
            elif "prod" in env:
                purpose = "Production deployment, minimal dependencies"
            else:
                purpose = "Unknown purpose"
            
            print(f"{status} {env}")
            print(f"    Purpose: {purpose}")
            print()
    else:
        print("No Nocturna environments found")
        print("Run 'make setup-dev' or 'make setup-test' to create environments")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Switch between Nocturna Calculations conda environments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --env dev          # Switch to development environment
  %(prog)s --env test         # Switch to testing environment  
  %(prog)s --env prod         # Switch to production environment
  %(prog)s --list             # List available environments
  %(prog)s --validate dev     # Validate development environment
        """
    )
    
    parser.add_argument(
        "--env", "-e",
        help="Environment to switch to (dev/test/prod)",
        choices=["dev", "development", "test", "testing", "prod", "production"]
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available environments"
    )
    
    parser.add_argument(
        "--validate", "-v",
        help="Validate specified environment"
    )
    
    parser.add_argument(
        "--current", "-c",
        action="store_true",
        help="Show current environment"
    )
    
    args = parser.parse_args()
    
    # If no arguments provided, show environment info
    if not any([args.env, args.list, args.validate, args.current]):
        show_environment_info()
        return
    
    # Show current environment
    if args.current:
        current = get_current_environment()
        print(f"Current environment: {current or 'base'}")
        return
    
    # List environments
    if args.list:
        show_environment_info()
        return
    
    # Validate environment
    if args.validate:
        success = validate_environment(args.validate)
        sys.exit(0 if success else 1)
    
    # Switch environment
    if args.env:
        success = switch_environment(args.env)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 