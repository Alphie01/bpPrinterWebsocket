#!/usr/bin/env python3
"""
.env Test Script
================

Test script to verify that all modules correctly load SERVER_URL from .env file.
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_env_loading():
    """Test .env loading in all modules"""
    print("Testing .env file loading...")
    print("=" * 50)
    
    # Test 1: Direct .env loading
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✓ python-dotenv successfully loaded")
    except ImportError:
        print("✗ python-dotenv not available")
        print("  Install with: pip install python-dotenv")
        return False
    
    # Test 2: Check SERVER_URL in .env
    server_url = os.getenv('SERVER_URL')
    if server_url:
        print(f"✓ SERVER_URL found in environment: {server_url}")
    else:
        print("✗ SERVER_URL not found in environment")
        print("  Make sure .env file exists and contains SERVER_URL=...")
    
    # Test 3: Test config module
    try:
        from config import ServerConfig
        config = ServerConfig.from_env()
        print(f"✓ config.py ServerConfig: {config.url}")
    except Exception as e:
        print(f"✗ config.py error: {e}")
    
    # Test 4: Test USB printer client module
    try:
        # Just test the import and .env loading part
        from usb_printer_client import os as client_os
        print("✓ usb_printer_client.py imported successfully")
    except Exception as e:
        print(f"✗ usb_printer_client.py error: {e}")
    
    # Test 5: Show all environment variables starting with SERVER, PRINTER, USB
    print("\\nEnvironment variables:")
    print("-" * 30)
    for key, value in os.environ.items():
        if key.startswith(('SERVER', 'PRINTER', 'USB', 'LOG')):
            print(f"{key}={value}")
    
    print("\\nTest completed!")
    return True

if __name__ == "__main__":
    test_env_loading()
