#!/usr/bin/env python
"""
Quick verification script to ensure CI/CD fixes are working
"""
import subprocess
import sys

def run_tests():
    """Run pytest to verify everything works"""
    print("🧪 Running test suite...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--tb=no", "-q"],
        cwd="c:\\development\\plant_journal"
    )
    return result.returncode == 0

def check_imports():
    """Verify all dependencies import correctly"""
    print("\n📦 Checking imports...")
    try:
        import django
        import rest_framework
        import gradio
        import pytest
        import factory
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 CI/CD Fix Verification\n")
    
    if check_imports():
        print("\n✅ Dependencies look good!")
        if run_tests():
            print("\n✅ All tests passing!")
            print("\n🎉 CI/CD is ready to go!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed")
            sys.exit(1)
    else:
        print("\n❌ Dependency issues found")
        sys.exit(1)
