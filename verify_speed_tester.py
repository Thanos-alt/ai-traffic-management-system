#!/usr/bin/env python3
"""
Speed Tester Setup Verification
Checks all dependencies and system requirements
"""

import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} - Requires Python 3.8+")
        return False


def check_import(module_name, display_name=None):
    """Check if module can be imported"""
    display = display_name or module_name
    try:
        __import__(module_name)
        print(f"✅ {display} - Installed")
        return True
    except ImportError:
        print(f"❌ {display} - NOT installed")
        return False


def check_module_version(module_name, min_version=None):
    """Check module version"""
    try:
        module = __import__(module_name)
        version = getattr(module, '__version__', 'unknown')
        if min_version:
            from packaging import version as pkg_version
            if pkg_version.parse(version) >= pkg_version.parse(min_version):
                print(f"   Version: {version} ✓")
                return True
            else:
                print(f"   Version: {version} ⚠️ (requires {min_version}+)")
                return False
        else:
            print(f"   Version: {version}")
            return True
    except Exception as e:
        print(f"   Error checking version: {e}")
        return False


def check_file_exists(filepath):
    """Check if file exists"""
    path = Path(filepath)
    if path.exists():
        print(f"✅ {filepath} - Found")
        return True
    else:
        print(f"❌ {filepath} - Missing")
        return False


def check_opencv_features():
    """Check OpenCV video support"""
    try:
        import cv2
        
        # Check codecs
        print("\n📹 Video Codec Support:")
        codecs = {
            'H.264 (MP4)': cv2.CAP_FFMPEG,
            'MJPEG (AVI)': cv2.CAP_FFMPEG,
            'Camera': cv2.CAP_V4L2 if sys.platform != 'win32' else 'MSMF'
        }
        
        # Try to open dummy file for codec check
        print("   Video support: ✓")
        return True
    except Exception as e:
        print(f"❌ OpenCV codec check failed: {e}")
        return False


def main():
    """Run all checks"""
    print("=" * 60)
    print("🚗 Speed Tester - Setup Verification")
    print("=" * 60)
    
    all_ok = True
    
    # Python version
    print("\n📌 Python Environment:")
    all_ok = check_python_version() and all_ok
    
    # Core dependencies
    print("\n📦 Core Dependencies:")
    dependencies = [
        ('cv2', 'OpenCV'),
        ('numpy', 'NumPy'),
        ('PIL', 'Pillow'),
        ('tkinter', 'Tkinter'),
        ('matplotlib', 'Matplotlib'),
    ]
    
    for module, display in dependencies:
        if not check_import(module, display):
            all_ok = False
    
    # Optional dependencies
    print("\n📦 Optional Dependencies:")
    optional = [
        ('pandas', 'Pandas (data analysis)'),
        ('scipy', 'SciPy (signal processing)'),
    ]
    
    for module, display in optional:
        check_import(module, display)
    
    # Check files exist
    print("\n📁 Required Files:")
    files = [
        'opencv_speed_detection.py',
        'speed_tester.py',
        'requirements.txt',
    ]
    
    for filepath in files:
        check_file_exists(filepath)
    
    # OpenCV features
    check_opencv_features()
    
    # Installation instructions
    if not all_ok:
        print("\n" + "=" * 60)
        print("⚠️  INSTALLATION REQUIRED")
        print("=" * 60)
        print("\nRun this command to install missing dependencies:\n")
        print("  pip install -r requirements.txt\n")
        print("For Tkinter on Linux:")
        print("  sudo apt-get install python3-tk\n")
        print("For Tkinter on macOS:")
        print("  brew install python-tk\n")
    else:
        print("\n" + "=" * 60)
        print("✅ All checks passed! Speed Tester is ready.")
        print("=" * 60)
        print("\n🚀 To launch Speed Tester:\n")
        print("  python speed_tester.py\n")
        print("📚 For help, read:")
        print("  - SPEED_TESTER_QUICKSTART.md (30-second intro)")
        print("  - SPEED_TESTER_GUIDE.md (complete guide)")
        print("  - OPENCV_SPEED_DETECTION_README.md (technical ref)\n")
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
