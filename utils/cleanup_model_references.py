#!/usr/bin/env python
"""
Utility script for cleaning up references to removed model classes.
This script scans Python files in the project and replaces imports
of UserRoleModel and RolePermissionModel with appropriate comments.
"""

import os
import re
from pathlib import Path

# Define the project root directory
PROJECT_ROOT = Path(__file__).parent.parent

def scan_and_replace():
    """
    Scan all Python files in the project and replace imports of
    removed models with appropriate comments.
    """
    count = 0
    pattern1 = r"from models\.domain\.user_role import UserRoleModel"
    pattern2 = r"from models\.domain\.role_permission import RolePermissionModel"
    
    for path in PROJECT_ROOT.rglob("*.py"):
        if "venv" in str(path) or "__pycache__" in str(path):
            continue
            
        content = path.read_text()
        original = content
        
        # Replace imports
        content = re.sub(pattern1, "# UserRoleModel has been removed - using user_role association table instead", content)
        content = re.sub(pattern2, "# RolePermissionModel has been removed - using role_permission association table instead", content)
        
        # Write changes back if modified
        if content != original:
            path.write_text(content)
            count += 1
            print(f"Updated {path}")
    
    print(f"Updated {count} files")

if __name__ == "__main__":
    scan_and_replace()
