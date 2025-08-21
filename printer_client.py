"""
Label Printer WebSocket Client
=============================

WebSocket client that connects to the Node.js server and handles print jobs
by sending commands to thermal printers via serial port.

Features:
- WebSocket connection to print server
- Serial port communication with thermal printers
- Support for different label formats (location, pallet, test)
- Automatic printer registration and health monitoring
- Error handling and reconnection logic

Author: Your Name
Version: 1.0.0
"""

import asyncio
import json
import logging
import serial
import serial.tools.list_ports
import socketio
import time
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

# Try to import USB support
try:
    from usb_printer import USBPrinterInterface, USBPrinterType
    USB_SUPPORT = True
except ImportError:
    USB_SUPPORT = False
    logging.warning("USB printer support not available. Install pyusb for USB support.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PrinterConnectionType(Enum):
    """Printer connection types"""
    SERIAL = "serial"
    USB = "usb"
    AUTO = "auto"


class PrinterType(Enum):
    """Supported printer types"""
    LABEL = "label"
    THERMAL = "thermal"
    LASER = "laser"
    ZEBRA = "zebra"


class LabelTemplate(Enum):
    """Supported label templates"""
    LOCATION = "location_label"
    PALLET = "pallet_label"
    TEST = "test_label"


@dataclass
class PrinterConfig:
    """Printer configuration"""
    printer_id: str
    printer_name: str
    printer_type: PrinterType
    location: str
    connection_type: PrinterConnectionType = PrinterConnectionType.AUTO
    serial_port: Optional[str] = None
    baud_rate: int = 9600
    timeout: float = 1.0
    usb_vendor_id: Optional[int] = None
    usb_product_id: Optional[int] = None


@dataclass
class PrintJob:
    """Print job data structure"""
    job_id: str
    label_data: Dict[str, Any]
    timestamp: str
    requested_by: Optional[str] = None


class PrinterInterface:
    """Unified interface for both serial and USB printers"""
    
    def __init__(self, config: PrinterConfig):
        self.config = config
        self.serial_interface: Optional[SerialPrinterInterface] = None
        self.usb_interface: Optional[USBPrinterInterface] = None
        self.connection_type: Optional[PrinterConnectionType] = None
        self.is_connected = False
    
    def connect(self) -> bool:
        """Connect to printer using the best available method"""
        if self.config.connection_type == PrinterConnectionType.SERIAL:
            return self._connect_serial()
        elif self.config.connection_type == PrinterConnectionType.USB:
            return self._connect_usb()
        elif self.config.connection_type == PrinterConnectionType.AUTO:
            # Try USB first, then fallback to serial
            if USB_SUPPORT and self._connect_usb():
                return True
            elif self.config.serial_port and self._connect_serial():
                return True
            else:
                logger.error("Could not connect using any method")
                return False
        else:
            logger.error(f"Unknown connection type: {self.config.connection_type}")
            return False
    
    def _connect_usb(self) -> bool:
        """Connect via USB"""
        if not USB_SUPPORT:
            logger.warning("USB support not available")
            return False
        
        try:
            if self.config.usb_vendor_id and self.config.usb_product_id:
                # Use specific vendor/product ID
                self.usb_interface = USBPrinterInterface(
                    self.config.usb_vendor_id, 
                    self.config.usb_product_id, 
                    auto_detect=False
                )
            else:
                # Auto-detect
                self.usb_interface = USBPrinterInterface(auto_detect=True)
            
            if self.usb_interface.connect():
                self.connection_type = PrinterConnectionType.USB
                self.is_connected = True
                logger.info("Connected via USB")
                return True
            else:
                logger.warning("USB connection failed")
                return False
                
        except Exception as e:
            logger.warning(f"USB connection error: {e}")
            return False
    
    def _connect_serial(self) -> bool:
        """Connect via serial port"""
        if not self.config.serial_port:
            logger.warning("No serial port specified")
            return False
        
        try:
            self.serial_interface = SerialPrinterInterface(
                self.config.serial_port,
                self.config.baud_rate,
                self.config.timeout
            )
            
            if self.serial_interface.connect():
                self.connection_type = PrinterConnectionType.SERIAL
                self.is_connected = True
                logger.info(f"Connected via serial port: {self.config.serial_port}")
                return True
            else:
                logger.warning("Serial connection failed")
                return False
                
        except Exception as e:
            logger.warning(f"Serial connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from printer"""
        if self.usb_interface:
            self.usb_interface.disconnect()
            self.usb_interface = None
        
        if self.serial_interface:
            self.serial_interface.disconnect()
            self.serial_interface = None
        
        self.connection_type = None
        self.is_connected = False
    
    def send_command(self, command: str) -> bool:
        """Send command to printer"""
        if not self.is_connected:
            logger.error("Printer not connected")
            return False
        
        if self.connection_type == PrinterConnectionType.USB and self.usb_interface:
            return self.usb_interface.send_command(command)
        elif self.connection_type == PrinterConnectionType.SERIAL and self.serial_interface:
            return self.serial_interface.send_command(command)
        else:
            logger.error("No active connection")
            return False
    
    def send_raw_bytes(self, data: bytes) -> bool:
        """Send raw bytes to printer"""
        if not self.is_connected:
            logger.error("Printer not connected")
            return False
        
        if self.connection_type == PrinterConnectionType.USB and self.usb_interface:
            return self.usb_interface.send_raw_bytes(data)
        elif self.connection_type == PrinterConnectionType.SERIAL and self.serial_interface:
            return self.serial_interface.send_raw_bytes(data)
        else:
            logger.error("No active connection")
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information"""
        info = {
            'connected': self.is_connected,
            'connection_type': self.connection_type.value if self.connection_type else None,
            'printer_config': {
                'id': self.config.printer_id,
                'name': self.config.printer_name,
                'type': self.config.printer_type.value,
                'location': self.config.location
            }
        }
        
        if self.connection_type == PrinterConnectionType.USB and self.usb_interface:
            usb_info = self.usb_interface.get_printer_info()
            if usb_info:
                info['usb_info'] = usb_info
        elif self.connection_type == PrinterConnectionType.SERIAL and self.serial_interface:
            info['serial_info'] = {
                'port': self.config.serial_port,
                'baud_rate': self.config.baud_rate,
                'timeout': self.config.timeout
            }
        
        return info


class SerialPrinterInterface:
    """Interface for serial communication with thermal printers"""
    
    def __init__(self, port: str, baud_rate: int = 9600, timeout: float = 1.0):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.connection: Optional[serial.Serial] = None
        
    def connect(self) -> bool:
        """Connect to the serial port"""
        try:
            self.connection = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=self.timeout
            )
            logger.info(f"Connected to printer on {self.port}")
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to connect to {self.port}: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the serial port"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.info(f"Disconnected from {self.port}")
    
    def send_command(self, command: str) -> bool:
        """Send command to printer"""
        if not self.connection or not self.connection.is_open:
            logger.error("Printer not connected")
            return False
        
        try:
            self.connection.write(command.encode('utf-8'))
            logger.debug(f"Sent command: {command.strip()}")
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to send command: {e}")
            return False
    
    def send_raw_bytes(self, data: bytes) -> bool:
        """Send raw bytes to printer"""
        if not self.connection or not self.connection.is_open:
            logger.error("Printer not connected")
            return False
        
        try:
            self.connection.write(data)
            logger.debug(f"Sent {len(data)} bytes to printer")
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to send raw data: {e}")
            return False


class LabelGenerator:
    """Generate printer-specific label commands"""
    
    @staticmethod
    def generate_location_label(data: Dict[str, Any]) -> str:
        """Generate ESC/POS commands for location label"""
        commands = []
        
        # Initialize printer
        commands.append("\x1B\x40")  # ESC @ - Initialize printer
        
        # Set font size
        commands.append("\x1B\x21\x30")  # ESC ! 0 - Normal font
        
        # Center alignment
        commands.append("\x1B\x61\x01")  # ESC a 1 - Center align
        
        # Print header
        commands.append("LOCATION LABEL\n")
        commands.append("=" * 32 + "\n")
        
        # Left alignment for data
        commands.append("\x1B\x61\x00")  # ESC a 0 - Left align
        
        # Print barcode (if supported)
        barcode = data.get('barcode', '')
        if barcode:
            commands.append(f"Barcode: {barcode}\n")
        
        # Print location data
        commands.append(f"Location: {data.get('locationName', 'N/A')}\n")
        commands.append(f"Warehouse: {data.get('warehouseCode', 'N/A')}\n")
        commands.append(f"Type: {data.get('locationType', 'N/A')}\n")
        
        aisle = data.get('aisle', '')
        bay = data.get('bay', '')
        level = data.get('level', '')
        if aisle or bay or level:
            commands.append(f"Position: {aisle}-{bay}-{level}\n")
        
        max_weight = data.get('maxWeight', '')
        if max_weight:
            commands.append(f"Max Weight: {max_weight} kg\n")
        
        max_volume = data.get('maxVolume', '')
        if max_volume:
            commands.append(f"Max Volume: {max_volume} m³\n")
        
        # Print timestamp
        commands.append("-" * 32 + "\n")
        commands.append(f"Printed: {data.get('printedAt', time.strftime('%Y-%m-%d %H:%M:%S'))}\n")
        
        # Cut paper
        commands.append("\x1D\x56\x42\x00")  # GS V B 0 - Partial cut
        
        return "".join(commands)
    
    @staticmethod
    def generate_pallet_label(data: Dict[str, Any]) -> str:
        """Generate ESC/POS commands for pallet label"""
        commands = []
        
        # Initialize printer
        commands.append("\x1B\x40")  # ESC @ - Initialize printer
        
        # Set font size
        commands.append("\x1B\x21\x30")  # ESC ! 0 - Normal font
        
        # Center alignment
        commands.append("\x1B\x61\x01")  # ESC a 1 - Center align
        
        # Print header
        commands.append("PALLET LABEL\n")
        commands.append("=" * 32 + "\n")
        
        # Left alignment for data
        commands.append("\x1B\x61\x00")  # ESC a 0 - Left align
        
        # Print barcode
        barcode = data.get('barcode', '')
        if barcode:
            commands.append(f"Barcode: {barcode}\n")
        
        # Print pallet data
        commands.append(f"Type: {data.get('palletType', 'N/A')}\n")
        commands.append(f"Status: {data.get('status', 'N/A')}\n")
        commands.append(f"Warehouse: {data.get('warehouseCode', 'N/A')}\n")
        
        current_weight = data.get('currentWeight', 0)
        max_weight = data.get('maxWeight', 0)
        commands.append(f"Weight: {current_weight}/{max_weight} kg\n")
        
        current_volume = data.get('currentVolume', 0)
        max_volume = data.get('maxVolume', 0)
        commands.append(f"Volume: {current_volume}/{max_volume} m³\n")
        
        # Print timestamp
        commands.append("-" * 32 + "\n")
        commands.append(f"Printed: {data.get('printedAt', time.strftime('%Y-%m-%d %H:%M:%S'))}\n")
        
        # Cut paper
        commands.append("\x1D\x56\x42\x00")  # GS V B 0 - Partial cut
        
        return "".join(commands)
    
    @staticmethod
    def generate_test_label(data: Dict[str, Any]) -> str:
        """Generate ESC/POS commands for test label"""
        commands = []
        
        # Initialize printer
        commands.append("\x1B\x40")  # ESC @ - Initialize printer
        
        # Center alignment
        commands.append("\x1B\x61\x01")  # ESC a 1 - Center align
        
        # Large font
        commands.append("\x1B\x21\x30")  # ESC ! 0 - Normal font
        
        # Print test message
        commands.append("TEST LABEL\n")
        commands.append("=" * 20 + "\n")
        commands.append(f"{data.get('message', 'Printer Test')}\n")
        commands.append(f"Time: {data.get('timestamp', time.strftime('%H:%M:%S'))}\n")
        commands.append("=" * 20 + "\n")
        
        # Cut paper
        commands.append("\x1D\x56\x42\x00")  # GS V B 0 - Partial cut
        
        return "".join(commands)


class WebSocketPrinterClient:
    """WebSocket client for printer communication"""
    
    def __init__(self, config: PrinterConfig, server_url: str = "http://192.168.1.139:25625"):
        self.config = config
        self.server_url = server_url
        self.sio = socketio.AsyncClient()
        self.printer_interface = PrinterInterface(config)
        self.label_generator = LabelGenerator()
        self.is_connected = False
        self.setup_event_handlers()
    
    def setup_event_handlers(self):
        """Setup WebSocket event handlers"""
        
        @self.sio.event
        async def connect():
            logger.info("Connected to WebSocket server")
            await self.register_printer()
        
        @self.sio.event
        async def disconnect():
            logger.info("Disconnected from WebSocket server")
            self.is_connected = False
        
        @self.sio.event
        async def registration_success(data):
            logger.info(f"Printer registered successfully: {data}")
            self.is_connected = True
        
        @self.sio.event
        async def registration_error(data):
            logger.error(f"Printer registration failed: {data}")
        
        @self.sio.event
        async def print_job(data):
            logger.info(f"Received print job: {data.get('jobId', 'unknown')}")
            
            # Extract template and data from new backend format
            template = data.get('template', 'test_label')
            print_data = data.get('data', {})
            
            # Create job object with template info
            job = PrintJob(
                job_id=data.get('jobId', f"job_{int(time.time())}"),
                label_data={
                    'template': template,
                    **print_data
                },
                timestamp=data.get('timestamp', time.strftime('%Y-%m-%d %H:%M:%S')),
                requested_by=data.get('requestedBy')
            )
            await self.process_print_job(job)
        
        @self.sio.event
        async def ping():
            await self.sio.emit('pong')
        
        @self.sio.event
        async def printer_list_updated(data):
            logger.info(f"Printer list updated: {len(data)} printers connected")
    
    async def register_printer(self):
        """Register this printer with the server"""
        registration_data = {
            'printerId': self.config.printer_id,
            'printerName': self.config.printer_name,
            'printerType': self.config.printer_type.value,
            'location': self.config.location
        }
        await self.sio.emit('register_printer', registration_data)
    
    async def process_print_job(self, job: PrintJob):
        """Process a print job based on template type"""
        try:
            template = job.label_data.get('template', 'test_label')
            logger.info(f"Processing job {job.job_id} with template: {template}")
            
            if template == 'pallet_label':
                # ZPL thermal label printing only
                await self._process_thermal_label(job)
                
            elif template == 'pallet_content_list_a5':
                # A5 summary printing to default printer only
                await self._process_a5_summary(job)
                
            elif template in [LabelTemplate.LOCATION.value, LabelTemplate.TEST.value]:
                # Legacy ESC/POS thermal printing
                await self._process_thermal_label(job)
                
            else:
                raise ValueError(f"Unknown template: {template}")
                
        except Exception as e:
            logger.error(f"Error processing print job {job.job_id}: {e}")
            result = {
                'success': False,
                'error': str(e)
            }
            await self.sio.emit(f'print_result_{job.job_id}', result)
    
    async def _process_thermal_label(self, job: PrintJob):
        """Process thermal label printing (ZPL or ESC/POS)"""
        try:
            template = job.label_data.get('template', 'test_label')
            
            # Generate label commands based on template
            if template == 'pallet_label':
                # Use ZPL commands for pallet labels
                commands = self._generate_zpl_pallet_label(job.label_data)
            elif template == LabelTemplate.LOCATION.value:
                commands = self.label_generator.generate_location_label(job.label_data)
            elif template == LabelTemplate.TEST.value:
                commands = self.label_generator.generate_test_label(job.label_data)
            else:
                # Default to pallet label for unknown thermal templates
                commands = self.label_generator.generate_pallet_label(job.label_data)
            
            # Send to thermal printer
            success = self.printer_interface.send_command(commands)
            
            # Send result back to server
            result = {
                'success': success,
                'message': f'Thermal label printed successfully' if success else 'Thermal print job failed'
            }
            
            await self.sio.emit(f'print_result_{job.job_id}', result)
            
            if success:
                logger.info(f"Thermal print job {job.job_id} completed successfully")
            else:
                logger.error(f"Thermal print job {job.job_id} failed")
                
        except Exception as e:
            logger.error(f"Error in thermal printing {job.job_id}: {e}")
            raise
    
    async def _process_a5_summary(self, job: PrintJob):
        """Process A5 summary printing to default printer"""
        try:
            # Generate A5 summary content
            summary_content = self._generate_a5_summary_content(job.label_data)
            
            # Here you would implement the logic to send to default printer
            # This could be platform-specific (Windows, macOS, Linux)
            success = await self._print_to_default_printer(summary_content, job.job_id)
            
            # Send result back to server
            result = {
                'success': success,
                'message': f'A5 summary printed successfully' if success else 'A5 summary print job failed'
            }
            
            await self.sio.emit(f'print_result_{job.job_id}', result)
            
            if success:
                logger.info(f"A5 summary print job {job.job_id} completed successfully")
            else:
                logger.error(f"A5 summary print job {job.job_id} failed")
                
        except Exception as e:
            logger.error(f"Error in A5 summary printing {job.job_id}: {e}")
            raise
    
    def _generate_zpl_pallet_label(self, data: Dict[str, Any]) -> str:
        """Generate ZPL commands for pallet label"""
        zpl_commands = []
        
        # Start ZPL format
        zpl_commands.append("^XA")
        
        # Set label dimensions (adjust as needed)
        zpl_commands.append("^LH0,0")  # Label Home
        
        # Print pallet ID
        pallet_id = data.get('pallet_id', 'Unknown')
        zpl_commands.append(f"^FO50,50^A0N,50,50^FD{pallet_id}^FS")
        
        # Print barcode if available
        barcode = data.get('barcode', pallet_id)
        zpl_commands.append(f"^FO50,120^BY3^BCN,100,Y,N,N^FD{barcode}^FS")
        
        # Print location
        location = data.get('location', 'N/A')
        zpl_commands.append(f"^FO50,250^A0N,30,30^FDLocation: {location}^FS")
        
        # Print timestamp
        timestamp = data.get('timestamp', time.strftime('%Y-%m-%d %H:%M:%S'))
        zpl_commands.append(f"^FO50,300^A0N,25,25^FD{timestamp}^FS")
        
        # End ZPL format
        zpl_commands.append("^XZ")
        
        return "".join(zpl_commands)
    
    def _generate_a5_summary_content(self, data: Dict[str, Any]) -> str:
        """Generate A5 summary content for pallet materials"""
        content = []
        
        # Header
        content.append("PALLET CONTENT SUMMARY")
        content.append("=" * 50)
        content.append("")
        
        # Pallet info
        pallet_id = data.get('pallet_id', 'Unknown')
        content.append(f"Pallet ID: {pallet_id}")
        
        location = data.get('location', 'N/A')
        content.append(f"Location: {location}")
        
        timestamp = data.get('timestamp', time.strftime('%Y-%m-%d %H:%M:%S'))
        content.append(f"Generated: {timestamp}")
        content.append("")
        
        # Materials list
        materials = data.get('materials', [])
        if materials:
            content.append("MATERIALS:")
            content.append("-" * 30)
            
            for i, material in enumerate(materials, 1):
                content.append(f"{i}. {material.get('description', 'Unknown Material')}")
                content.append(f"   Code: {material.get('material_code', 'N/A')}")
                content.append(f"   Quantity: {material.get('quantity', 0)} {material.get('unit', 'pcs')}")
                content.append("")
        else:
            content.append("No materials found")
        
        content.append("=" * 50)
        
        return "\n".join(content)
    
    async def _print_to_default_printer(self, content: str, job_id: str) -> bool:
        """Print content to default system printer (A5 format)"""
        try:
            import platform
            import tempfile
            import os
            import subprocess
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            # Platform-specific printing
            system = platform.system()
            
            if system == "Windows":
                # Windows printing
                subprocess.run(['notepad', '/p', temp_file_path], check=True)
                success = True
            elif system == "Darwin":  # macOS
                # macOS printing with lpr
                subprocess.run(['lpr', '-P', 'default', temp_file_path], check=True)
                success = True
            elif system == "Linux":
                # Linux printing with lp
                subprocess.run(['lp', '-d', 'default', temp_file_path], check=True)
                success = True
            else:
                logger.warning(f"Unsupported platform for default printing: {system}")
                success = False
            
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
            
            return success
            
        except Exception as e:
            logger.error(f"Error printing to default printer: {e}")
            return False
    
    async def connect_to_server(self):
        """Connect to WebSocket server"""
        try:
            await self.sio.connect(self.server_url)
            logger.info(f"Connected to server at {self.server_url}")
        except Exception as e:
            logger.error(f"Failed to connect to server: {e}")
            raise
    
    async def disconnect_from_server(self):
        """Disconnect from WebSocket server"""
        await self.sio.disconnect()
    
    def connect_to_printer(self) -> bool:
        """Connect to the serial printer"""
        return self.printer_interface.connect()
    
    def disconnect_from_printer(self):
        """Disconnect from the serial printer"""
        self.printer_interface.disconnect()
    
    async def start(self):
        """Start the client"""
        logger.info("Starting WebSocket Printer Client...")
        
        # Connect to printer
        if not self.connect_to_printer():
            logger.error("Failed to connect to printer. Exiting.")
            return False
        
        # Connect to server
        try:
            await self.connect_to_server()
            
            # Keep the client running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        except Exception as e:
            logger.error(f"Client error: {e}")
        finally:
            await self.disconnect_from_server()
            self.disconnect_from_printer()
        
        return True


def list_serial_ports():
    """List available serial ports"""
    ports = serial.tools.list_ports.comports()
    print("Available serial ports:")
    for i, port in enumerate(ports):
        print(f"  {i}: {port.device} - {port.description}")
    return [port.device for port in ports]


def list_usb_printers():
    """List available USB printers"""
    if not USB_SUPPORT:
        print("USB support not available. Install pyusb for USB printer support.")
        return []
    
    try:
        from usb_printer import USBPrinterInterface
        printers = USBPrinterInterface.list_usb_printers()
        print("Available USB printers:")
        for i, printer in enumerate(printers):
            print(f"  {i}: {printer['description']} (VID: 0x{printer['vendor_id']:04X}, PID: 0x{printer['product_id']:04X})")
        return printers
    except Exception as e:
        print(f"Error listing USB printers: {e}")
        return []


def list_all_printers():
    """List both serial and USB printers"""
    print("🔍 Searching for printers...")
    print("=" * 50)
    
    # List serial ports
    serial_ports = list_serial_ports()
    
    print()
    
    # List USB printers
    usb_printers = list_usb_printers()
    
    return {
        'serial': serial_ports,
        'usb': usb_printers
    }


async def main():
    """Main function"""
    print("Label Printer WebSocket Client")
    print("=" * 40)
    
    # List available printers
    available_printers = list_all_printers()
    
    if not available_printers['serial'] and not available_printers['usb']:
        print("No printers found. Please check your printer connections.")
        return
    
    # Get user input for configuration
    print("\nEnter printer configuration:")
    
    printer_id = input("Printer ID (e.g., PRINTER_001): ").strip() or "PRINTER_001"
    printer_name = input("Printer Name (e.g., Main Printer): ").strip() or "Main Printer"
    location = input("Location (e.g., Warehouse A): ").strip() or "Warehouse A"
    
    # Connection type selection
    print("\nSelect connection type:")
    print("  1: Auto (try USB first, then serial)")
    print("  2: USB only")
    print("  3: Serial only")
    
    connection_choice = input("Connection type (1-3) [1]: ").strip() or "1"
    
    if connection_choice == "1":
        connection_type = PrinterConnectionType.AUTO
    elif connection_choice == "2":
        connection_type = PrinterConnectionType.USB
    elif connection_choice == "3":
        connection_type = PrinterConnectionType.SERIAL
    else:
        print("Invalid choice, using auto")
        connection_type = PrinterConnectionType.AUTO
    
    # Configure based on connection type
    serial_port = None
    usb_vendor_id = None
    usb_product_id = None
    baud_rate = 9600
    
    if connection_type in [PrinterConnectionType.SERIAL, PrinterConnectionType.AUTO]:
        if available_printers['serial']:
            print(f"\nSelect serial port (0-{len(available_printers['serial'])-1}):")
            try:
                port_index = int(input("Port index: ").strip())
                if 0 <= port_index < len(available_printers['serial']):
                    serial_port = available_printers['serial'][port_index]
                else:
                    print("Invalid port index, using first available port")
                    serial_port = available_printers['serial'][0]
            except ValueError:
                print("Invalid input, using first available port")
                serial_port = available_printers['serial'][0]
            
            baud_input = input("Baud rate (default 9600): ").strip()
            try:
                baud_rate = int(baud_input) if baud_input else 9600
            except ValueError:
                baud_rate = 9600
    
    if connection_type in [PrinterConnectionType.USB, PrinterConnectionType.AUTO]:
        if available_printers['usb']:
            print(f"\nSelect USB printer (0-{len(available_printers['usb'])-1}) or press Enter to auto-detect:")
            usb_choice = input("USB printer index: ").strip()
            if usb_choice:
                try:
                    usb_index = int(usb_choice)
                    if 0 <= usb_index < len(available_printers['usb']):
                        usb_printer = available_printers['usb'][usb_index]
                        usb_vendor_id = usb_printer['vendor_id']
                        usb_product_id = usb_printer['product_id']
                        print(f"Selected: {usb_printer['description']}")
                    else:
                        print("Invalid index, will auto-detect")
                except ValueError:
                    print("Invalid input, will auto-detect")
    
    server_url = input("Server URL (default http://192.168.1.139:25625): ").strip() or "http://192.168.1.139:25625"
    
    # Determine printer type based on selection
    printer_type = PrinterType.THERMAL
    if available_printers['usb']:
        for printer in available_printers['usb']:
            if printer.get('type') == 'zebra':
                printer_type = PrinterType.ZEBRA
                break
    
    # Create printer configuration
    config = PrinterConfig(
        printer_id=printer_id,
        printer_name=printer_name,
        printer_type=printer_type,
        location=location,
        connection_type=connection_type,
        serial_port=serial_port,
        baud_rate=baud_rate,
        usb_vendor_id=usb_vendor_id,
        usb_product_id=usb_product_id
    )
    
    print(f"\nConfiguration:")
    print(f"  Printer ID: {config.printer_id}")
    print(f"  Printer Name: {config.printer_name}")
    print(f"  Printer Type: {config.printer_type.value}")
    print(f"  Location: {config.location}")
    print(f"  Connection Type: {config.connection_type.value}")
    if config.serial_port:
        print(f"  Serial Port: {config.serial_port}")
        print(f"  Baud Rate: {config.baud_rate}")
    if config.usb_vendor_id and config.usb_product_id:
        print(f"  USB: VID 0x{config.usb_vendor_id:04X}, PID 0x{config.usb_product_id:04X}")
    print(f"  Server URL: {server_url}")
    
    input("\nPress Enter to start the client...")
    
    # Create and start client
    client = WebSocketPrinterClient(config, server_url)
    await client.start()


if __name__ == "__main__":
    asyncio.run(main())
