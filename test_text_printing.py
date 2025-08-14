#!/usr/bin/env python3
"""
Test Text Printing
==================
"""

import subprocess
import os

def test_text_printing():
    """Test text file printing on macOS"""
    print("📝 Text Printing Test")
    print("=" * 50)
    
    # Test text file
    txt_file = "test_output/dual_summary_PLT2025005_20250814_110924.txt"
    
    if not os.path.exists(txt_file):
        print(f"❌ Test text file not found: {txt_file}")
        return
    
    print(f"📄 Test file: {txt_file}")
    print()
    
    # Show file content (first few lines)
    print("📋 File content (first 10 lines):")
    print("-" * 40)
    try:
        with open(txt_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:10]):
                print(f"{i+1:2d}: {line.rstrip()}")
        print(f"... (total {len(lines)} lines)")
    except Exception as e:
        print(f"Error reading file: {e}")
    print("-" * 40)
    print()
    
    # Test lpr with text file
    print("🖨️  Testing lpr with text file:")
    try:
        cmd = ["lpr", txt_file]
        print(f"Command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"Return code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Text file sent to printer successfully!")
        else:
            print(f"❌ Error: {result.stderr}")
            
        if result.stdout:
            print(f"STDOUT: {result.stdout}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_text_printing()
