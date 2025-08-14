#!/usr/bin/env python3
"""
Test Platform Detection and Printing
====================================
"""

import platform
import subprocess
import os

def test_platform_detection():
    """Test platform detection"""
    print("🖥️  Platform Detection Test")
    print("=" * 50)
    
    system = platform.system()
    print(f"Platform: {system}")
    print(f"Platform detailed: {platform.platform()}")
    print(f"Machine: {platform.machine()}")
    print(f"Node: {platform.node()}")
    print()
    
    # Test HTML file path
    html_file = "test_output/dual_summary_PLT2025005_20250814_110924.html"
    
    if not os.path.exists(html_file):
        print(f"❌ Test HTML file not found: {html_file}")
        return
    
    print(f"📄 Test file: {html_file}")
    print()
    
    if system == "Darwin":  # macOS
        print("🍎 macOS detected - Testing print commands")
        
        # Test 1: Check available printers
        print("\n1️⃣ Available printers:")
        try:
            result = subprocess.run(["lpstat", "-p"], capture_output=True, text=True)
            if result.returncode == 0:
                print(result.stdout)
            else:
                print("No printers found with lpstat")
        except Exception as e:
            print(f"Error checking printers: {e}")
        
        # Test 2: Check default printer
        print("\n2️⃣ Default printer:")
        try:
            result = subprocess.run(["lpstat", "-d"], capture_output=True, text=True)
            if result.returncode == 0:
                print(result.stdout)
            else:
                print("No default printer set")
        except Exception as e:
            print(f"Error checking default printer: {e}")
        
        # Test 3: Try lpr command
        print("\n3️⃣ Testing lpr command:")
        try:
            # First try with default printer
            cmd = ["lpr", html_file]
            print(f"Command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(f"Return code: {result.returncode}")
            if result.stdout:
                print(f"STDOUT: {result.stdout}")
            if result.stderr:
                print(f"STDERR: {result.stderr}")
        except Exception as e:
            print(f"Error with lpr: {e}")
        
        # Test 4: Open with Safari
        print("\n4️⃣ Testing Safari open:")
        try:
            cmd = ["open", "-a", "Safari", html_file]
            print(f"Command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(f"Return code: {result.returncode}")
            if result.stdout:
                print(f"STDOUT: {result.stdout}")
            if result.stderr:
                print(f"STDERR: {result.stderr}")
        except Exception as e:
            print(f"Error with Safari: {e}")
    
    else:
        print(f"ℹ️  Platform {system} - Limited testing")

if __name__ == "__main__":
    test_platform_detection()
