#!/usr/bin/env python3
"""
USB Auto Recovery Printer Test
==============================

Test script for the enhanced USB printer with automatic error recovery.
Tests various error scenarios and recovery mechanisms.
"""

import logging
import time
import asyncio
from usb_auto_recovery_printer import USBAutoRecoveryPrinter, send_zpl_with_auto_recovery

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_basic_functionality():
    """Test basic printer functionality"""
    print("\n" + "="*60)
    print("🧪 BASIC FUNCTIONALITY TEST")
    print("="*60)
    
    printer = USBAutoRecoveryPrinter(auto_detect=True, max_recovery_attempts=3)
    
    try:
        # Connect
        print("1. Connecting to printer...")
        if not printer.connect():
            print("❌ Failed to connect to printer")
            return False
        
        print("✅ Connected successfully")
        
        # Get printer info
        info = printer.get_printer_info()
        print(f"📱 Printer Info: {info}")
        
        # Test ZPL command
        test_zpl = "^XA^FO50,50^A0N,50,50^FDBasic Test^FS^XZ"
        print("2. Sending test label...")
        
        if printer.send_zpl_command(test_zpl):
            print("✅ Test label sent successfully")
        else:
            print("❌ Failed to send test label")
            return False
        
        # Show error stats
        stats = printer.get_error_stats()
        print(f"📊 Error Stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        printer.disconnect()


def test_multiple_prints():
    """Test multiple consecutive prints"""
    print("\n" + "="*60)
    print("🔄 MULTIPLE PRINTS TEST")
    print("="*60)
    
    printer = USBAutoRecoveryPrinter(auto_detect=True, max_recovery_attempts=3)
    
    try:
        if not printer.connect():
            print("❌ Failed to connect to printer")
            return False
        
        print("✅ Connected successfully")
        
        # Test multiple prints
        for i in range(5):
            print(f"\n📄 Print {i+1}/5...")
            
            test_zpl = f"^XA^FO50,50^A0N,50,50^FDPrint #{i+1}^FS^FO50,120^A0N,30,30^FD{time.strftime('%H:%M:%S')}^FS^XZ"
            
            if printer.send_zpl_command(test_zpl):
                print(f"✅ Print {i+1} sent successfully")
            else:
                print(f"❌ Print {i+1} failed")
                
            # Show stats after each print
            stats = printer.get_error_stats()
            print(f"📊 Current Stats: Errors: {stats['total_errors']}, Recoveries: {stats['total_recovery_attempts']}")
            
            # Wait between prints
            time.sleep(1)
        
        # Final stats
        final_stats = printer.get_error_stats()
        print(f"\n📊 Final Stats: {final_stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        printer.disconnect()


def test_convenience_function():
    """Test the convenience function"""
    print("\n" + "="*60)
    print("🎯 CONVENIENCE FUNCTION TEST")
    print("="*60)
    
    test_zpl = "^XA^FO50,50^A0N,50,50^FDConvenience Test^FS^XZ"
    
    print("Testing send_zpl_with_auto_recovery function...")
    
    if send_zpl_with_auto_recovery(test_zpl, max_attempts=3):
        print("✅ Convenience function test successful")
        return True
    else:
        print("❌ Convenience function test failed")
        return False


def test_error_stats_reset():
    """Test error statistics reset"""
    print("\n" + "="*60)
    print("🔄 ERROR STATS RESET TEST")
    print("="*60)
    
    printer = USBAutoRecoveryPrinter(auto_detect=True, max_recovery_attempts=3)
    
    try:
        if not printer.connect():
            print("❌ Failed to connect to printer")
            return False
        
        # Generate some activity
        for i in range(3):
            test_zpl = f"^XA^FO50,50^A0N,50,50^FDReset Test {i+1}^FS^XZ"
            printer.send_zpl_command(test_zpl)
            time.sleep(0.5)
        
        # Check stats before reset
        stats_before = printer.get_error_stats()
        print(f"📊 Stats before reset: {stats_before}")
        
        # Reset stats
        printer.reset_error_history()
        
        # Check stats after reset
        stats_after = printer.get_error_stats()
        print(f"📊 Stats after reset: {stats_after}")
        
        if stats_after['total_errors'] == 0 and stats_after['total_recovery_attempts'] == 0:
            print("✅ Error stats reset successful")
            return True
        else:
            print("❌ Error stats reset failed")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        printer.disconnect()


def run_all_tests():
    """Run all tests"""
    print("🚀 USB AUTO RECOVERY PRINTER TESTS")
    print("=" * 60)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Multiple Prints", test_multiple_prints),
        ("Convenience Function", test_convenience_function),
        ("Error Stats Reset", test_error_stats_reset)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
        
        time.sleep(2)  # Wait between tests
    
    # Summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nTotal: {len(results)} tests, {passed} passed, {len(results) - passed} failed")
    
    if passed == len(results):
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️ Some tests failed!")
        return False


if __name__ == "__main__":
    import sys
    
    print("🖨️ USB Auto Recovery Printer Test Suite")
    print("=" * 60)
    
    # Check if USB is available
    try:
        import usb.core
        import usb.util
        from usb_auto_recovery_printer import USBAutoRecoveryPrinter
        print("✅ PyUSB and auto-recovery printer available")
    except ImportError as e:
        print(f"❌ Required dependencies not available: {e}")
        print("Install with: pip install pyusb")
        sys.exit(1)
    
    # Check for available printers
    print("🔍 Checking for available USB printers...")
    printer = USBAutoRecoveryPrinter(auto_detect=True)
    
    try:
        if printer.connect():
            info = printer.get_printer_info()
            print(f"✅ Found printer: {info}")
            printer.disconnect()
        else:
            print("❌ No USB printers found")
            print("Please ensure a supported USB printer is connected")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error checking printers: {e}")
        sys.exit(1)
    
    # Run tests
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        
        if test_name == "basic":
            test_basic_functionality()
        elif test_name == "multiple":
            test_multiple_prints()
        elif test_name == "convenience":
            test_convenience_function()
        elif test_name == "reset":
            test_error_stats_reset()
        else:
            print(f"Unknown test: {test_name}")
            print("Available tests: basic, multiple, convenience, reset")
    else:
        # Run all tests
        success = run_all_tests()
        sys.exit(0 if success else 1)
