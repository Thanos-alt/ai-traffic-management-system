"""Verify installation and environment"""

import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor} (requires 3.8+)")
        return False

def check_package(package_name):
    """Check if package is installed"""
    try:
        __import__(package_name)
        print(f"✓ {package_name}")
        return True
    except ImportError:
        print(f"✗ {package_name} (not installed)")
        return False

def check_directories():
    """Check required directories"""
    dirs = ["config", "src", "models", "logs"]
    all_exist = True
    
    for dir_name in dirs:
        if Path(dir_name).exists():
            print(f"✓ {dir_name}/ directory exists")
        else:
            print(f"✗ {dir_name}/ directory missing")
            all_exist = False
    
    return all_exist

def check_files():
    """Check required files"""
    files = [
        "main.py",
        "requirements.txt",
        "config/config.py",
        "src/traffic_detector.py",
        "src/camera_handler.py",
        "src/voice_alert.py",
    ]
    all_exist = True
    
    for filename in files:
        if Path(filename).exists():
            print(f"✓ {filename}")
        else:
            print(f"✗ {filename} missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all checks"""
    print("=" * 50)
    print("AI Traffic Management System - Verification")
    print("=" * 50)
    
    print("\n[1] Python Version Check")
    py_ok = check_python_version()
    
    print("\n[2] Required Packages")
    packages = ["cv2", "ultralytics", "numpy", "pyttsx3"]
    pkg_ok = all(check_package(pkg) for pkg in packages)
    
    print("\n[3] Directory Structure")
    dir_ok = check_directories()
    
    print("\n[4] Required Files")
    file_ok = check_files()
    
    print("\n" + "=" * 50)
    if py_ok and dir_ok and file_ok:
        if pkg_ok:
            print("✓ All checks passed! Ready to run.")
            print("\nStart with: python main.py")
        else:
            print("⚠ Missing packages. Run:")
            print("  pip install -r requirements.txt")
    else:
        print("✗ Some checks failed. Please fix issues above.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
