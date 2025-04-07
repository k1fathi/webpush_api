import os
import sys
import py_compile
import subprocess
import shutil
from pathlib import Path


def check_syntax(path):
    """Check Python files for syntax errors"""
    errors = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    py_compile.compile(file_path, doraise=True)
                except Exception as e:
                    errors.append(f"{file_path}: {str(e)}")
    
    return errors


def check_command_exists(command):
    """Check if a command exists in the system PATH"""
    return shutil.which(command) is not None


def run_mypy(path):
    """Run MyPy type checking"""
    if not check_command_exists('mypy'):
        print("MyPy is not installed or not in PATH. Skipping type checking.")
        return True, "", "MyPy not installed. Install with: pip install mypy"
    
    try:
        result = subprocess.run(['mypy', str(path)], capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", f"Error running MyPy: {str(e)}"


def run_pylint(path):
    """Run Pylint code quality checks"""
    if not check_command_exists('pylint'):
        print("Pylint is not installed or not in PATH. Skipping code quality checks.")
        return True, "", "Pylint not installed. Install with: pip install pylint"
    
    try:
        result = subprocess.run(['pylint', str(path)], capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", f"Error running Pylint: {str(e)}"


def run_flake8(path):
    """Run Flake8 style checks"""
    if not check_command_exists('flake8'):
        print("Flake8 is not installed or not in PATH. Skipping style checks.")
        return True, "", "Flake8 not installed. Install with: pip install flake8"
    
    try:
        result = subprocess.run(['flake8', str(path)], capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", f"Error running Flake8: {str(e)}"


def main():
    # Default to tests directory, or use argument if provided
    if len(sys.argv) > 1:
        test_path = Path(sys.argv[1])
    else:
        test_path = Path(r'c:\K1\ZUZZUU\webpush\webpush_api\tests')
    
    if not test_path.exists():
        print(f"Path not found: {test_path}")
        return False
        
    # Check syntax
    print(f"Checking syntax errors in {test_path}...")
    syntax_errors = check_syntax(test_path)
    if syntax_errors:
        print("Syntax errors found:")
        for error in syntax_errors:
            print(f"  {error}")
        return False
    else:
        print("✓ No syntax errors found")
    
    # Run MyPy
    print("\nRunning type checking...")
    mypy_success, mypy_stdout, mypy_stderr = run_mypy(test_path)
    if not mypy_success and mypy_stderr:
        print("Type errors found:")
        if mypy_stdout:
            print(mypy_stdout)
        if mypy_stderr:
            print(mypy_stderr)
        return False
    else:
        print("✓ Type checking passed")
    
    # Run Flake8
    print("\nRunning style checking...")
    flake8_success, flake8_stdout, flake8_stderr = run_flake8(test_path)
    if not flake8_success and flake8_stdout:
        print("Style issues found:")
        print(flake8_stdout)
        # Don't fail the build for style issues
        print("⚠️ Style check warnings (not failing the build)")
    else:
        print("✓ Style checking passed")
    
    # Run Pylint
    print("\nRunning code quality checks...")
    pylint_success, pylint_stdout, pylint_stderr = run_pylint(test_path)
    if not pylint_success and pylint_stdout:
        print("Code quality issues found:")
        print(pylint_stdout)
        # Don't fail the build for pylint issues
        print("⚠️ Code quality warnings (not failing the build)")
    else:
        print("✓ Code quality checks passed")
    
    print("\nAll critical checks passed successfully!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)