import os
import sys
import py_compile
import subprocess
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

def run_mypy(path):
    """Run MyPy type checking"""
    result = subprocess.run(['mypy', path], capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def run_pylint(path):
    """Run Pylint code quality checks"""
    result = subprocess.run(['pylint', path], capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def main():
    test_path = Path(r'c:\K1\ZUZZUU\webpush\webpush_api\tests')
    
    # Check syntax
    print("Checking syntax errors...")
    syntax_errors = check_syntax(test_path)
    if syntax_errors:
        print("Syntax errors found:")
        for error in syntax_errors:
            print(f"  {error}")
        return False
    
    # Run MyPy
    print("\nRunning type checking...")
    mypy_success, mypy_stdout, mypy_stderr = run_mypy(test_path)
    if not mypy_success:
        print("Type errors found:")
        print(mypy_stdout)
        print(mypy_stderr)
        return False
    
    # Run Pylint
    print("\nRunning code quality checks...")
    pylint_# filepath: c:\K1\ZUZZUU\webpush\webpush_api\tools\pretest.py
import os
import sys
import py_compile
import subprocess
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

def run_mypy(path):
    """Run MyPy type checking"""
    result = subprocess.run(['mypy', path], capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def run_pylint(path):
    """Run Pylint code quality checks"""
    result = subprocess.run(['pylint', path], capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def main():
    test_path = Path(r'c:\K1\ZUZZUU\webpush\webpush_api\tests')
    
    # Check syntax
    print("Checking syntax errors...")
    syntax_errors = check_syntax(test_path)
    if syntax_errors:
        print("Syntax errors found:")
        for error in syntax_errors:
            print(f"  {error}")
        return False
    
    # Run MyPy
    print("\nRunning type checking...")
    mypy_success, mypy_stdout, mypy_stderr = run_mypy(test_path)
    if not mypy_success:
        print("Type errors found:")
        print(mypy_stdout)
        print(mypy_stderr)
        return False
    
    # Run Pylint
    print("\nRunning code quality checks...")
    pylint_