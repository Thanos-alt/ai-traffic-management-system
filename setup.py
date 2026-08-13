"""Setup script for AI Traffic Management System"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Setup project environment"""
    print("Setting up AI Traffic Management System...")
    
    # Create required directories
    dirs = [
        "models",
        "logs",
        "config",
        "src"
    ]
    
    for dir_name in dirs:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)
        print(f"✓ Created directory: {dir_name}")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("✗ Python 3.8+ required")
        return False
    print(f"✓ Python version: {sys.version.split()[0]}")
    
    # Check if requirements can be installed
    print("\nTo complete setup, run:")
    print("  pip install -r requirements.txt")
    print("\nThen start the application with:")
    print("  python main.py")
    
    return True

if __name__ == "__main__":
    success = setup_environment()
    sys.exit(0 if success else 1)
