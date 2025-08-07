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


def auto_detect_serial_port() -> Optional[str]:
    """Auto-detect the first available serial port"""
    try:
        available_printers = list_all_printers()
        if available_printers and available_printers.get('serial'):
            port = available_printers['serial'][0]
            logger.info(f"Auto-detected serial port: {port}")
            return port
        else:
            # Fallback: Try common serial ports
            if SERIAL_AVAILABLE:
                ports = list(serial.tools.list_ports.comports())
                if ports:
                    # Sort ports to prefer lower numbered COM ports on Windows
                    if platform.system().lower() == 'windows':
                        ports = sorted(ports, key=lambda x: x.device)
                    
                    port = ports[0].device
                    logger.info(f"Fallback: Using first available port: {port} - {ports[0].description}")
                    return port
                else:
                    logger.warning("No serial ports found on system")
            else:
                logger.warning("PySerial not available for port detection")
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
    if not serial_port and connection_type in [PrinterConnectionType.SERIAL, PrinterConnectionType.AUTO]:
        serial_port = auto_detect_serial_port()
        if not serial_port:
            logger.warning("No serial port specified and auto-detection failed")
            # For Windows, try common COM ports as fallback
            if platform.system().lower() == 'windows' and SERIAL_AVAILABLE:
                for com_port in ['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8']:
                    try:
                        test_serial = serial.Serial(com_port, timeout=0.1)
                        test_serial.close()
                        serial_port = com_port
                        logger.info(f"Found working COM port: {com_port}")
                        break
                    except Exception:
                        continue
    
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
                    
                    # Test if port is accessible
                    try:
                        test_serial = serial.Serial(port.device, timeout=0.1)
                        test_serial.close()
                        logger.info(f"      Status: Available ✓")
                    except Exception as e:
                        logger.info(f"      Status: Busy or Error - {e}")
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
            logger.info("Attempting to find any available printers...")
            try:
                if SERIAL_AVAILABLE:
                    ports = list(serial.tools.list_ports.comports())
                    if ports:
                        logger.info("Available serial ports found:")
                        for i, port in enumerate(ports):
                            logger.info(f"  {i}: {port.device} - {port.description}")
                        
                        # Use the first available port
                        first_port = ports[0].device
                        logger.info(f"Using first available port: {first_port}")
                        
                        # Update printer config with found port
                        printer_config.serial_port = first_port
                        printer_config.connection_type = PrinterConnectionType.SERIAL
                        has_serial = True
                    else:
                        logger.error("No serial ports found on this system.")
                else:
                    logger.error("PySerial not available for port scanning.")
            except Exception as e:
                logger.error(f"Error scanning for ports: {e}")
            
            if not has_serial and not has_usb:
                logger.error("No printer connections available. Please:")
                logger.error("1. Check if printer is connected")
                logger.error("2. Install printer drivers")
                logger.error("3. Check Windows Device Manager for COM ports")
                logger.error("4. Set SERIAL_PORT environment variable manually")
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