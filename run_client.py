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

from config import ServerConfig
from printer_client import WebSocketPrinterClient, PrinterConnectionType, PrinterConfig, PrinterType, list_all_printers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
    """Auto-detect the first available USB printer"""
    try:
        available_printers = list_all_printers()
        if available_printers and available_printers.get('usb'):
            printer = available_printers['usb'][0]
            vendor_id = printer.get('vendor_id')
            product_id = printer.get('product_id')
            if vendor_id and product_id:
                logger.info(f"Auto-detected USB printer: VID 0x{vendor_id:04X}, PID 0x{product_id:04X}")
                return vendor_id, product_id
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
        except ValueError:
            logger.warning("Invalid USB vendor/product ID format")
    elif connection_type in [PrinterConnectionType.USB, PrinterConnectionType.AUTO]:
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
    """List all available serial ports for debugging"""
    logger.info("=== Available Serial Ports Debug ===")
    
    if not SERIAL_AVAILABLE:
        logger.error("PySerial not installed. Install with: pip install pyserial")
        return
    
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
        logger.error(f"Error listing ports: {e}")


async def main():
    """Main function to start the WebSocket printer client"""
    logger.info("Starting WebSocket Printer Client...")
    logger.info(f"Operating System: {platform.system()} {platform.release()}")
    logger.info(f"PySerial Available: {SERIAL_AVAILABLE}")
    
    # List available ports for debugging
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