#!/usr/bin/env python3
"""
Port Diagnostics and Recovery Tool
==================================

A utility script to diagnose and fix serial port connection issues.
This tool helps identify which applications are using COM ports and
provides recovery mechanisms for stuck ports.

Usage:
    python port_diagnostics.py
    python port_diagnostics.py --port COM3
    python port_diagnostics.py --release COM3
    python port_diagnostics.py --find-printers
"""

import argparse
import logging
import platform
import subprocess
import sys
import time
from typing import List, Optional, Dict, Any

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("ERROR: PySerial not available. Install with: pip install pyserial")
    sys.exit(1)

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("WARNING: psutil not available. Process detection will be limited.")
    print("Install with: pip install psutil")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_port_usage_windows(port: str) -> List[Dict[str, Any]]:
    """Check which processes are using a specific COM port on Windows"""
    processes = []
    
    if not PSUTIL_AVAILABLE:
        logger.warning("psutil not available - cannot check process usage")
        return processes
    
    try:
        # Get the device path for the COM port
        device_path = f"\\\\.\\{port}"
        
        # Check all running processes
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
            try:
                # Check if process has any handles to the COM port
                handles = proc.open_files()
                for handle in handles:
                    if port.upper() in handle.path.upper():
                        processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'exe': proc.info['exe'],
                            'cmdline': ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else '',
                            'handle_path': handle.path
                        })
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except Exception as e:
        logger.error(f"Error checking port usage: {e}")
    
    return processes


def force_release_port(port: str, aggressive: bool = False) -> bool:
    """Attempt to force release a COM port"""
    logger.info(f"Attempting to release port {port}...")
    
    success = False
    
    try:
        # Method 1: Multiple quick open/close cycles
        logger.info("Method 1: Quick open/close cycles...")
        for attempt in range(5):
            try:
                ser = serial.Serial(port, 9600, timeout=0.1)
                time.sleep(0.05)
                ser.close()
                time.sleep(0.1)
                logger.debug(f"  Cycle {attempt + 1} completed")
            except Exception:
                continue
        
        # Test if this worked
        if test_port_quick(port):
            logger.info(f"✓ Port {port} released successfully (Method 1)")
            return True
        
        # Method 2: Try different baud rates to reset connection
        logger.info("Method 2: Baud rate reset...")
        for baud in [300, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]:
            try:
                ser = serial.Serial(port, baud, timeout=0.1)
                time.sleep(0.05)
                ser.close()
                time.sleep(0.05)
            except Exception:
                continue
        
        # Test again
        time.sleep(0.5)
        if test_port_quick(port):
            logger.info(f"✓ Port {port} released successfully (Method 2)")
            return True
        
        # Method 3: Aggressive mode (if requested)
        if aggressive:
            logger.info("Method 3: Aggressive release (attempting to kill processes)...")
            processes = check_port_usage_windows(port)
            
            if processes:
                logger.info(f"Found {len(processes)} process(es) using port {port}:")
                for proc in processes:
                    logger.info(f"  PID {proc['pid']}: {proc['name']} - {proc['exe']}")
                
                # Ask user if they want to terminate processes
                if input(f"Terminate processes using {port}? (y/N): ").lower() == 'y':
                    for proc in processes:
                        try:
                            psutil.Process(proc['pid']).terminate()
                            logger.info(f"Terminated process {proc['pid']} ({proc['name']})")
                        except Exception as e:
                            logger.error(f"Failed to terminate process {proc['pid']}: {e}")
                    
                    # Wait for processes to close
                    time.sleep(2.0)
                    
                    # Test again
                    if test_port_quick(port):
                        logger.info(f"✓ Port {port} released successfully (Method 3)")
                        return True
        
        # Method 4: Windows device reset (if on Windows)
        if platform.system().lower() == 'windows':
            logger.info("Method 4: Windows device reset...")
            try:
                # Try to use devcon if available
                result = subprocess.run(['devcon', 'restart', f'*{port}*'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    time.sleep(2.0)
                    if test_port_quick(port):
                        logger.info(f"✓ Port {port} released successfully (Method 4)")
                        return True
            except (subprocess.TimeoutExpired, FileNotFoundError):
                logger.debug("devcon not available or failed")
    
    except Exception as e:
        logger.error(f"Error during port release: {e}")
    
    if not success:
        logger.error(f"✗ Failed to release port {port}")
        logger.error("Manual steps required:")
        logger.error("1. Close all applications that might be using the port")
        logger.error("2. Check Windows Device Manager for port conflicts")
        logger.error("3. Disconnect and reconnect the USB cable")
        logger.error("4. Restart the computer if necessary")
    
    return success


def test_port_quick(port: str) -> bool:
    """Quick test if a port is accessible"""
    try:
        with serial.Serial(port, timeout=0.1) as ser:
            return ser.is_open
    except Exception:
        return False


def comprehensive_port_scan():
    """Perform a comprehensive scan of all COM ports"""
    logger.info("🔍 Comprehensive COM Port Scan")
    logger.info("=" * 50)
    
    # Get all available ports
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        logger.warning("No COM ports found")
        return
    
    logger.info(f"Found {len(ports)} COM port(s):")
    logger.info("")
    
    for i, port in enumerate(ports):
        logger.info(f"📍 Port {i+1}: {port.device}")
        logger.info(f"   Description: {port.description}")
        logger.info(f"   Hardware ID: {port.hwid if hasattr(port, 'hwid') else 'N/A'}")
        
        # Test accessibility
        accessible = test_port_quick(port.device)
        if accessible:
            logger.info(f"   Status: ✅ Available")
        else:
            logger.info(f"   Status: ❌ Blocked/In Use")
            
            # Check what's using it
            if platform.system().lower() == 'windows':
                processes = check_port_usage_windows(port.device)
                if processes:
                    logger.info(f"   Used by:")
                    for proc in processes:
                        logger.info(f"     - {proc['name']} (PID: {proc['pid']})")
                else:
                    logger.info(f"   Used by: Unknown (possibly system driver)")
        
        # Test with different baud rates
        if accessible:
            logger.info(f"   Baud rate test:")
            working_bauds = []
            for baud in [9600, 19200, 38400, 57600, 115200]:
                try:
                    with serial.Serial(port.device, baud, timeout=0.1):
                        working_bauds.append(str(baud))
                except:
                    pass
            logger.info(f"     Working rates: {', '.join(working_bauds) if working_bauds else 'None'}")
        
        logger.info("")


def find_printer_ports():
    """Find ports that are likely connected to printers"""
    logger.info("🖨️  Searching for Printer Ports")
    logger.info("=" * 50)
    
    ports = list(serial.tools.list_ports.comports())
    printer_ports = []
    
    # Keywords that indicate printer devices
    printer_keywords = [
        'printer', 'zebra', 'epson', 'brother', 'dymo', 'label', 'thermal',
        'zd220', 'zd410', 'zd420', 'tm-t', 'ql-', 'labelwriter'
    ]
    
    for port in ports:
        description = port.description.lower()
        hwid = (port.hwid or '').lower()
        
        # Check if description or hardware ID contains printer keywords
        is_printer = any(keyword in description or keyword in hwid 
                        for keyword in printer_keywords)
        
        if is_printer:
            printer_ports.append(port)
            logger.info(f"📍 Found printer: {port.device}")
            logger.info(f"   Description: {port.description}")
            logger.info(f"   Hardware ID: {port.hwid}")
            logger.info(f"   Accessible: {'✅ Yes' if test_port_quick(port.device) else '❌ No'}")
            logger.info("")
    
    if not printer_ports:
        logger.warning("No obvious printer ports found")
        logger.info("Checking all ports for potential printers...")
        
        for port in ports:
            logger.info(f"📍 {port.device}: {port.description}")
            if test_port_quick(port.device):
                logger.info(f"   Status: Available - could be a printer")
            else:
                logger.info(f"   Status: In use - might be a printer")
    
    return printer_ports


def main():
    parser = argparse.ArgumentParser(description='COM Port Diagnostics and Recovery Tool')
    parser.add_argument('--port', help='Specific COM port to test (e.g., COM3)')
    parser.add_argument('--release', help='Attempt to force release a specific port')
    parser.add_argument('--aggressive', action='store_true', 
                       help='Use aggressive release methods (may terminate processes)')
    parser.add_argument('--scan', action='store_true', 
                       help='Perform comprehensive port scan')
    parser.add_argument('--find-printers', action='store_true',
                       help='Find ports likely connected to printers')
    
    args = parser.parse_args()
    
    if not SERIAL_AVAILABLE:
        logger.error("PySerial is required but not available")
        return 1
    
    # If no arguments, show help and do basic scan
    if not any([args.port, args.release, args.scan, args.find_printers]):
        parser.print_help()
        print("\n" + "="*50)
        print("Performing basic printer port detection...")
        print("="*50)
        find_printer_ports()
        return 0
    
    # Handle specific actions
    if args.scan:
        comprehensive_port_scan()
    
    if args.find_printers:
        find_printer_ports()
    
    if args.port:
        logger.info(f"Testing port {args.port}...")
        if test_port_quick(args.port):
            logger.info(f"✅ Port {args.port} is accessible")
        else:
            logger.info(f"❌ Port {args.port} is not accessible")
            
            # Show what's using it
            if platform.system().lower() == 'windows':
                processes = check_port_usage_windows(args.port)
                if processes:
                    logger.info("Processes using this port:")
                    for proc in processes:
                        logger.info(f"  - {proc['name']} (PID: {proc['pid']})")
    
    if args.release:
        force_release_port(args.release, args.aggressive)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
