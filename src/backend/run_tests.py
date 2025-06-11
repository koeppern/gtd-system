#!/usr/bin/env python3
"""
Test runner for GTD Backend
"""
import sys
import os
import subprocess
import asyncio

# Add current directory to Python path for relative imports
current_dir = os.path.dirname(__file__)
sys.path.insert(0, current_dir)

def run_tests():
    """Run all tests with pytest."""
    print("🧪 Running GTD Backend Test Suite")
    print("=" * 50)
    
    # Basic pytest command
    pytest_args = [
        "python", "-m", "pytest",
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--strict-markers",  # Strict marker checking
        "tests/",  # Test directory
    ]
    
    # Add coverage if available
    try:
        import pytest_cov
        pytest_args.extend([
            "--cov=app",  # Coverage for app directory
            "--cov-report=term-missing",  # Show missing lines
            "--cov-report=html:htmlcov",  # Generate HTML report
        ])
        print("📊 Coverage reporting enabled")
    except ImportError:
        print("ℹ️  Coverage reporting not available (install pytest-cov for coverage)")
    
    print(f"🚀 Running: {' '.join(pytest_args)}")
    print()
    
    # Run tests
    try:
        result = subprocess.run(pytest_args, check=True)
        print()
        print("✅ All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print()
        print(f"❌ Tests failed with exit code {e.returncode}")
        return False
    except KeyboardInterrupt:
        print()
        print("⚠️  Tests interrupted by user")
        return False

def run_quick_tests():
    """Run quick tests (skip slow integration tests)."""
    print("⚡ Running Quick Test Suite")
    print("=" * 50)
    
    pytest_args = [
        "python", "-m", "pytest",
        "-v",
        "--tb=short",
        "-m", "not slow",  # Skip slow tests
        "tests/",
    ]
    
    print(f"🚀 Running: {' '.join(pytest_args)}")
    print()
    
    try:
        result = subprocess.run(pytest_args, check=True)
        print()
        print("✅ Quick tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print()
        print(f"❌ Quick tests failed with exit code {e.returncode}")
        return False

def check_test_setup():
    """Check if test environment is properly set up."""
    print("🔍 Checking test environment...")
    
    required_modules = [
        "pytest",
        "pytest_asyncio",
        "fastapi",
        "sqlalchemy",
        "pydantic",
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} (missing)")
            missing_modules.append(module)
    
    if missing_modules:
        print()
        print("❌ Missing required modules for testing:")
        for module in missing_modules:
            print(f"   - {module}")
        print()
        print("Install missing modules with:")
        print("pip install pytest pytest-asyncio pytest-cov")
        return False
    
    print()
    print("✅ Test environment is ready!")
    return True

def main():
    """Main test runner."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "check":
            success = check_test_setup()
        elif command == "quick":
            if check_test_setup():
                success = run_quick_tests()
            else:
                success = False
        elif command == "full":
            if check_test_setup():
                success = run_tests()
            else:
                success = False
        else:
            print(f"Unknown command: {command}")
            print("Available commands: check, quick, full")
            success = False
    else:
        # Default: run quick check then full tests
        if check_test_setup():
            success = run_tests()
        else:
            success = False
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()