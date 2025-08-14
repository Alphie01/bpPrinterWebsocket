"""
USB-Only WebSocket Printer Client
=================================

WebSocket client that connects to the print server and handles print jobs
by sending commands directly to USB printers. This version removes all
COM port (serial) communication dependencies and uses only direct USB communication.

Features:
- WebSocket connection to print server
- Direct USB communication with thermal printers
- Support for different label formats (location, pallet, test)
- Automatic printer registration and health monitoring
- Error handling and reconnection logic
- No COM port dependencies

Author: Copilot
Version: 2.0.0 (USB-Only)
"""

import asyncio
import json
import logging
import socketio
import time
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    logging.warning("python-dotenv not available. Install with: pip install python-dotenv")

# Import our enhanced USB printer interface with auto-recovery
from usb_auto_recovery_printer import USBAutoRecoveryPrinter, USBErrorType
from usb_direct_printer import DirectUSBPrinter, USBPrinterType, KNOWN_USB_PRINTERS
from label_generators import get_label_generator
from pallet_summary_generator import get_pallet_summary_generator

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO to DEBUG for more detailed logging
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
class USBPrinterConfig:
    """USB Printer configuration (simplified, no serial port options)"""
    printer_id: str
    printer_name: str
    printer_type: PrinterType
    location: str
    usb_vendor_id: Optional[int] = None
    usb_product_id: Optional[int] = None
    auto_detect: bool = True


@dataclass
class PrintJob:
    """Print job data structure"""
    job_id: str
    label_data: Dict[str, Any]
    timestamp: str
    requested_by: Optional[str] = None


class USBPrinterInterface:
    """Simplified USB-only printer interface"""
    
    def __init__(self, config: USBPrinterConfig):
        self.config = config
        self.usb_printer: Optional[DirectUSBPrinter] = None
        self.is_connected = False
    
    def connect(self) -> bool:
        """Connect to USB printer"""
        try:
            # Use the enhanced auto-recovery printer
            self.usb_printer = USBAutoRecoveryPrinter(
                vendor_id=self.config.usb_vendor_id,
                product_id=self.config.usb_product_id,
                auto_detect=self.config.auto_detect,
                max_recovery_attempts=3,
                recovery_delay=2.0,
                auto_recovery_enabled=True
            )
            
            if self.usb_printer.connect():
                self.is_connected = True
                logger.info(f"Connected to USB printer: {self.config.printer_name}")
                return True
            else:
                logger.error(f"Failed to connect to USB printer: {self.config.printer_name}")
                return False
                
        except Exception as e:
            logger.error(f"USB connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from printer"""
        if self.usb_printer:
            self.usb_printer.disconnect()
            self.usb_printer = None
        
        self.is_connected = False
        logger.info(f"Disconnected from printer: {self.config.printer_name}")
    
    def send_command(self, command: str) -> bool:
        """Send command to printer"""
        if not self.is_connected or not self.usb_printer:
            logger.error("Printer not connected")
            return False
        
        return self.usb_printer.send_zpl_command(command)
    
    def send_raw_bytes(self, data: bytes) -> bool:
        """Send raw bytes to printer"""
        if not self.is_connected or not self.usb_printer:
            logger.error("Printer not connected")
            return False
        
        return self.usb_printer.send_bytes(data)
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information"""
        info = {
            'connected': self.is_connected,
            'connection_type': 'usb',
            'printer_config': {
                'id': self.config.printer_id,
                'name': self.config.printer_name,
                'type': self.config.printer_type.value,
                'location': self.config.location
            }
        }
        
        if self.is_connected and self.usb_printer:
            usb_info = self.usb_printer.get_printer_info()
            if usb_info:
                info['usb_info'] = usb_info
        
        return info
    
    def test_connection(self) -> bool:
        """Test printer connection"""
        if not self.is_connected or not self.usb_printer:
            return False
        
        return self.usb_printer.test_connection()


class WebSocketPrinterClient:
    """
    WebSocket client for USB printer communication
    Simplified version that only supports USB printers
    """
    
    def __init__(self, server_url: str, printer_config: USBPrinterConfig):
        self.server_url = server_url
        self.printer_config = printer_config
        self.printer: Optional[USBPrinterInterface] = None
        self.sio = socketio.AsyncClient()
        self.is_connected = False
        self.is_registered = False  # Kayıt durumu takibi
        self.registration_attempts = 0
        self.max_registration_attempts = 5
        self.reconnect_delay = 5
        self.max_reconnect_attempts = 10
        self.reconnect_attempts = 0
        
        # Setup event handlers
        self._setup_event_handlers()
        
        logger.info(f"WebSocket Printer Client initialized for: {printer_config.printer_name}")
    
    def _setup_event_handlers(self):
        """Setup WebSocket event handlers"""
        
        @self.sio.event
        async def connect():
            logger.info("Connected to WebSocket server")
            self.is_connected = True
            self.reconnect_attempts = 0
            self.is_registered = False  # Reset kayıt durumu
            self.registration_attempts = 0
            await self._register_printer()
        
        @self.sio.event
        async def disconnect():
            logger.info("Disconnected from WebSocket server")
            self.is_connected = False
            self.is_registered = False
        
        @self.sio.event
        async def connect_error(data):
            logger.error(f"Connection error: {data}")
            self.is_connected = False
            self.is_registered = False
        
        @self.sio.event
        async def registration_success(data):
            """Handle successful printer registration"""
            logger.info(f"✅ Printer registration successful: {data}")
            self.is_registered = True
            self.registration_attempts = 0
        
        @self.sio.event
        async def registration_failed(data):
            """Handle failed printer registration"""
            logger.error(f"❌ Printer registration failed: {data}")
            self.is_registered = False
            await self._retry_registration()
        
        @self.sio.event
        async def registration_error(data):
            """Handle printer registration error"""
            logger.error(f"💥 Printer registration error: {data}")
            self.is_registered = False
            await self._retry_registration()
        
        @self.sio.event
        async def print_job(data):
            """Handle incoming print job"""
            if not self.is_registered:
                logger.warning("Received print job but printer not registered. Attempting to register...")
                await self._register_printer()
                # Wait a bit and check if registered
                await asyncio.sleep(2)
                if not self.is_registered:
                    logger.error("Cannot process print job: printer registration failed")
                    return
            await self._handle_print_job(data)
        
        @self.sio.event
        async def printer_command(data):
            """Handle direct printer commands"""
            if not self.is_registered:
                logger.warning("Received printer command but printer not registered")
                return
            await self._handle_printer_command(data)
        
        @self.sio.event
        async def health_check(data):
            """Handle health check requests"""
            await self._handle_health_check(data)
        
        @self.sio.event
        async def pong():
            """Handle pong response"""
            logger.debug("Pong received from server")
    
    async def _register_printer(self):
        """Register printer with the server"""
        try:
            if not self.is_connected:
                logger.warning("Cannot register printer: not connected to server")
                return
            
            if not self.printer or not self.printer.is_connected:
                logger.warning("Cannot register printer: USB printer not connected")
                return
            
            self.registration_attempts += 1
            logger.info(f"Registering printer (attempt {self.registration_attempts}/{self.max_registration_attempts})...")
            
            printer_info = {
                'printerId': self.printer_config.printer_id,  # Server beklediği format
                'printerName': self.printer_config.printer_name,
                'printerType': self.printer_config.printer_type.value,
                'location': self.printer_config.location,
                'connectionType': 'usb',
                'capabilities': ['zpl', 'thermal', 'label'],
                'status': 'online',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if self.printer and self.printer.is_connected:
                connection_info = self.printer.get_connection_info()
                if connection_info and 'usb_info' in connection_info:
                    printer_info['usbInfo'] = connection_info['usb_info']
            
            await self.sio.emit('register_printer', printer_info)
            logger.info(f"Registration request sent for printer: {self.printer_config.printer_id}")
            
            # Kayıt yanıtını bekleme timeout'u (5 saniye)
            await asyncio.sleep(5)
            if not self.is_registered:
                logger.warning("No registration response received within 5 seconds")
                await self._retry_registration()
            
        except Exception as e:
            logger.error(f"Error registering printer: {e}")
            await self._retry_registration()
    
    async def _retry_registration(self):
        """Retry printer registration"""
        if self.registration_attempts >= self.max_registration_attempts:
            logger.error(f"Max registration attempts ({self.max_registration_attempts}) reached. Giving up.")
            return
        
        logger.info(f"Retrying registration in {self.reconnect_delay} seconds...")
        await asyncio.sleep(self.reconnect_delay)
        
        if self.is_connected:  # Sadece bağlantı varsa yeniden dene
            await self._register_printer()
    
    async def _send_ping(self):
        """Send ping to server to test connection"""
        try:
            if self.is_connected:
                await self.sio.emit('ping')
                logger.debug("Ping sent to server")
        except Exception as e:
            logger.error(f"Error sending ping: {e}")
    
    async def _handle_print_job(self, data):
        """Handle incoming print job"""
        try:
            logger.info(f"Received print job data: {data}")
            
            # Fix field mapping - WebSocket sends camelCase, we need snake_case
            job = PrintJob(
                job_id=data.get('jobId', data.get('job_id', '')),
                label_data=data.get('labelData', data.get('label_data', {})),
                timestamp=data.get('timestamp', ''),
                requested_by=data.get('requested_by', None)
            )
            
            # Also get labelType from top level (WebSocket structure)
            label_type_from_websocket = data.get('labelType', '')
            
            logger.info(f"Created print job: {job.job_id}")
            logger.debug(f"Job label_data: {job.label_data}")
            print(f"Raw WebSocket data: {data}")
            print(f"WebSocket labelType: {label_type_from_websocket}")
            print(f"Mapped job_id: {job.job_id}")
            print(f"Mapped label_data: {job.label_data}")
            
            # Add labelType to label_data for processing
            if label_type_from_websocket and 'type' not in job.label_data:
                job.label_data['type'] = label_type_from_websocket
            
            # Process the print job
            success = await self._process_print_job(job)
            
            # Send response back to server
            response = {
                'job_id': job.job_id,
                'printer_id': self.printer_config.printer_id,
                'status': 'completed' if success else 'failed',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            await self.sio.emit('print_job_result', response)
            
        except Exception as e:
            logger.error(f"Error handling print job: {e}")
    
    async def _process_print_job(self, job: PrintJob) -> bool:
        """Process a print job"""
        try:
            if not self.printer or not self.printer.is_connected:
                logger.error("Printer not connected")
                return False
            
            print(f"Job object: {job}")
            label_data = job.label_data
            print(f"Label data: {label_data}")
            print(f"Label data type: {type(label_data)}")
            print(f"Label data keys: {list(label_data.keys())}")
            print(f"Label data length: {len(label_data)}")
            
            label_type = label_data.get('type', 'auto')
            
            logger.info(f"Processing print job {job.job_id} with type: {label_type}")
            logger.debug(f"Label data received: {label_data}")
            print(f'Detected label_type: {label_type}')
            
            # Check if label_data is empty or has only 'type' field
            if not label_data or (len(label_data) == 1 and 'type' in label_data):
                print("Label data is empty or has only type field, generating default test label")
                logger.info("Label data is empty, generating default test label")
                label_generator = get_label_generator("zpl")
                zpl_command = label_generator.generate_test_label({})
            # Generate label based on type or auto-detect from data
            elif label_type == 'custom_zpl':
                # Direct ZPL command provided
                zpl_command = label_data.get('zpl_command', '')
                logger.info("Using direct ZPL command from label_data")
            elif label_type == 'pallet' or label_type == 'palet':
                # Pallet label with specific data - now supports dual printing
                logger.info("Generating pallet label using provided data")
                label_generator = get_label_generator("zpl")
                zpl_command = label_generator.generate_pallet_label(label_data)
                
                # Check if summary printing is requested
                if label_data.get('print_summary', True):  # Default to True for pallet labels
                    await self._generate_and_save_pallet_summary(label_data, job.job_id)
            elif label_type == 'location':
                # Location label with specific data
                logger.info("Generating location label using provided data")
                label_generator = get_label_generator("zpl")
                zpl_command = label_generator.generate_location_label(label_data)
            elif label_type == 'test':
                # Test label - could be with or without data
                if len(label_data) <= 1:
                    # Test label with no additional data - use default test label
                    logger.info("Generating default test label (no custom data provided)")
                    label_generator = get_label_generator("zpl")
                    zpl_command = label_generator.generate_test_label({})
                else:
                    # Test label with custom data
                    logger.info("Generating test label with custom data")
                    zpl_command = self._generate_custom_label(label_data)
            else:
                # Any other case - use custom label generation with provided data
                logger.info(f"Generating custom label using provided data for type: {label_type}")
                zpl_command = self._generate_custom_label(label_data)
            
            if not zpl_command:
                logger.error("No ZPL command generated")
                return False
            
            # Send to printer with auto-recovery
            logger.info(f"Sending ZPL command to printer (length: {len(zpl_command)} chars)")
            success = self.printer.send_command(zpl_command)
            
            # Log error statistics if auto-recovery printer is used
            if hasattr(self.printer.usb_printer, 'get_error_stats'):
                error_stats = self.printer.usb_printer.get_error_stats()
                if error_stats['total_errors'] > 0:
                    logger.info(f"Print job completed with {error_stats['total_errors']} errors and {error_stats['total_recovery_attempts']} recovery attempts")
            
            if success:
                logger.info(f"Print job {job.job_id} completed successfully")
            else:
                logger.error(f"Print job {job.job_id} failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing print job: {e}")
            return False
    
    def _generate_custom_label(self, label_data: Dict[str, Any]) -> str:
        """Generate custom label using data similar to main.py implementation"""
        try:
            # Extract data with defaults
            firma = label_data.get('firma', 'Default Company')
            production_date = label_data.get('production_date', time.strftime('%Y-%m-%d'))
            lot_code = label_data.get('lot_code', '000-000')
            product_code = label_data.get('product_code', 'DEFAULT')
            product_name = label_data.get('product_name', 'Default Product')
            personel_code = label_data.get('personel_code', '000')
            total_amount = label_data.get('total_amount', '100')
            qr_code = label_data.get('qr_code', product_code)
            bom = label_data.get('bom', '')
            hat_kodu = label_data.get('hat_kodu', 'S')
            siparis_kodu = label_data.get('siparis_kodu', '')
            firma_kodu = label_data.get('firma_kodu', 'DEFAULT')
            adet_bilgisi = label_data.get('adet_bilgisi', '250')
            
            # Flags
            uretim_miktari_checked = label_data.get('uretim_miktari_checked', True)
            adet_girisi_checked = label_data.get('adet_girisi_checked', True)
            firma_bilgileri_checked = label_data.get('firma_bilgileri_checked', True)
            brut_kg_checked = label_data.get('brut_kg_checked', True)
            
            # Use the generate_zpl_label function from main.py
            return self._generate_zpl_label(
                firma, production_date, lot_code, product_code, product_name, personel_code,
                total_amount, qr_code, bom, hat_kodu, siparis_kodu, firma_kodu, adet_bilgisi,
                uretim_miktari_checked, adet_girisi_checked, firma_bilgileri_checked, brut_kg_checked
            )
            
        except Exception as e:
            logger.error(f"Error generating custom label: {e}")
            return ""
    
    def _generate_zpl_label(self, firma, production_date, lot_code, product_code, product_name, personel_code,
                           total_amount, qr_code, bom, hat_kodu, siparis_kodu, firma_kodu, adet_bilgisi,
                           uretim_miktari_checked=True, adet_girisi_checked=True,
                           firma_bilgileri_checked=True, brut_kg_checked=True):
        """Generate ZPL label (from main.py implementation)"""
        
        def split_string(text, length=50):
            return text[:length], text[length:] if len(text) > length else ""

        code1, code2 = split_string(product_code)
        name1, name2 = split_string(product_name)
        
        kg_total_amount = (
            "^CF0,25\\n"
            "^FO10,385^FB375,1,0,C^FDUretim miktari / Total Amount^FS\\n"
            "^A0N,60,60^FO10,415^FB375,1,0,C^FD{}^FS\\n"
        ).format(total_amount)
        
        paket_ici_adet = (
            "^CF0,25\\n"
            "^FO365,385^FB375,1,0,C^FDParca ic adedi^FS\\n"
            "^FO365,410^FB375,1,0,C^FDUnits Per Package^FS\\n"
            "^A0N,35,35^FO365,440^FB375,1,0,C^FD{}^FS\\n"
        ).format(adet_bilgisi)
        
        firma_bilgileri = (
            "^CF0,25\\n"
            "^FO10,490^FB375,1,0,C^FDFirma Kodu / CompanyCode^FS\\n"
            "^A0N,30,30^FO10,515^FB375,1,0,C^FD{}^FS\\n"
            "^CF0,25\\n"
            "^FO10,555^FB375,1,0,C^FDSiparis kodu / Sales Code^FS\\n"
            "^A0N,30,30^FO10,585^FB375,1,0,C^FD{}^FS\\n"
        ).format(firma_kodu, siparis_kodu)
        
        burut_kg = float(total_amount) + 0.5  # Utils.dara yerine sabit dara eklendi
        formatted_brut_kg = "{:.2f}".format(burut_kg)
        
        brut_kg = (
            "^CF0,25\\n"
            "^A0N,20,20^FO390,490^FB375,1,0,C^FDBrut kg / total Weight kg^FS\\n"
            "^A0N,50,50^FO390,515^FB375,1,0,C^FD{}^FS\\n"
        ).format(formatted_brut_kg)
        
        zpl_label = []
        
        start_main_design = f"""
           ^XA
            ^FX set width and height
            ^PW799 ^FX size in points = 100 mm width
            ^LL630   ^FX size in points = 80 mm height
            ^CI28
            ^MMT    ^FX set media type to Tear-off
            ^BY3,3  ^FX set the bar code height and gap between labels (gap in dots, 3 mm = 12 dots at 8 dots/mm)
            ^FX border start
            ^FO10,10^GB750,2,2^FS ^FX TOP
            ^FO10,10^GB2,600,2,B^FS ^FX LEFT
            ^FO759,10^GB2,600,2,B^FS ^FX RIGHT
            ^FO10,618^GB750,2,2^FS ^FX BOTTOM
            ^FX border end
            ^FX companySection
            ^FO18,25
            ^A0N,25,25
            ^FDFrima Adi /Customer Name^FS

            ^FO25,55
            ^A0N,50,50
            ^FD{firma}^FS

            ^FX black box
            ^FO660,10
            ^GB100,100,80^FS
            ^FR
            ^FO665,30
            ^A0N,80,80
            ^FD {hat_kodu}^FS
            ^FX end of black box

            ^FX border start
            ^FO550,35
            ^GB100,50,4^FS    
            ^FO560,45
            ^A0N,45,45
            ^FD {bom}^FS   
            ^FX border end

            ^FO10,110^GB750,2,2^FS 
            ^FX end of CompanySection

            ^FO18,120
            ^A0N,35,35
            ^FD{code1}  ^FS  ^FS ^FX 30 charecter max

            ^FO18,160
            ^A0N,35,35
            ^FO10,160^GB750,2,2^FS 

            ^FO18,170
            ^A0N,42,42
            ^FD{name1}^FS ^FX 35 charecter max
            ^FO18,220
            ^A0N,42,42
            ^FD{name2}^FS ^FX 35 charecter max
            ^FO10,270^GB750,2,2^FS 
            ^FO10,275^GB750,2,2^FS 
            ^FX start table

            ^FO10,275^GB750,2,2^FS

            ^FO10,275^GB250,50,2^FS
            ^FO260,275^GB250,50,2 ^FS
            ^FO510,275^GB250,50,2 ^FS

            ^CF0,30
            ^A0N,20,20^FO10,290^FB250,1,0,C^FDU. Tarihi / Production Date^FS
            ^A0N,25,25^FO260,290^FB250,1,0,C^FDLot kodu / Lot Code^FS
            ^A0N,25,25^FO510,290^FB250,1,0,C^FDP.kodu / E. Code^FS


            ^FO10,325^GB250,50,2^FS
            ^FO260,325^GB250,50,2 ^FS
            ^FO510,325^GB250,50,2 ^FS

            ^CF0,30
            ^A0N,25,25^FO20,340^FB250,1,0,C^FD{production_date}^FS
            ^A0N,25,25^FO270,340^FB250,1,0,C^FD{lot_code}^FS
            ^A0N,25,25^FO530,340^FB250,1,0,C^FD{personel_code}^FS

            ^FX end of table

            ^FX start bottom table
            
            ^FO10,375^GB375,100,2^FS
            ^FO385,375^GB270,100,2 ^FS
            
      
            ^FO665,375^BQN,2,4
            ^FDQA,{product_code}^FS
            
            ^FX END BOTTOM TABLE
            
            
            ^FX start bottom table
            
            ^FO10,480^GB375,140,2^FS
            ^FO385,480^GB375,140,2^FS

                """
        
        zpl_label.append(start_main_design)
        
        if uretim_miktari_checked:
            zpl_label.append(kg_total_amount)
        if adet_girisi_checked:
            zpl_label.append(paket_ici_adet)
        if firma_bilgileri_checked:
            zpl_label.append(firma_bilgileri)
        if brut_kg_checked:
            zpl_label.append(brut_kg)
        
        zpl_label.append("^XZ")
        
        return "".join(zpl_label).strip()
    
    async def _handle_printer_command(self, data):
        """Handle direct printer commands"""
        try:
            command = data.get('command', '')
            command_type = data.get('type', 'zpl')
            
            if not self.printer or not self.printer.is_connected:
                logger.error("Printer not connected")
                return
            
            logger.info(f"Received printer command: {command[:50]}...")
            
            if command_type == 'zpl':
                success = self.printer.send_command(command)
            else:
                success = self.printer.send_raw_bytes(command.encode('utf-8'))
            
            # Send response
            response = {
                'printer_id': self.printer_config.printer_id,
                'command_status': 'completed' if success else 'failed',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            await self.sio.emit('command_result', response)
            
        except Exception as e:
            logger.error(f"Error handling printer command: {e}")
    
    async def _handle_health_check(self, data):
        """Handle health check requests"""
        try:
            # Test printer connection
            printer_status = 'online' if (self.printer and self.printer.is_connected) else 'offline'
            
            if self.printer and self.printer.is_connected:
                # Perform actual test
                test_success = self.printer.test_connection()
                if not test_success:
                    printer_status = 'error'
            
            health_data = {
                'printer_id': self.printer_config.printer_id,
                'status': printer_status,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'connection_info': self.printer.get_connection_info() if self.printer else None
            }
            
            await self.sio.emit('health_response', health_data)
            logger.info(f"Health check completed: {printer_status}")
            
        except Exception as e:
            logger.error(f"Error handling health check: {e}")
    
    async def _generate_and_save_pallet_summary(self, pallet_data: Dict[str, Any], job_id: str):
        """Generate pallet summary in A5 format and save to file"""
        try:
            logger.info(f"Generating pallet summary for job {job_id}")
            
            # Create summary generator
            summary_generator = get_pallet_summary_generator()
            
            # Generate HTML summary (A5 format)
            html_summary = summary_generator.generate_html_summary(pallet_data)
            
            # Generate text summary (for basic printers)
            text_summary = summary_generator.generate_text_summary(pallet_data)
            
            # Create output directory if it doesn't exist
            import os
            output_dir = "pallet_summaries"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Get pallet ID for filename
            pallet_id = pallet_data.get('palet_id', pallet_data.get('pallet_id', job_id))
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            
            # Save HTML version
            html_filename = f"{output_dir}/pallet_summary_{pallet_id}_{timestamp}.html"
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(html_summary)
            
            # Save text version
            txt_filename = f"{output_dir}/pallet_summary_{pallet_id}_{timestamp}.txt"
            with open(txt_filename, 'w', encoding='utf-8') as f:
                f.write(text_summary)
            
            logger.info(f"✅ Pallet summary saved:")
            logger.info(f"   HTML: {html_filename}")
            logger.info(f"   Text: {txt_filename}")
            
            # Try to print HTML version if default printer is available
            await self._print_summary_to_default_printer(html_filename)
            
        except Exception as e:
            logger.error(f"Error generating pallet summary: {e}")
    
    async def _print_summary_to_default_printer(self, html_file_path: str):
        """Print the HTML summary to the default system printer"""
        try:
            import subprocess
            import platform
            
            system = platform.system()
            logger.info(f"Attempting to print summary on {system}")
            
            if system == "Darwin":  # macOS
                # Use system print command
                cmd = ["lpr", "-P", "default", "-o", "media=A5", html_file_path]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info("✅ Summary sent to default printer successfully")
                else:
                    # Try alternative method - open with default browser for printing
                    cmd = ["open", "-a", "Safari", html_file_path]
                    subprocess.run(cmd)
                    logger.info("📄 Summary opened in browser for manual printing")
                    
            elif system == "Windows":
                # Use Windows print command
                cmd = ["print", "/D:default", html_file_path]
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info("✅ Summary sent to default printer successfully")
                else:
                    # Try alternative method - open with default browser
                    import webbrowser
                    webbrowser.open(html_file_path)
                    logger.info("📄 Summary opened in browser for manual printing")
                    
            elif system == "Linux":
                # Use Linux print command
                cmd = ["lp", "-d", "default", "-o", "media=A5", html_file_path]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info("✅ Summary sent to default printer successfully")
                else:
                    # Try alternative method - open with default browser
                    import webbrowser
                    webbrowser.open(html_file_path)
                    logger.info("📄 Summary opened in browser for manual printing")
            
        except Exception as e:
            logger.warning(f"Could not print summary automatically: {e}")
            logger.info(f"📄 Summary file available at: {html_file_path}")
    
    async def start(self):
        """Start the WebSocket client"""
        try:
            # Initialize printer
            self.printer = USBPrinterInterface(self.printer_config)
            
            # Connect to printer
            if not self.printer.connect():
                logger.error("Failed to connect to USB printer")
                return False
            
            logger.info("✅ USB printer connected successfully")
            
            # Connect to WebSocket server
            while self.reconnect_attempts < self.max_reconnect_attempts:
                try:
                    logger.info(f"Attempting to connect to WebSocket server: {self.server_url}")
                    await self.sio.connect(self.server_url)
                    break
                except Exception as e:
                    self.reconnect_attempts += 1
                    logger.error(f"Connection attempt {self.reconnect_attempts} failed: {e}")
                    if self.reconnect_attempts < self.max_reconnect_attempts:
                        logger.info(f"Retrying in {self.reconnect_delay} seconds...")
                        await asyncio.sleep(self.reconnect_delay)
            
            if self.reconnect_attempts >= self.max_reconnect_attempts:
                logger.error("Max reconnection attempts reached")
                return False
            
            logger.info("✅ WebSocket connection established")
            
            # Wait for registration to complete
            max_wait = 30  # 30 saniye bekle
            wait_time = 0
            while not self.is_registered and wait_time < max_wait:
                await asyncio.sleep(1)
                wait_time += 1
                if wait_time % 5 == 0:  # Her 5 saniyede bir log
                    logger.info(f"Waiting for printer registration... ({wait_time}/{max_wait}s)")
            
            if self.is_registered:
                logger.info("🎉 Printer registration completed successfully!")
                
                # Send initial ping
                await self._send_ping()
                
                # Start periodic ping (her 30 saniyede bir)
                asyncio.create_task(self._periodic_ping())
                
            else:
                logger.warning("⚠️ Printer registration not confirmed within timeout")
            
            # Keep the client running
            await self.sio.wait()
            
        except Exception as e:
            logger.error(f"Error starting client: {e}")
            return False
        finally:
            # Cleanup
            if self.printer:
                self.printer.disconnect()
    
    async def _periodic_ping(self):
        """Send periodic ping to maintain connection"""
        while self.is_connected:
            try:
                await asyncio.sleep(30)  # 30 saniye bekle
                if self.is_connected:
                    await self._send_ping()
            except Exception as e:
                logger.error(f"Error in periodic ping: {e}")
                break
    
    async def stop(self):
        """Stop the WebSocket client"""
        try:
            if self.sio.connected:
                await self.sio.disconnect()
            
            if self.printer:
                self.printer.disconnect()
            
            logger.info("WebSocket client stopped")
            
        except Exception as e:
            logger.error(f"Error stopping client: {e}")


def list_available_usb_printers() -> List[Dict[str, Any]]:
    """List all available USB printers"""
    return DirectUSBPrinter.list_available_printers()


async def run_usb_printer_client(server_url: str, printer_config: USBPrinterConfig):
    """Run the USB printer client"""
    client = WebSocketPrinterClient(server_url, printer_config)
    
    try:
        await client.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        await client.stop()


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # List available printers
    printers = list_available_usb_printers()
    print("Available USB printers:")
    for i, printer in enumerate(printers):
        print(f"{i+1}. {printer['manufacturer']} {printer['model']} (VID: 0x{printer['vendor_id']:04X}, PID: 0x{printer['product_id']:04X})")
    
    if printers:
        # Use first available printer
        first_printer = printers[0]
        
        config = USBPrinterConfig(
            printer_id="USB_PRINTER_001",
            printer_name=f"{first_printer['manufacturer']} {first_printer['model']}",
            printer_type=PrinterType.ZEBRA if first_printer['type'] == 'zebra' else PrinterType.THERMAL,
            location="Warehouse A",
            usb_vendor_id=first_printer['vendor_id'],
            usb_product_id=first_printer['product_id'],
            auto_detect=False
        )
        
        # Get server URL from environment variables
        server_url = os.getenv('SERVER_URL', 'http://192.168.1.139:25625')
        print(f"Using server URL: {server_url}")
        
        print(f"Starting client for: {config.printer_name}")
        asyncio.run(run_usb_printer_client(server_url, config))
    else:
        print("No USB printers found. Please connect a supported USB printer.")
