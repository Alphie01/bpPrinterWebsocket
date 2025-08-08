#!/usr/bin/env python3
"""
WebSocket Printer Client Runner
===============================

Simple entry point to start the WebSocket printer client.
This script loads configuration from environment variables or uses defaults,
then starts the WebSocket printer client.

Usage:
    python run_client.py

Environment Variables:
    PRINTER_ID: Unique identifier for the printer (default: PRINTER_001)
    PRINTER_NAME: Human-readable name for the printer (default: Default Printer)
    PRINTER_TYPE: Type of printer (thermal, label, laser) (default: thermal)
    PRINTER_LOCATION: Physical location of the printer (default: Warehouse A)
    SERIAL_PORT: Serial port for the printer (default: auto-detect)
    BAUD_RATE: Serial communication baud rate (default: 9600)
    SERIAL_TIMEOUT: Serial communication timeout (default: 1.0)
    SERVER_URL: WebSocket server URL (default: http://localhost:25625)
    CONNECTION_TYPE: Connection type (auto, serial, usb) (default: auto)
    USB_VENDOR_ID: USB vendor ID for USB printers (optional)
    USB_PRODUCT_ID: USB product ID for USB printers (optional)
"""

import asyncio
import logging
import os
import sys
import platform
from typing import Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    logging.warning("python-dotenv not available. Environment variables from .env file will not be loaded.")

# Add current directory to path to import local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    logging.warning("PySerial not available. Serial port functionality will be limited.")

try:
    import usb.core
    import usb.util
    USB_CORE_AVAILABLE = True
except ImportError:
    USB_CORE_AVAILABLE = False
    logging.warning("PyUSB not available. USB functionality will be limited.")

from config import ServerConfig
from printer_client import WebSocketPrinterClient, PrinterConnectionType, PrinterConfig, PrinterType, list_all_printers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Known printer USB IDs
KNOWN_PRINTER_IDS = {
    # Zebra printers
    (0x0A5F, 0x0164): {"brand": "Zebra", "model": "ZD410/ZD420", "type": "thermal"},
    (0x0A5F, 0x0181): {"brand": "Zebra", "model": "ZD510", "type": "thermal"},
    (0x0A5F, 0x0049): {"brand": "Zebra", "model": "GC420t", "type": "thermal"},
    (0x0A5F, 0x0061): {"brand": "Zebra", "model": "GK420t", "type": "thermal"},
    (0x0A5F, 0x008A): {"brand": "Zebra", "model": "ZT410", "type": "thermal"},
    
    # Brother printers  
    (0x04F9, 0x2028): {"brand": "Brother", "model": "QL-700", "type": "label"},
    (0x04F9, 0x202A): {"brand": "Brother", "model": "QL-710W", "type": "label"},
    (0x04F9, 0x202B): {"brand": "Brother", "model": "QL-720NW", "type": "label"},
    
    # Dymo printers
    (0x0922, 0x1001): {"brand": "Dymo", "model": "LabelWriter 450", "type": "label"},
    (0x0922, 0x1002): {"brand": "Dymo", "model": "LabelWriter 450 Turbo", "type": "label"},
    
    # Epson printers
    (0x04B8, 0x0202): {"brand": "Epson", "model": "TM-T20", "type": "thermal"},
    (0x04B8, 0x0204): {"brand": "Epson", "model": "TM-T88V", "type": "thermal"},
}


def find_usb_printers():
    """Find all USB printers using vendor/product IDs"""
    printers = []
    
    if not USB_CORE_AVAILABLE:
        logger.warning("PyUSB not available. Install with: pip install pyusb")
        return printers
    
    try:
        # Find all USB devices
        devices = usb.core.find(find_all=True)
        
        for device in devices:
            vendor_id = device.idVendor
            product_id = device.idProduct
            
            # Check if this is a known printer
            printer_key = (vendor_id, product_id)
            if printer_key in KNOWN_PRINTER_IDS:
                printer_info = KNOWN_PRINTER_IDS[printer_key].copy()
                printer_info.update({
                    'vendor_id': vendor_id,
                    'product_id': product_id,
                    'bus': device.bus,
                    'address': device.address,
                    'device': device
                })
                printers.append(printer_info)
                logger.info(f"Found {printer_info['brand']} {printer_info['model']} - VID:0x{vendor_id:04X} PID:0x{product_id:04X}")
    
    except Exception as e:
        logger.error(f"Error scanning USB devices: {e}")
        logger.info("Note: On Linux you may need to run with sudo or add udev rules")
    
    return printers


def find_specific_usb_printer(vendor_id: int, product_id: int):
    """Find a specific USB printer by vendor and product ID"""
    if not USB_CORE_AVAILABLE:
        logger.error("PyUSB not available for USB printer detection")
        return None
    
    try:
        device = usb.core.find(idVendor=vendor_id, idProduct=product_id)
        if device is not None:
            printer_key = (vendor_id, product_id)
            if printer_key in KNOWN_PRINTER_IDS:
                printer_info = KNOWN_PRINTER_IDS[printer_key].copy()
                logger.info(f"Found specific printer: {printer_info['brand']} {printer_info['model']}")
            else:
                logger.info(f"Found unknown USB device: VID:0x{vendor_id:04X} PID:0x{product_id:04X}")
            
            return device
        else:
            logger.warning(f"USB printer not found: VID:0x{vendor_id:04X} PID:0x{product_id:04X}")
            return None
    except Exception as e:
        logger.error(f"Error finding USB printer: {e}")
        return None


def get_connection_type() -> PrinterConnectionType:
    """Get connection type from environment variable"""
    connection_type_str = os.getenv('CONNECTION_TYPE', 'auto').lower()
    if connection_type_str == 'serial':
        return PrinterConnectionType.SERIAL
    elif connection_type_str == 'usb':
        return PrinterConnectionType.USB
    else:
        return PrinterConnectionType.AUTO


def test_serial_port(port: str, baud_rate: int = 9600, timeout: float = 1.0) -> bool:
    """Test if a serial port is accessible and working"""
    if not SERIAL_AVAILABLE:
        logger.error("PySerial not available for port testing")
        return False
    
    try:
        logger.info(f"Testing port {port} with baud rate {baud_rate}...")
        
        # Try to open the port with minimal timeout
        with serial.Serial(port, baud_rate, timeout=timeout) as ser:
            logger.info(f"Port {port} opened successfully")
            
            # Test if port is readable/writable
            if ser.is_open:
                logger.info(f"Port {port} is open and ready")
                return True
            else:
                logger.warning(f"Port {port} failed to open properly")
                return False
                
    except serial.SerialException as e:
        logger.error(f"SerialException on port {port}: {e}")
        if "permission" in str(e).lower() or "access" in str(e).lower():
            logger.error(f"Permission denied for port {port}. Port may be in use by another application.")
        elif "not exist" in str(e).lower() or "cannot find" in str(e).lower():
            logger.error(f"Port {port} does not exist or is not available.")
        return False
    except PermissionError as e:
        logger.error(f"Permission error on port {port}: {e}")
        logger.error("Try running as administrator or close other applications using this port")
        return False
    except Exception as e:
        logger.error(f"Unexpected error testing port {port}: {e}")
        return False


def force_release_port(port: str) -> bool:
    """Attempt to force release a port that may be stuck"""
    if not SERIAL_AVAILABLE:
        return False
    
    logger.info(f"Attempting to force release port {port}...")
    
    try:
        # Try multiple strategies to release the port
        import time
        
        # Strategy 1: Quick open/close cycle
        for attempt in range(3):
            try:
                ser = serial.Serial(port, timeout=0.1)
                time.sleep(0.1)
                ser.close()
                time.sleep(0.2)
                logger.info(f"Port release attempt {attempt + 1} completed")
            except:
                continue
        
        # Strategy 2: Try different baud rates to reset the connection
        for baud in [9600, 19200, 38400, 115200]:
            try:
                ser = serial.Serial(port, baud, timeout=0.1)
                time.sleep(0.1)
                ser.close()
                time.sleep(0.1)
            except:
                continue
        
        # Wait a bit for the port to be released by the system
        time.sleep(1.0)
        
        # Test if the port is now available
        return test_serial_port(port, timeout=0.5)
        
    except Exception as e:
        logger.warning(f"Force release failed for port {port}: {e}")
        return False


def find_working_serial_port() -> Optional[str]:
    """Find the first working serial port"""
    if not SERIAL_AVAILABLE:
        return None
    
    try:
        ports = list(serial.tools.list_ports.comports())
        if not ports:
            logger.warning("No serial ports found")
            return None
        
        logger.info(f"Testing {len(ports)} available serial port(s)...")
        
        for port_info in ports:
            port_device = port_info.device
            logger.info(f"Testing {port_device}: {port_info.description}")
            
            # Skip ports that are likely not printers
            description_lower = port_info.description.lower()
            if any(skip_word in description_lower for skip_word in ['bluetooth', 'virtual', 'emulated']):
                logger.info(f"Skipping {port_device} - appears to be virtual/bluetooth device")
                continue
            
            if test_serial_port(port_device):
                logger.info(f"Found working port: {port_device}")
                return port_device
            else:
                logger.warning(f"Port {port_device} is not accessible")
        
        logger.error("No working serial ports found")
        return None
        
    except Exception as e:
        logger.error(f"Error scanning for working ports: {e}")
        return None


def auto_detect_serial_port() -> Optional[str]:
    """Auto-detect the first available serial port with enhanced recovery"""
    try:
        available_printers = list_all_printers()
        if available_printers and available_printers.get('serial'):
            port = available_printers['serial'][0]
            logger.info(f"Auto-detected serial port from list_all_printers: {port}")
            
            # Test if the detected port actually works
            if test_serial_port(port):
                return port
            else:
                logger.warning(f"Detected port {port} is not accessible, trying recovery...")
                
                # Try to force release the port
                if force_release_port(port):
                    logger.info(f"Successfully recovered port {port}")
                    return port
                else:
                    logger.warning(f"Could not recover port {port}, trying fallback...")
        
        # Fallback: Find a working serial port
        logger.info("Trying to find any working serial port...")
        working_port = find_working_serial_port()
        if working_port:
            return working_port
        
        # Enhanced fallback: Try to recover stuck ports
        if platform.system().lower() == 'windows' and SERIAL_AVAILABLE:
            logger.info("Trying common Windows COM ports with recovery...")
            for com_port in ['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8']:
                logger.info(f"Checking {com_port}...")
                if test_serial_port(com_port, timeout=0.5):
                    logger.info(f"Found working COM port: {com_port}")
                    return com_port
                else:
                    # Try to recover this port
                    logger.info(f"Attempting recovery for {com_port}...")
                    if force_release_port(com_port):
                        logger.info(f"Successfully recovered COM port: {com_port}")
                        return com_port
        
        logger.warning("No accessible serial ports found")
            
    except Exception as e:
        logger.error(f"Error detecting serial ports: {e}")
    return None


def auto_detect_usb_printer() -> tuple[Optional[int], Optional[int]]:
    """Auto-detect the first available USB printer using known IDs"""
    try:
        # First try the project's list_all_printers function
        available_printers = list_all_printers()
        if available_printers and available_printers.get('usb'):
            printer = available_printers['usb'][0]
            vendor_id = printer.get('vendor_id')
            product_id = printer.get('product_id')
            if vendor_id and product_id:
                logger.info(f"Auto-detected USB printer: VID 0x{vendor_id:04X}, PID 0x{product_id:04X}")
                return vendor_id, product_id
        
        # If that fails, try direct USB scanning with known printer IDs
        if USB_CORE_AVAILABLE:
            logger.info("Scanning for known USB printers...")
            usb_printers = find_usb_printers()
            if usb_printers:
                # Use the first found printer
                printer = usb_printers[0]
                vendor_id = printer['vendor_id']
                product_id = printer['product_id']
                logger.info(f"Found {printer['brand']} {printer['model']} - VID:0x{vendor_id:04X} PID:0x{product_id:04X}")
                return vendor_id, product_id
        
        # Enhanced Zebra detection for libusb devices
        if USB_CORE_AVAILABLE:
            logger.info("Checking for Zebra printers with multiple PID variants...")
            zebra_vendor = 0x0A5F
            zebra_pids = [0x0164, 0x0161, 0x0049, 0x0061, 0x008A, 0x0078, 0x0181]  # Common Zebra PIDs
            
            for pid in zebra_pids:
                device = usb.core.find(idVendor=zebra_vendor, idProduct=pid)
                if device is not None:
                    try:
                        manufacturer = usb.util.get_string(device, device.iManufacturer) if device.iManufacturer else "Unknown"
                        product = usb.util.get_string(device, device.iProduct) if device.iProduct else "Unknown"
                        logger.info(f"Found Zebra printer: {manufacturer} {product} - VID:0x{zebra_vendor:04X} PID:0x{pid:04X}")
                        return zebra_vendor, pid
                    except Exception:
                        logger.info(f"Found Zebra printer (details unavailable) - VID:0x{zebra_vendor:04X} PID:0x{pid:04X}")
                        return zebra_vendor, pid
            
        # Try the specific Zebra printer from old_matching.py as fallback
        zebra_vendor = 0x0A5F
        zebra_product = 0x0164
        if find_specific_usb_printer(zebra_vendor, zebra_product):
            logger.info(f"Found Zebra printer (fallback): VID:0x{zebra_vendor:04X} PID:0x{zebra_product:04X}")
            return zebra_vendor, zebra_product
            
    except Exception as e:
        logger.error(f"Error detecting USB printers: {e}")
    
    return None, None


def create_printer_config() -> PrinterConfig:
    """Create printer configuration from environment variables with auto-detection"""
    # Basic configuration from environment
    printer_id = os.getenv('PRINTER_ID', 'PRINTER_001')
    printer_name = os.getenv('PRINTER_NAME', 'Default Printer')
    printer_type_str = os.getenv('PRINTER_TYPE', 'thermal')
    location = os.getenv('PRINTER_LOCATION', 'Warehouse A')
    baud_rate = int(os.getenv('BAUD_RATE', '9600'))
    timeout = float(os.getenv('SERIAL_TIMEOUT', '1.0'))
    connection_type = get_connection_type()
    
    # Convert printer type string to enum
    try:
        printer_type = PrinterType(printer_type_str)
    except ValueError:
        logger.warning(f"Invalid printer type '{printer_type_str}', using 'thermal'")
        printer_type = PrinterType.THERMAL
    
    # Handle serial port configuration
    serial_port = os.getenv('SERIAL_PORT')
    if serial_port:
        # Test the specified port
        logger.info(f"Testing specified serial port: {serial_port}")
        if not test_serial_port(serial_port, baud_rate):
            logger.error(f"Specified serial port {serial_port} is not accessible!")
            logger.error("Common solutions:")
            logger.error("1. Close any other applications using this port (Arduino IDE, PuTTY, etc.)")
            logger.error("2. Check Device Manager for port conflicts")
            logger.error("3. Try running as Administrator")
            logger.error("4. Disconnect and reconnect the printer")
            logger.error("5. Try a different USB port")
            
            # Ask if user wants to try auto-detection
            if connection_type in [PrinterConnectionType.SERIAL, PrinterConnectionType.AUTO]:
                logger.info("Attempting to find an alternative working port...")
                auto_port = auto_detect_serial_port()
                if auto_port and auto_port != serial_port:
                    logger.info(f"Found alternative working port: {auto_port}")
                    serial_port = auto_port
                else:
                    logger.warning("No alternative ports found")
                    serial_port = None
            else:
                serial_port = None
    elif connection_type in [PrinterConnectionType.SERIAL, PrinterConnectionType.AUTO]:
        logger.info("No serial port specified, attempting auto-detection...")
        serial_port = auto_detect_serial_port()
        if not serial_port:
            logger.warning("No working serial port found during auto-detection")
    
    # Handle USB configuration
    usb_vendor_id = None
    usb_product_id = None
    
    vendor_id_str = os.getenv('USB_VENDOR_ID')
    product_id_str = os.getenv('USB_PRODUCT_ID')
    
    if vendor_id_str and product_id_str:
        try:
            usb_vendor_id = int(vendor_id_str, 16) if vendor_id_str.startswith('0x') else int(vendor_id_str)
            usb_product_id = int(product_id_str, 16) if product_id_str.startswith('0x') else int(product_id_str)
            logger.info(f"Using USB IDs from environment: VID:0x{usb_vendor_id:04X} PID:0x{usb_product_id:04X}")
            
            # Verify the device exists
            if USB_CORE_AVAILABLE:
                device = find_specific_usb_printer(usb_vendor_id, usb_product_id)
                if device is None:
                    logger.warning("Specified USB printer not found, will try auto-detection")
                    usb_vendor_id = None
                    usb_product_id = None
        except ValueError:
            logger.warning("Invalid USB vendor/product ID format in environment variables")
    
    # Auto-detect if not specified or not found
    if not usb_vendor_id or not usb_product_id:
        if connection_type in [PrinterConnectionType.USB, PrinterConnectionType.AUTO]:
            logger.info("Auto-detecting USB printer...")
            usb_vendor_id, usb_product_id = auto_detect_usb_printer()
    
    return PrinterConfig(
        printer_id=printer_id,
        printer_name=printer_name,
        printer_type=printer_type,
        location=location,
        connection_type=connection_type,
        serial_port=serial_port,
        baud_rate=baud_rate,
        timeout=timeout,
        usb_vendor_id=usb_vendor_id,
        usb_product_id=usb_product_id
    )


def create_server_config() -> ServerConfig:
    """Create server configuration from environment variables"""
    return ServerConfig(
        url=os.getenv('SERVER_URL', 'http://localhost:25625'),
        reconnect_delay=float(os.getenv('RECONNECT_DELAY', '5.0')),
        max_reconnect_attempts=int(os.getenv('MAX_RECONNECT_ATTEMPTS', '10')),
        ping_interval=float(os.getenv('PING_INTERVAL', '30.0'))
    )


def list_available_ports():
    """List all available serial ports and USB printers for debugging"""
    logger.info("=== Available Printers Debug ===")
    
    # Serial ports
    if not SERIAL_AVAILABLE:
        logger.error("PySerial not installed. Install with: pip install pyserial")
    else:
        try:
            ports = list(serial.tools.list_ports.comports())
            if not ports:
                logger.warning("No serial ports found")
                if platform.system().lower() == 'windows':
                    logger.info("Windows troubleshooting tips:")
                    logger.info("1. Check Device Manager for COM ports")
                    logger.info("2. Install printer drivers")
                    logger.info("3. Check if printer is properly connected")
                    logger.info("4. Try different USB ports")
            else:
                logger.info(f"Found {len(ports)} serial port(s):")
                for i, port in enumerate(ports):
                    logger.info(f"  {i+1}: {port.device}")
                    logger.info(f"      Description: {port.description}")
                    logger.info(f"      Hardware ID: {port.hwid if hasattr(port, 'hwid') else 'N/A'}")
                    
                    # Test if port is accessible with better error reporting
                    try:
                        with serial.Serial(port.device, timeout=0.1) as test_ser:
                            logger.info(f"      Status: Available ✓")
                    except serial.SerialException as e:
                        if "permission" in str(e).lower() or "access" in str(e).lower():
                            logger.info(f"      Status: ❌ Permission denied - Port in use")
                        elif "not exist" in str(e).lower():
                            logger.info(f"      Status: ❌ Port does not exist")
                        else:
                            logger.info(f"      Status: ❌ Error - {e}")
                    except PermissionError:
                        logger.info(f"      Status: ❌ Permission denied - Port in use")
                    except Exception as e:
                        logger.info(f"      Status: ❌ Error - {e}")
                    logger.info("")
        except Exception as e:
            logger.error(f"Error listing serial ports: {e}")
    
    # USB printers
    logger.info("=== USB Printers ===")
    if not USB_CORE_AVAILABLE:
        logger.warning("PyUSB not installed. Install with: pip install pyusb")
        logger.info("Note: PyUSB is required for direct USB printer communication")
    else:
        try:
            usb_printers = find_usb_printers()
            if not usb_printers:
                logger.warning("No known USB printers found")
                logger.info("Looking for any USB devices that might be printers...")
                
                # Look for any USB devices that might be printers
                devices = usb.core.find(find_all=True)
                printer_like_devices = []
                
                for device in devices:
                    try:
                        # Check device class (7 = Printer class)
                        if hasattr(device, 'bDeviceClass') and device.bDeviceClass == 7:
                            printer_like_devices.append(device)
                        # Check interface class
                        elif hasattr(device, 'configurations'):
                            for config in device.configurations():
                                for interface in config:
                                    if interface.bInterfaceClass == 7:  # Printer class
                                        printer_like_devices.append(device)
                                        break
                    except:
                        continue
                
                if printer_like_devices:
                    logger.info(f"Found {len(printer_like_devices)} potential printer device(s):")
                    for device in printer_like_devices:
                        logger.info(f"  VID:0x{device.idVendor:04X} PID:0x{device.idProduct:04X}")
                        try:
                            logger.info(f"    Manufacturer: {usb.util.get_string(device, device.iManufacturer)}")
                            logger.info(f"    Product: {usb.util.get_string(device, device.iProduct)}")
                        except:
                            logger.info(f"    Description: Unknown")
                else:
                    logger.info("No USB printer devices found")
            else:
                logger.info(f"Found {len(usb_printers)} known USB printer(s):")
                for printer in usb_printers:
                    logger.info(f"  {printer['brand']} {printer['model']}")
                    logger.info(f"    VID:0x{printer['vendor_id']:04X} PID:0x{printer['product_id']:04X}")
                    logger.info(f"    Type: {printer['type']}")
                    logger.info("")
        except Exception as e:
            logger.error(f"Error listing USB devices: {e}")
            if platform.system().lower() == 'linux':
                logger.info("Note: On Linux you may need to run with sudo or add udev rules")
            elif platform.system().lower() == 'windows':
                logger.info("Note: Install libusb drivers for USB access")


async def main():
    """Main function to start the WebSocket printer client"""
    logger.info("Starting WebSocket Printer Client...")
    logger.info(f"Operating System: {platform.system()} {platform.release()}")
    logger.info(f"PySerial Available: {SERIAL_AVAILABLE}")
    logger.info(f"PyUSB Available: {USB_CORE_AVAILABLE}")
    
    # List available ports and printers for debugging
    list_available_ports()
    
    try:
        # Create configurations
        printer_config = create_printer_config()
        server_config = create_server_config()
        
        # Log configuration
        logger.info("Printer Configuration:")
        logger.info(f"  ID: {printer_config.printer_id}")
        logger.info(f"  Name: {printer_config.printer_name}")
        logger.info(f"  Type: {printer_config.printer_type.value}")
        logger.info(f"  Location: {printer_config.location}")
        logger.info(f"  Connection Type: {printer_config.connection_type.value}")
        
        if printer_config.serial_port:
            logger.info(f"  Serial Port: {printer_config.serial_port}")
            logger.info(f"  Baud Rate: {printer_config.baud_rate}")
        
        if printer_config.usb_vendor_id and printer_config.usb_product_id:
            logger.info(f"  USB: VID 0x{printer_config.usb_vendor_id:04X}, PID 0x{printer_config.usb_product_id:04X}")
        
        logger.info(f"Server URL: {server_config.url}")
        
        # Check if any printer connection is available
        has_serial = printer_config.serial_port is not None
        has_usb = printer_config.usb_vendor_id is not None and printer_config.usb_product_id is not None
        
        if not has_serial and not has_usb:
            logger.warning("No printer connection configured.")
            
            # Try to find any available printers as last resort
            logger.info("Attempting emergency port detection...")
            try:
                if SERIAL_AVAILABLE:
                    # Use the working port finder instead of just listing
                    working_port = find_working_serial_port()
                    if working_port:
                        logger.info(f"Emergency detection found working port: {working_port}")
                        printer_config.serial_port = working_port
                        printer_config.connection_type = PrinterConnectionType.SERIAL
                        has_serial = True
                    else:
                        logger.error("No working serial ports found during emergency detection")
                else:
                    logger.error("PySerial not available for emergency port scanning.")
            except Exception as e:
                logger.error(f"Error during emergency port detection: {e}")
            
            if not has_serial and not has_usb:
                logger.error("No printer connections available.")
                logger.error("")
                logger.error("🔧 QUICK FIX AVAILABLE!")
                logger.error("Run the following command to diagnose and fix COM port issues:")
                logger.error("    python fix_com3.py")
                logger.error("")
                logger.error("=== Troubleshooting Guide ===")
                logger.error("For Serial/COM port issues:")
                logger.error("1. Check if another application is using the port:")
                logger.error("   - Close Arduino IDE, PuTTY, HyperTerminal, etc.")
                logger.error("   - Close any other printer software")
                logger.error("   - Close Zebra Setup Utilities or ZebraLink")
                logger.error("2. Check Windows Device Manager:")
                logger.error("   - Look for 'Ports (COM & LPT)' section")
                logger.error("   - Check for yellow warning icons")
                logger.error("   - Try updating drivers")
                logger.error("   - Disable and re-enable the COM port")
                logger.error("3. Hardware troubleshooting:")
                logger.error("   - Disconnect and reconnect USB cable")
                logger.error("   - Try different USB port")
                logger.error("   - Check cable quality")
                logger.error("4. Permission issues:")
                logger.error("   - Try running as Administrator")
                logger.error("   - Check if port is locked by Windows")
                logger.error("5. Set specific port manually:")
                logger.error("   - Set environment variable: SET SERIAL_PORT=COM1")
                logger.error("   - Or add to .env file: SERIAL_PORT=COM1")
                logger.error("6. Force release stuck port:")
                logger.error("   - Run: python port_diagnostics.py --release COM3")
                logger.error("")
                logger.error("For USB direct connection:")
                logger.error("1. Install PyUSB: pip install pyusb")
                logger.error("2. Set USB IDs: USB_VENDOR_ID=0x0A5F USB_PRODUCT_ID=0x0164")
                logger.error("3. Set connection type: CONNECTION_TYPE=usb")
                logger.error("4. For Windows: Install WinUSB driver using Zadig")
                logger.error("   Download Zadig: https://zadig.akeo.ie/")
                logger.error("   Select your printer and install WinUSB driver")
                logger.error("5. Quick USB setup: python setup_usb_zebra.py")
                logger.error("")
                logger.error("💡 TIP: For Zebra ZD220 printers, try USB direct connection")
                logger.error("    This bypasses COM port issues entirely!")
                logger.error("🔧 AUTOMATED USB SETUP:")
                logger.error("    Run: python setup_usb_zebra.py")
                return 1
        
        # Create and start the WebSocket client
        client = WebSocketPrinterClient(printer_config, server_config.url)
        
        logger.info("Starting WebSocket client...")
        await client.start()
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
        return 0
    except Exception as e:
        logger.error(f"Error starting client: {e}")
        return 1


if __name__ == "__main__":
    # Run the main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code)