"""
Entry point for the FastAPI application when run through Docker.
This file serves as a bridge to the actual application in the main.py file in the root directory.
"""
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path to import the main app
parent_dir = str(Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from main import app  # Import the app from the main.py file

# The application is now available as 'app' for uvicorn to use