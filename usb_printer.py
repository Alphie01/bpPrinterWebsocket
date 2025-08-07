"""
USB Printer Interface for direct USB communication with printers
Supports Zebra printers and other USB-based thermal printers
"""

import logging
import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

try:
    import usb.core
    import usb.util
    USB_AVAILABLE = True
except ImportError:
    USB_AVAILABLE = False
    logging.warning("PyUSB not available. USB printer support disabled.")

logger = logging.getLogger(__name__)


class USBPrinterType(Enum):
    """Known USB printer types"""
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
    product: str
    printer_type: USBPrinterType
    description: str


# Known USB printers database
KNOWN_USB_PRINTERS = [
    # Zebra printers
    USBPrinterInfo(0x0A5F, 0x0164, "Zebra", "ZD410", USBPrinterType.ZEBRA, "Zebra ZD410 Direct Thermal Printer"),
    USBPrinterInfo(0x0A5F, 0x0161, "Zebra", "ZD420", USBPrinterType.ZEBRA, "Zebra ZD420 Direct Thermal Printer"),
    USBPrinterInfo(0x0A5F, 0x0078, "Zebra", "GK420d", USBPrinterType.ZEBRA, "Zebra GK420d Direct Thermal Printer"),
    USBPrinterInfo(0x0A5F, 0x0166, "Zebra", "ZT411", USBPrinterType.ZEBRA, "Zebra ZT411 Industrial Printer"),
    
    # Epson printers
    USBPrinterInfo(0x04B8, 0x0202, "Epson", "TM-T20", USBPrinterType.EPSON, "Epson TM-T20 Receipt Printer"),
    USBPrinterInfo(0x04B8, 0x0203, "Epson", "TM-T88", USBPrinterType.EPSON, "Epson TM-T88 Receipt Printer"),
    
    # Brother printers
    USBPrinterInfo(0x04F9, 0x209D, "Brother", "QL-820NWB", USBPrinterType.BROTHER, "Brother QL-820NWB Label Printer"),
    USBPrinterInfo(0x04F9, 0x2100, "Brother", "QL-800", USBPrinterType.BROTHER, "Brother QL-800 Label Printer"),
]


class USBPrinterInterface:
    """Interface for USB communication with printers"""
    
    def __init__(self, vendor_id: int = None, product_id: int = None, auto_detect: bool = True):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.auto_detect = auto_detect
        self.device: Optional[usb.core.Device] = None
        self.printer_info: Optional[USBPrinterInfo] = None
        self.endpoint_out = None
        self.is_connected = False
        
        if not USB_AVAILABLE:
            raise ImportError("PyUSB not available. Install with: pip install pyusb")
    
    @staticmethod
    def list_usb_printers() -> List[Dict[str, Any]]:
        """List all available USB printers"""
        if not USB_AVAILABLE:
            return []
        
        found_printers = []
        
        for printer_info in KNOWN_USB_PRINTERS:
            device = usb.core.find(idVendor=printer_info.vendor_id, idProduct=printer_info.product_id)
            if device is not None:
                found_printers.append({
                    'vendor_id': printer_info.vendor_id,
                    'product_id': printer_info.product_id,
                    'manufacturer': printer_info.manufacturer,
                    'product': printer_info.product,
                    'type': printer_info.printer_type.value,
                    'description': printer_info.description,
                    'device': device
                })
        
        # Also check for generic USB devices that might be printers
        devices = usb.core.find(find_all=True)
        for device in devices:
            # Check if it's a printer class device (class 7)
            try:
                if device.bDeviceClass == 7:  # Printer class
                    # Check if not already in our known list
                    if not any(p['vendor_id'] == device.idVendor and p['product_id'] == device.idProduct 
                              for p in found_printers):
                        try:
                            manufacturer = usb.util.get_string(device, device.iManufacturer) if device.iManufacturer else "Unknown"
                            product = usb.util.get_string(device, device.iProduct) if device.iProduct else "Unknown"
                        except:
                            manufacturer = "Unknown"
                            product = "Unknown"
                        
                        found_printers.append({
                            'vendor_id': device.idVendor,
                            'product_id': device.idProduct,
                            'manufacturer': manufacturer,
                            'product': product,
                            'type': 'generic',
                            'description': f"Generic USB Printer ({manufacturer} {product})",
                            'device': device
                        })
            except:
                continue
        
        return found_printers
    
    @staticmethod
    def find_zebra_printer() -> Optional['USBPrinterInterface']:
        """Find and create interface for Zebra printer (legacy compatibility)"""
        zebra_printers = [p for p in KNOWN_USB_PRINTERS if p.printer_type == USBPrinterType.ZEBRA]
        
        for printer_info in zebra_printers:
            device = usb.core.find(idVendor=printer_info.vendor_id, idProduct=printer_info.product_id)
            if device is not None:
                interface = USBPrinterInterface(printer_info.vendor_id, printer_info.product_id, auto_detect=False)
                interface.printer_info = printer_info
                return interface
        
        return None
    
    def connect(self) -> bool:
        """Connect to USB printer"""
        try:
            if self.auto_detect:
                # Try to find any available printer
                printers = self.list_usb_printers()
                if not printers:
                    logger.error("No USB printers found")
                    return False
                
                # Use the first available printer
                printer_data = printers[0]
                self.vendor_id = printer_data['vendor_id']
                self.product_id = printer_data['product_id']
                self.device = printer_data['device']
                
                # Find printer info
                for info in KNOWN_USB_PRINTERS:
                    if info.vendor_id == self.vendor_id and info.product_id == self.product_id:
                        self.printer_info = info
                        break
                
                logger.info(f"Auto-detected printer: {printer_data['description']}")
            else:
                # Use specified vendor/product ID
                if not self.vendor_id or not self.product_id:
                    logger.error("Vendor ID and Product ID must be specified when auto_detect is False")
                    return False
                
                self.device = usb.core.find(idVendor=self.vendor_id, idProduct=self.product_id)
                if self.device is None:
                    logger.error(f"USB printer not found (VID: 0x{self.vendor_id:04X}, PID: 0x{self.product_id:04X})")
                    return False
            
            # Configure the device
            try:
                # Detach kernel driver if active
                if self.device.is_kernel_driver_active(0):
                    self.device.detach_kernel_driver(0)
                    logger.debug("Detached kernel driver")
                
                # Set configuration
                self.device.set_configuration()
                logger.debug("USB configuration set")
                
                # Find output endpoint
                cfg = self.device.get_active_configuration()
                intf = cfg[(0, 0)]
                
                # Find bulk out endpoint
                self.endpoint_out = usb.util.find_descriptor(
                    intf,
                    custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
                )
                
                if self.endpoint_out is None:
                    logger.error("Output endpoint not found")
                    return False
                
                self.is_connected = True
                logger.info(f"Successfully connected to USB printer (VID: 0x{self.vendor_id:04X}, PID: 0x{self.product_id:04X})")
                return True
                
            except usb.core.USBError as e:
                logger.error(f"USB configuration error: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to connect to USB printer: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from USB printer"""
        if self.device and self.is_connected:
            try:
                usb.util.dispose_resources(self.device)
                logger.info("Disconnected from USB printer")
            except Exception as e:
                logger.warning(f"Error during disconnect: {e}")
        
        self.device = None
        self.endpoint_out = None
        self.is_connected = False
    
    def send_command(self, command: str) -> bool:
        """Send text command to printer"""
        if not self.is_connected or not self.device or not self.endpoint_out:
            logger.error("Printer not connected")
            return False
        
        try:
            data = command.encode('utf-8')
            bytes_written = self.device.write(self.endpoint_out.bEndpointAddress, data, timeout=5000)
            logger.debug(f"Sent {bytes_written} bytes to USB printer")
            return True
            
        except usb.core.USBError as e:
            logger.error(f"Failed to send command to USB printer: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending command: {e}")
            return False
    
    def send_raw_bytes(self, data: bytes) -> bool:
        """Send raw bytes to printer"""
        if not self.is_connected or not self.device or not self.endpoint_out:
            logger.error("Printer not connected")
            return False
        
        try:
            bytes_written = self.device.write(self.endpoint_out.bEndpointAddress, data, timeout=5000)
            logger.debug(f"Sent {bytes_written} raw bytes to USB printer")
            return True
            
        except usb.core.USBError as e:
            logger.error(f"Failed to send raw data to USB printer: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending raw data: {e}")
            return False
    
    def get_printer_info(self) -> Optional[Dict[str, Any]]:
        """Get printer information"""
        if not self.is_connected or not self.device:
            return None
        
        try:
            info = {
                'vendor_id': f"0x{self.vendor_id:04X}",
                'product_id': f"0x{self.product_id:04X}",
                'manufacturer': usb.util.get_string(self.device, self.device.iManufacturer) if self.device.iManufacturer else "Unknown",
                'product': usb.util.get_string(self.device, self.device.iProduct) if self.device.iProduct else "Unknown",
                'serial': usb.util.get_string(self.device, self.device.iSerialNumber) if self.device.iSerialNumber else "Unknown",
                'bus': self.device.bus,
                'address': self.device.address,
            }
            
            if self.printer_info:
                info.update({
                    'type': self.printer_info.printer_type.value,
                    'description': self.printer_info.description
                })
            
            return info
            
        except Exception as e:
            logger.warning(f"Could not get printer info: {e}")
            return {
                'vendor_id': f"0x{self.vendor_id:04X}",
                'product_id': f"0x{self.product_id:04X}",
                'manufacturer': "Unknown",
                'product': "Unknown"
            }


# Legacy compatibility functions
def find_zebra_printer():
    """Find Zebra printer (legacy compatibility)"""
    return USBPrinterInterface.find_zebra_printer()


def send_zpl_to_printer(printer_interface, zpl_command):
    """Send ZPL command to printer (legacy compatibility)"""
    if isinstance(printer_interface, USBPrinterInterface):
        return printer_interface.send_command(zpl_command)
    else:
        logger.error("Invalid printer interface")
        return False
