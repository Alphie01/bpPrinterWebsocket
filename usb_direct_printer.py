"""
Direct USB Printer Interface
============================

Direct USB communication with Zebra and other thermal printers.
This module removes all COM port dependencies and communicates directly via USB.

Based on the main.py implementation for direct USB communication.
"""

import logging
import time
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

try:
    import usb.core
    import usb.util
    USB_AVAILABLE = True
except ImportError:
    USB_AVAILABLE = False
    raise ImportError("PyUSB is required for USB printer communication. Install with: pip install pyusb")

logger = logging.getLogger(__name__)


class USBPrinterType(Enum):
    """USB printer types"""
    ZEBRA = "zebra"
    EPSON = "epson"
    BROTHER = "brother"
    GENERIC = "generic"


@dataclass
class USBPrinterInfo:
    """USB Printer information"""
    vendor_id: int
    product_id: int
    manufacturer: str
    model: str
    printer_type: USBPrinterType
    description: str


# Known USB printers database
KNOWN_USB_PRINTERS = [
    # Zebra printers
    USBPrinterInfo(0x0A5F, 0x0164, "Zebra", "ZD410/ZD420", USBPrinterType.ZEBRA, "Zebra ZD410/ZD420 Direct Thermal Printer"),
    USBPrinterInfo(0x0A5F, 0x0181, "Zebra", "ZD510", USBPrinterType.ZEBRA, "Zebra ZD510 Direct Thermal Printer"),
    USBPrinterInfo(0x0A5F, 0x0049, "Zebra", "GC420t", USBPrinterType.ZEBRA, "Zebra GC420t Thermal Printer"),
    USBPrinterInfo(0x0A5F, 0x0061, "Zebra", "GK420t", USBPrinterType.ZEBRA, "Zebra GK420t Thermal Printer"),
    USBPrinterInfo(0x0A5F, 0x008A, "Zebra", "ZT410", USBPrinterType.ZEBRA, "Zebra ZT410 Industrial Printer"),
    USBPrinterInfo(0x0A5F, 0x0078, "Zebra", "GK420d", USBPrinterType.ZEBRA, "Zebra GK420d Direct Thermal Printer"),
    USBPrinterInfo(0x0A5F, 0x0166, "Zebra", "ZT411", USBPrinterType.ZEBRA, "Zebra ZT411 Industrial Printer"),
    
    # Brother printers  
    USBPrinterInfo(0x04F9, 0x2028, "Brother", "QL-700", USBPrinterType.BROTHER, "Brother QL-700 Label Printer"),
    USBPrinterInfo(0x04F9, 0x202A, "Brother", "QL-710W", USBPrinterType.BROTHER, "Brother QL-710W Label Printer"),
    USBPrinterInfo(0x04F9, 0x202B, "Brother", "QL-720NW", USBPrinterType.BROTHER, "Brother QL-720NW Label Printer"),
    USBPrinterInfo(0x04F9, 0x209D, "Brother", "QL-820NWB", USBPrinterType.BROTHER, "Brother QL-820NWB Label Printer"),
    USBPrinterInfo(0x04F9, 0x2100, "Brother", "QL-800", USBPrinterType.BROTHER, "Brother QL-800 Label Printer"),
    
    # Epson printers
    USBPrinterInfo(0x04B8, 0x0202, "Epson", "TM-T20", USBPrinterType.EPSON, "Epson TM-T20 Receipt Printer"),
    USBPrinterInfo(0x04B8, 0x0204, "Epson", "TM-T88V", USBPrinterType.EPSON, "Epson TM-T88V Receipt Printer"),
    USBPrinterInfo(0x04B8, 0x0203, "Epson", "TM-T88", USBPrinterType.EPSON, "Epson TM-T88 Receipt Printer"),
]


class DirectUSBPrinter:
    """
    Direct USB printer interface that communicates directly with USB printers
    without using COM ports or serial communication.
    
    Based on the implementation in main.py for direct USB communication.
    """
    
    def __init__(self, vendor_id: Optional[int] = None, product_id: Optional[int] = None, auto_detect: bool = True):
        """
        Initialize USB printer interface
        
        Args:
            vendor_id: USB Vendor ID (e.g., 0x0A5F for Zebra)
            product_id: USB Product ID (e.g., 0x0164 for ZD410/ZD420)
            auto_detect: Auto-detect printer if vendor/product ID not specified
        """
        if not USB_AVAILABLE:
            raise ImportError("PyUSB is required for USB printer communication")
        
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.auto_detect = auto_detect
        self.device: Optional[usb.core.Device] = None
        self.printer_info: Optional[USBPrinterInfo] = None
        self.endpoint_out = None
        self.is_connected = False
        
        logger.info("DirectUSBPrinter initialized")
    
    @staticmethod
    def list_available_printers() -> List[Dict[str, Any]]:
        """
        List all available USB printers
        
        Returns:
            List of available printer information
        """
        if not USB_AVAILABLE:
            logger.error("PyUSB not available")
            return []
        
        available_printers = []
        
        for printer_info in KNOWN_USB_PRINTERS:
            try:
                device = usb.core.find(idVendor=printer_info.vendor_id, idProduct=printer_info.product_id)
                if device is not None:
                    available_printers.append({
                        'vendor_id': printer_info.vendor_id,
                        'product_id': printer_info.product_id,
                        'manufacturer': printer_info.manufacturer,
                        'model': printer_info.model,
                        'type': printer_info.printer_type.value,
                        'description': printer_info.description,
                        'connected': True
                    })
            except Exception as e:
                logger.debug(f"Error checking printer {printer_info.manufacturer} {printer_info.model}: {e}")
        
        return available_printers
    
    def connect(self) -> bool:
        """
        Connect to USB printer
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if self.vendor_id and self.product_id:
                # Connect to specific printer
                self.device = usb.core.find(idVendor=self.vendor_id, idProduct=self.product_id)
                if self.device is None:
                    logger.error(f"Printer with Vendor ID 0x{self.vendor_id:04X} and Product ID 0x{self.product_id:04X} not found")
                    return False
            elif self.auto_detect:
                # Auto-detect first available printer
                for printer_info in KNOWN_USB_PRINTERS:
                    device = usb.core.find(idVendor=printer_info.vendor_id, idProduct=printer_info.product_id)
                    if device is not None:
                        self.device = device
                        self.vendor_id = printer_info.vendor_id
                        self.product_id = printer_info.product_id
                        self.printer_info = printer_info
                        logger.info(f"Auto-detected printer: {printer_info.manufacturer} {printer_info.model}")
                        break
                
                if self.device is None:
                    logger.error("No supported USB printers found")
                    return False
            else:
                logger.error("No printer specified and auto-detect disabled")
                return False
            
            # Set the active configuration
            try:
                self.device.set_configuration()
            except usb.core.USBError as e:
                logger.warning(f"Could not set configuration: {e}")
            
            # Find the OUT endpoint
            self.endpoint_out = None
            for cfg in self.device:
                for intf in cfg:
                    for ep in intf:
                        # Look for bulk OUT endpoint (typically 0x01)
                        if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT:
                            if usb.util.endpoint_type(ep.bmAttributes) == usb.util.ENDPOINT_TYPE_BULK:
                                self.endpoint_out = ep
                                break
                    if self.endpoint_out:
                        break
                if self.endpoint_out:
                    break
            
            if self.endpoint_out is None:
                logger.error("OUT endpoint not found")
                return False
            
            self.is_connected = True
            logger.info(f"Connected to USB printer (Vendor: 0x{self.vendor_id:04X}, Product: 0x{self.product_id:04X})")
            logger.info(f"Using endpoint address: 0x{self.endpoint_out.bEndpointAddress:02X}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to USB printer: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from USB printer"""
        if self.device:
            try:
                usb.util.release_interface(self.device, 0)
                logger.info("USB interface released")
            except Exception as e:
                logger.warning(f"Error releasing USB interface: {e}")
        
        self.device = None
        self.endpoint_out = None
        self.is_connected = False
        logger.info("Disconnected from USB printer")
    
    def send_zpl_command(self, zpl_command: str) -> bool:
        """
        Send ZPL command to printer (based on main.py implementation)
        
        Args:
            zpl_command: ZPL command string to send
            
        Returns:
            True if command sent successfully, False otherwise
        """
        if not self.is_connected or not self.device or not self.endpoint_out:
            logger.error("Printer not connected")
            return False
        
        try:
            # Send data to the OUT endpoint
            self.device.write(self.endpoint_out.bEndpointAddress, zpl_command.encode('utf-8'), timeout=1000)
            logger.info("ZPL command sent successfully")
            
            # Add a small delay as in main.py
            time.sleep(1)
            
            return True
            
        except usb.core.USBError as e:
            logger.error(f"Error sending ZPL command: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending ZPL command: {e}")
            return False
    
    def send_raw_command(self, command: str) -> bool:
        """
        Send raw command to printer
        
        Args:
            command: Raw command string to send
            
        Returns:
            True if command sent successfully, False otherwise
        """
        return self.send_zpl_command(command)
    
    def send_bytes(self, data: bytes) -> bool:
        """
        Send raw bytes to printer
        
        Args:
            data: Raw bytes to send
            
        Returns:
            True if data sent successfully, False otherwise
        """
        if not self.is_connected or not self.device or not self.endpoint_out:
            logger.error("Printer not connected")
            return False
        
        try:
            self.device.write(self.endpoint_out.bEndpointAddress, data, timeout=1000)
            logger.info("Raw bytes sent successfully")
            time.sleep(1)
            return True
            
        except usb.core.USBError as e:
            logger.error(f"Error sending raw bytes: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending raw bytes: {e}")
            return False
    
    def get_printer_info(self) -> Optional[Dict[str, Any]]:
        """
        Get printer information
        
        Returns:
            Dictionary with printer information or None if not connected
        """
        if not self.is_connected:
            return None
        
        info = {
            'vendor_id': self.vendor_id,
            'product_id': self.product_id,
            'connected': self.is_connected,
            'endpoint_address': f"0x{self.endpoint_out.bEndpointAddress:02X}" if self.endpoint_out else None
        }
        
        if self.printer_info:
            info.update({
                'manufacturer': self.printer_info.manufacturer,
                'model': self.printer_info.model,
                'type': self.printer_info.printer_type.value,
                'description': self.printer_info.description
            })
        
        return info
    
    def test_connection(self) -> bool:
        """
        Test printer connection by sending a simple ZPL command
        
        Returns:
            True if test successful, False otherwise
        """
        if not self.is_connected:
            return False
        
        # Send a simple ZPL configuration command (host status)
        test_command = "~HS"
        return self.send_zpl_command(test_command)


def send_zpl_to_printer_via_usb(zpl_command: str, vendor_id: int = 0x0A5F, product_id: int = 0x0164) -> bool:
    """
    Convenience function to send ZPL command directly to USB printer
    (Compatible with main.py implementation)
    
    Args:
        zpl_command: ZPL command to send
        vendor_id: USB Vendor ID (default: Zebra 0x0A5F)
        product_id: USB Product ID (default: ZD410/ZD420 0x0164)
        
    Returns:
        True if successful, False otherwise
    """
    printer = DirectUSBPrinter(vendor_id=vendor_id, product_id=product_id, auto_detect=False)
    
    try:
        if printer.connect():
            result = printer.send_zpl_command(zpl_command)
            printer.disconnect()
            return result
        else:
            logger.error("Could not connect to printer")
            return False
    except Exception as e:
        logger.error(f"Error in send_zpl_to_printer_via_usb: {e}")
        return False


if __name__ == "__main__":
    # Test the direct USB printer interface
    logging.basicConfig(level=logging.INFO)
    
    print("Available USB printers:")
    printers = DirectUSBPrinter.list_available_printers()
    for i, printer in enumerate(printers):
        print(f"{i+1}. {printer['manufacturer']} {printer['model']} (VID: 0x{printer['vendor_id']:04X}, PID: 0x{printer['product_id']:04X})")
    
    if printers:
        # Test connection to first available printer
        printer = DirectUSBPrinter(auto_detect=True)
        if printer.connect():
            info = printer.get_printer_info()
            print(f"\nConnected to: {info}")
            
            # Test with a simple ZPL command
            test_zpl = "^XA^FO50,50^A0N,50,50^FDTest Print^FS^XZ"
            if printer.send_zpl_command(test_zpl):
                print("Test print sent successfully")
            else:
                print("Failed to send test print")
            
            printer.disconnect()
        else:
            print("Failed to connect to printer")
    else:
        print("No USB printers found")
