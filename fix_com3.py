#!/usr/bin/env python3
"""
Quick Fix for COM3 Port Issues
==============================

This script provides a quick solution for the most common COM3 port access issues
encountered with the WebSocket Printer Client.

Usage:
    python fix_com3.py
"""

import logging
import platform
import subprocess
import sys
import time
from typing import List

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("ERROR: PySerial not available. Install with: pip install pyserial")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_if_port_exists(port: str) -> bool:
    """Check if the specified port exists in the system"""
    ports = list(serial.tools.list_ports.comports())
    return any(p.device.upper() == port.upper() for p in ports)


def get_port_description(port: str) -> str:
    """Get the description of a specific port"""
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if p.device.upper() == port.upper():
            return p.description
    return "Port not found"


def quick_port_release(port: str) -> bool:
    """Quick attempt to release a stuck port"""
    logger.info(f"Attempting quick release of {port}...")
    
    try:
        # Multiple quick open/close cycles with different timings
        for cycle in range(3):
            for timeout in [0.1, 0.2, 0.5]:
                try:
                    ser = serial.Serial(port, 9600, timeout=timeout)
                    time.sleep(0.1)
                    ser.close()
                    time.sleep(0.1)
                except Exception:
                    pass
        
        # Try different baud rates
        for baud in [9600, 19200, 38400, 115200]:
            try:
                ser = serial.Serial(port, baud, timeout=0.1)
                time.sleep(0.05)
                ser.close()
                time.sleep(0.05)
            except Exception:
                pass
        
        # Final test
        time.sleep(1.0)
        with serial.Serial(port, 9600, timeout=0.1) as ser:
            if ser.is_open:
                logger.info(f"✅ Successfully released {port}")
                return True
                
    except Exception as e:
        logger.debug(f"Release attempt failed: {e}")
    
    logger.warning(f"❌ Could not release {port} automatically")
    return False


def find_alternative_ports() -> List[str]:
    """Find alternative working COM ports"""
    logger.info("Searching for alternative working ports...")
    
    working_ports = []
    ports = list(serial.tools.list_ports.comports())
    
    for port in ports:
        try:
            with serial.Serial(port.device, 9600, timeout=0.1) as ser:
                if ser.is_open:
                    working_ports.append(port.device)
                    logger.info(f"✅ Found working port: {port.device} ({port.description})")
        except Exception:
            logger.debug(f"❌ Port {port.device} not accessible")
    
    return working_ports


def show_manual_solutions():
    """Show manual solutions for COM3 issues"""
    logger.info("=" * 60)
    logger.info("🔧 MANUAL SOLUTIONS FOR COM3 ACCESS ISSUES")
    logger.info("=" * 60)
    
    logger.info("1. CLOSE OTHER APPLICATIONS:")
    logger.info("   • Close Arduino IDE")
    logger.info("   • Close PuTTY, HyperTerminal, or other terminal programs")
    logger.info("   • Close ZebraLink, Zebra Setup Utilities")
    logger.info("   • Close any printer configuration software")
    logger.info("   • Close Windows Print Spooler (if safe to do so)")
    logger.info("")
    
    logger.info("2. WINDOWS DEVICE MANAGER:")
    logger.info("   • Press Win+X and select 'Device Manager'")
    logger.info("   • Expand 'Ports (COM & LPT)'")
    logger.info("   • Find your COM3 port")
    logger.info("   • Right-click → 'Disable device'")
    logger.info("   • Wait 5 seconds")
    logger.info("   • Right-click → 'Enable device'")
    logger.info("")
    
    logger.info("3. PHYSICAL RECONNECTION:")
    logger.info("   • Unplug the USB cable from the printer")
    logger.info("   • Wait 10 seconds")
    logger.info("   • Plug it back in")
    logger.info("   • Try a different USB port on your computer")
    logger.info("")
    
    logger.info("4. RESTART WINDOWS SERVICES:")
    logger.info("   • Press Win+R, type 'services.msc'")
    logger.info("   • Find 'Print Spooler' service")
    logger.info("   • Right-click → 'Restart'")
    logger.info("   • Find 'Plug and Play' service")
    logger.info("   • Right-click → 'Restart'")
    logger.info("")
    
    logger.info("5. USE ALTERNATIVE CONNECTION:")
    logger.info("   • Set environment variable: set CONNECTION_TYPE=usb")
    logger.info("   • Or try a different COM port if available")
    logger.info("")
    
    logger.info("6. LAST RESORT:")
    logger.info("   • Restart your computer")
    logger.info("   • This will release all port locks")
    logger.info("")


def create_fix_batch_file():
    """Create a batch file for Windows to help with port issues"""
    if platform.system().lower() != 'windows':
        return
    
    batch_content = '''@echo off
echo Zebra Printer COM3 Fix Utility
echo ===============================
echo.

echo Step 1: Stopping Print Spooler...
net stop spooler
timeout /t 2 /nobreak > nul

echo Step 2: Starting Print Spooler...
net start spooler
timeout /t 2 /nobreak > nul

echo Step 3: Refreshing USB devices...
echo Please disconnect and reconnect your printer USB cable now.
echo Then press any key to continue...
pause > nul

echo.
echo Fix complete! Try running the WebSocket client again.
echo.
pause
'''
    
    try:
        with open('fix_com3.bat', 'w') as f:
            f.write(batch_content)
        logger.info("✅ Created 'fix_com3.bat' - Run as Administrator to fix COM3 issues")
    except Exception as e:
        logger.error(f"Failed to create batch file: {e}")


def main():
    logger.info("🔧 COM3 Port Issue Diagnostic and Fix Tool")
    logger.info("=" * 50)
    
    # Check if COM3 exists
    if not check_if_port_exists('COM3'):
        logger.error("❌ COM3 port not found in system")
        logger.info("Your printer might be on a different port.")
        
        # Show all available ports
        ports = list(serial.tools.list_ports.comports())
        if ports:
            logger.info("\nAvailable ports:")
            for port in ports:
                logger.info(f"  📍 {port.device}: {port.description}")
        return 1
    
    # Show COM3 details
    description = get_port_description('COM3')
    logger.info(f"📍 Found COM3: {description}")
    
    # Test if COM3 is accessible
    try:
        with serial.Serial('COM3', 9600, timeout=0.1) as ser:
            if ser.is_open:
                logger.info("✅ COM3 is accessible! The issue might be temporary.")
                logger.info("Try running the WebSocket client again.")
                return 0
    except Exception as e:
        logger.warning(f"❌ COM3 is blocked: {e}")
    
    # Try quick fix
    logger.info("\n🛠️  Attempting automatic fix...")
    if quick_port_release('COM3'):
        logger.info("✅ COM3 has been released! Try running the client again.")
        return 0
    
    # Look for alternatives
    logger.info("\n🔍 Looking for alternative working ports...")
    alternatives = find_alternative_ports()
    
    if alternatives:
        logger.info(f"\n✅ Found {len(alternatives)} working alternative port(s):")
        for alt in alternatives:
            logger.info(f"  📍 {alt}")
        logger.info("\nTo use an alternative port, set environment variable:")
        logger.info(f"  set SERIAL_PORT={alternatives[0]}")
    else:
        logger.warning("\n❌ No alternative working ports found")
    
    # Create Windows batch file helper
    if platform.system().lower() == 'windows':
        create_fix_batch_file()
    
    # Show manual solutions
    show_manual_solutions()
    
    logger.info("🏁 NEXT STEPS:")
    logger.info("1. Try the manual solutions above")
    logger.info("2. If you have working alternative ports, use them")
    logger.info("3. Consider using USB direct connection instead")
    logger.info("4. If all else fails, restart your computer")
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
