#!/usr/bin/env python3
"""
USB-Only WebSocket Printer Client Runner
========================================

Simple entry point to start the USB-only WebSocket printer client.
This version removes all COM port dependencies and uses only direct USB communication.

Usage:
    python run_usb_client.py

Environment Variables:
    PRINTER_ID: Unique identifier for the printer (default: USB_PRINTER_001)
    PRINTER_NAME: Human-readable name for the printer (default: Auto-detected printer name)
    PRINTER_TYPE: Type of printer (thermal, label, zebra) (default: zebra)
    PRINTER_LOCATION: Physical location of the printer (default: Warehouse A)
    SERVER_URL: WebSocket server URL (default: http://192.168.1.139:25625)
    USB_VENDOR_ID: USB vendor ID for USB printers (optional, auto-detect if not specified)
    USB_PRODUCT_ID: USB product ID for USB printers (optional, auto-detect if not specified)
    AUTO_DETECT: Auto-detect printer if vendor/product ID not specified (default: true)
"""

import asyncio
import logging
import os
import sys
from typing import Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    logging.warning("python-dotenv not available. Environment variables from .env file will not be loaded. Install with: pip install python-dotenv")

# Add current directory to path to import local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import usb.core
    import usb.util
    USB_AVAILABLE = True
except ImportError:
    USB_AVAILABLE = False
    print("ERROR: PyUSB not available. Install with: pip install pyusb")
    sys.exit(1)

from usb_printer_client import WebSocketPrinterClient, USBPrinterConfig, PrinterType, list_available_usb_printers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_config_from_env() -> USBPrinterConfig:
    """Get printer configuration from environment variables"""
    
    # Get environment variables
    printer_id = os.getenv('PRINTER_ID', 'USB_PRINTER_001')
    printer_name = os.getenv('PRINTER_NAME', '')
    printer_type_str = os.getenv('PRINTER_TYPE', 'zebra').lower()
    printer_location = os.getenv('PRINTER_LOCATION', 'Warehouse A')
    
    # USB configuration
    usb_vendor_id = os.getenv('USB_VENDOR_ID')
    usb_product_id = os.getenv('USB_PRODUCT_ID')
    auto_detect = os.getenv('AUTO_DETECT', 'true').lower() == 'true'
    
    # Convert vendor/product IDs from hex strings if provided
    if usb_vendor_id:
        try:
            usb_vendor_id = int(usb_vendor_id, 16) if usb_vendor_id.startswith('0x') else int(usb_vendor_id)
        except ValueError:
            logger.warning(f"Invalid USB_VENDOR_ID: {usb_vendor_id}, using auto-detect")
            usb_vendor_id = None
    
    if usb_product_id:
        try:
            usb_product_id = int(usb_product_id, 16) if usb_product_id.startswith('0x') else int(usb_product_id)
        except ValueError:
            logger.warning(f"Invalid USB_PRODUCT_ID: {usb_product_id}, using auto-detect")
            usb_product_id = None
    
    # Convert printer type
    try:
        printer_type = PrinterType(printer_type_str)
    except ValueError:
        logger.warning(f"Unknown printer type: {printer_type_str}, using ZEBRA")
        printer_type = PrinterType.ZEBRA
    
    # If no printer name specified and we have vendor/product IDs, try to get info
    if not printer_name and usb_vendor_id and usb_product_id:
        printers = list_available_usb_printers()
        for printer in printers:
            if printer['vendor_id'] == usb_vendor_id and printer['product_id'] == usb_product_id:
                printer_name = f"{printer['manufacturer']} {printer['model']}"
                break
    
    if not printer_name:
        printer_name = "Auto-detected USB Printer"
    
    return USBPrinterConfig(
        printer_id=printer_id,
        printer_name=printer_name,
        printer_type=printer_type,
        location=printer_location,
        usb_vendor_id=usb_vendor_id,
        usb_product_id=usb_product_id,
        auto_detect=auto_detect
    )


def get_server_url() -> str:
    """Get server URL from environment variables"""
    # First try environment variable, then fallback to default
    server_url = os.getenv('SERVER_URL')
    if not server_url:
        server_url = 'http://192.168.1.139:25625'
        if DOTENV_AVAILABLE:
            print("WARNING: SERVER_URL not found in .env file, using default: http://192.168.1.139:25625")
        else:
            print("INFO: Using default SERVER_URL: http://192.168.1.139:25625")
    return server_url


def display_printer_info():
    """Display available printer information"""
    print("\\n" + "="*60)
    print("USB Printer Detection")
    print("="*60)
    
    # List available printers
    printers = list_available_usb_printers()
    
    if printers:
        print(f"Found {len(printers)} USB printer(s):")
        print()
        for i, printer in enumerate(printers, 1):
            print(f"{i}. {printer['manufacturer']} {printer['model']}")
            print(f"   Type: {printer['type'].upper()}")
            print(f"   USB ID: VID=0x{printer['vendor_id']:04X}, PID=0x{printer['product_id']:04X}")
            print(f"   Description: {printer['description']}")
            print()
    else:
        print("No supported USB printers found.")
        print()
        print("Supported printer types:")
        print("- Zebra thermal printers (ZD410, ZD420, GK420d, etc.)")
        print("- Brother label printers (QL-700, QL-800, etc.)")
        print("- Epson thermal printers (TM-T20, TM-T88, etc.)")
        print()
        print("Make sure your printer is:")
        print("1. Connected via USB")
        print("2. Powered on")
        print("3. Properly installed (drivers if needed)")
    
    print("="*60)


async def main():
    """Main function"""
    print("USB-Only WebSocket Printer Client")
    print("Version: 2.0.0 (No COM port dependencies)")
    print()
    
    # Display printer information
    display_printer_info()
    
    # Get configuration
    config = get_config_from_env()
    server_url = get_server_url()
    
    print("Configuration:")
    print(f"  Printer ID: {config.printer_id}")
    print(f"  Printer Name: {config.printer_name}")
    print(f"  Printer Type: {config.printer_type.value}")
    print(f"  Location: {config.location}")
    print(f"  Server URL: {server_url}")
    
    if config.usb_vendor_id and config.usb_product_id:
        print(f"  USB ID: VID=0x{config.usb_vendor_id:04X}, PID=0x{config.usb_product_id:04X}")
        print(f"  Auto-detect: {config.auto_detect}")
    else:
        print(f"  Auto-detect: {config.auto_detect}")
    
    print()
    
    # Validate that we have printers available
    printers = list_available_usb_printers()
    if not printers and not config.auto_detect:
        print("ERROR: No USB printers found and auto-detect is disabled.")
        print("Please connect a supported USB printer or enable auto-detect.")
        sys.exit(1)
    
    # Create and start client
    client = WebSocketPrinterClient(server_url, config)
    
    try:
        print("Starting USB printer client...")
        print("Press Ctrl+C to stop")
        print()
        
        await client.start()
        
    except KeyboardInterrupt:
        print("\\nReceived interrupt signal, stopping...")
    except Exception as e:
        logger.error(f"Error running client: {e}")
        sys.exit(1)
    finally:
        await client.stop()
        print("Client stopped.")


if __name__ == "__main__":
    # Check if pyusb is available
    if not USB_AVAILABLE:
        print("ERROR: PyUSB is required for USB printer communication.")
        print("Install with: pip install pyusb")
        print()
        print("On macOS, you may also need:")
        print("  brew install libusb")
        print()
        print("On Linux, you may need:")
        print("  sudo apt-get install libusb-1.0-0-dev")
        print("  or")
        print("  sudo yum install libusb1-devel")
        sys.exit(1)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\nShutdown complete.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
