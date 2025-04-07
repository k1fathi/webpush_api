#!/usr/bin/env python3
"""
Setup development environment for the WebPush API project
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(command):
    """Run a command and print output"""
    print(f"Executing: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    
    print(result.stdout)
    return True

def setup_dev_environment():
    """Install development dependencies and set up pre-commit hooks"""
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    
    # Install development dependencies
    req_dev_file = project_root / "requirements-dev.txt"
    if not req_dev_file.exists():
        print(f"Error: {req_dev_file} not found!")
        return False
    
    # Install development dependencies
    print("Installing development dependencies...")
    if not run_command([sys.executable, "-m", "pip", "install", "-r", str(req_dev_file)]):
        return False
    
    print("\nDevelopment environment set up successfully!")
    print("\nYou can now run the following commands:")
    print("  - python -m tools.pretest           # Run pre-test checks")
    print("  - pytest                            # Run tests")
    print("  - python -m black .                 # Format code")
    print("  - python -m isort .                 # Sort imports")
    
    return True

if __name__ == "__main__":
    success = setup_dev_environment()
    sys.exit(0 if success else 1)
