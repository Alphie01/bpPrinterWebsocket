#!/usr/bin/env python3
"""
Demo script for WebSocket Printer Client
Shows how to use the client without actual hardware
"""

import asyncio
import json
import time
from printer_client import SerialPrinterInterface
from label_generators import get_label_generator
from config import PrinterConfig, PrinterType


class MockSerialPrinter:
    """Mock serial printer for demonstration"""
    
    def __init__(self, port: str, baud_rate: int = 9600, timeout: float = 1.0):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.is_connected = False
        self.print_history = []
    
    def connect(self) -> bool:
        """Mock connection"""
        print(f"[MOCK] Connecting to printer on {self.port}")
        self.is_connected = True
        return True
    
    def disconnect(self):
        """Mock disconnection"""
        print(f"[MOCK] Disconnecting from {self.port}")
        self.is_connected = False
    
    def send_command(self, command: str) -> bool:
        """Mock command sending"""
        if not self.is_connected:
            return False
        
        print(f"[MOCK] Sending command to printer ({len(command)} chars)")
        print(f"[MOCK] Preview: {repr(command[:50])}...")
        self.print_history.append({
            'timestamp': time.time(),
            'command': command,
            'length': len(command)
        })
        return True
    
    def send_raw_bytes(self, data: bytes) -> bool:
        """Mock raw bytes sending"""
        return self.send_command(data.decode('utf-8', errors='ignore'))


def demo_label_generation():
    """Demonstrate label generation"""
    print("🏷️  Label Generation Demo")
    print("=" * 50)
    
    # Get ESC/POS generator
    generator = get_label_generator("thermal")
    
    # Location label demo
    print("\n📍 Location Label:")
    location_data = {
        'type': 'location',
        'id': 1,
        'barcode': 'LOC000001',
        'locationName': 'A-01-01',
        'warehouseCode': 'WH001',
        'locationType': 'SHELF',
        'aisle': 'A',
        'bay': '01',
        'level': '01',
        'position': '01',
        'maxWeight': 1000,
        'maxVolume': 500,
        'createdAt': '2025-08-07T10:30:00.000Z',
        'printedAt': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    location_label = generator.generate_location_label(location_data)
    print(f"Generated {len(location_label)} characters")
    print("Label content preview:")
    print("-" * 30)
    # Show printable characters only
    preview = ''.join(c if c.isprintable() or c in '\n\r' else f'[{ord(c):02X}]' for c in location_label)
    print(preview[:300] + "..." if len(preview) > 300 else preview)
    print("-" * 30)
    
    # Pallet label demo
    print("\n📦 Pallet Label:")
    pallet_data = {
        'type': 'pallet',
        'id': 1,
        'barcode': 'PAL000001',
        'palletType': 'EURO',
        'status': 'AVAILABLE',
        'currentWeight': 500,
        'maxWeight': 1000,
        'currentVolume': 250,
        'maxVolume': 500,
        'warehouseCode': 'WH001',
        'locationId': None,
        'createdAt': '2025-08-07T10:30:00.000Z',
        'printedAt': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    pallet_label = generator.generate_pallet_label(pallet_data)
    print(f"Generated {len(pallet_label)} characters")
    
    # Test label demo
    print("\n🧪 Test Label:")
    test_data = {
        'type': 'test',
        'message': 'Demo Test Label',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    test_label = generator.generate_test_label(test_data)
    print(f"Generated {len(test_label)} characters")
    
    return {
        'location': location_label,
        'pallet': pallet_label,
        'test': test_label
    }


def demo_printer_communication():
    """Demonstrate printer communication"""
    print("\n🖨️  Printer Communication Demo")
    print("=" * 50)
    
    # Create mock printer
    mock_printer = MockSerialPrinter("/dev/mock_printer", 9600)
    
    # Connect
    print("\n1. Connecting to printer...")
    if mock_printer.connect():
        print("✓ Connection successful")
    else:
        print("✗ Connection failed")
        return
    
    # Generate and send labels
    labels = demo_label_generation()
    
    print("\n2. Sending labels to printer...")
    for label_type, label_content in labels.items():
        print(f"\nSending {label_type} label...")
        success = mock_printer.send_command(label_content)
        if success:
            print(f"✓ {label_type.capitalize()} label sent successfully")
        else:
            print(f"✗ Failed to send {label_type} label")
    
    # Show history
    print(f"\n3. Print History ({len(mock_printer.print_history)} jobs):")
    for i, job in enumerate(mock_printer.print_history, 1):
        timestamp = time.strftime('%H:%M:%S', time.localtime(job['timestamp']))
        print(f"  {i}. {timestamp} - {job['length']} characters")
    
    # Disconnect
    print("\n4. Disconnecting...")
    mock_printer.disconnect()
    print("✓ Disconnected")


def demo_websocket_message_format():
    """Demonstrate WebSocket message formats"""
    print("\n🌐 WebSocket Message Format Demo")
    print("=" * 50)
    
    # Registration message
    print("\n📝 Printer Registration Message:")
    registration = {
        'printerId': 'PRINTER_001',
        'printerName': 'Main Warehouse Printer',
        'printerType': 'thermal',
        'location': 'Warehouse A - Loading Dock'
    }
    print(json.dumps(registration, indent=2))
    
    # Print job message
    print("\n📄 Print Job Message:")
    print_job = {
        'jobId': 'job_1723026123456_abc123def',
        'labelData': {
            'type': 'location',
            'id': 42,
            'barcode': 'LOC000042',
            'locationName': 'A-05-03',
            'warehouseCode': 'WH001',
            'locationType': 'SHELF',
            'template': 'location_label'
        },
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
        'requestedBy': 'web_client_001'
    }
    print(json.dumps(print_job, indent=2))
    
    # Print result message
    print("\n✅ Print Result Message:")
    print_result = {
        'success': True,
        'message': 'Label printed successfully',
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    }
    print(json.dumps(print_result, indent=2))


def demo_configuration():
    """Demonstrate configuration"""
    print("\n⚙️  Configuration Demo")
    print("=" * 50)
    
    # Different printer configurations
    configs = [
        {
            'name': 'Thermal Receipt Printer',
            'config': PrinterConfig(
                printer_id='THERMAL_001',
                printer_name='Epson TM-T20II',
                printer_type=PrinterType.THERMAL,
                location='Checkout Counter 1',
                serial_port='/dev/ttyUSB0',
                baud_rate=38400
            )
        },
        {
            'name': 'Label Printer',
            'config': PrinterConfig(
                printer_id='LABEL_001',
                printer_name='Brother QL-820NWB',
                printer_type=PrinterType.LABEL,
                location='Warehouse Office',
                serial_port='COM3',
                baud_rate=9600
            )
        },
        {
            'name': 'Industrial Printer',
            'config': PrinterConfig(
                printer_id='ZEBRA_001',
                printer_name='Zebra ZT411',
                printer_type=PrinterType.THERMAL,
                location='Production Line',
                serial_port='/dev/ttyACM0',
                baud_rate=115200
            )
        }
    ]
    
    for item in configs:
        config = item['config']
        print(f"\n{item['name']}:")
        print(f"  ID: {config.printer_id}")
        print(f"  Name: {config.printer_name}")
        print(f"  Type: {config.printer_type.value}")
        print(f"  Location: {config.location}")
        print(f"  Port: {config.serial_port}")
        print(f"  Baud Rate: {config.baud_rate}")


async def main():
    """Main demo function"""
    print("WebSocket Printer Client - Demo")
    print("=" * 50)
    print("This demo shows the capabilities of the printer client")
    print("without requiring actual hardware or server connection.")
    print()
    
    try:
        # Configuration demo
        demo_configuration()
        
        # Label generation demo
        demo_label_generation()
        
        # Printer communication demo
        demo_printer_communication()
        
        # WebSocket message format demo
        demo_websocket_message_format()
        
        print("\n" + "=" * 50)
        print("🎉 Demo completed successfully!")
        print("\nTo use with real hardware:")
        print("1. Connect a thermal printer via USB/Serial")
        print("2. Start the WebSocket server (npm start)")
        print("3. Run: python run_client.py")
        print("4. Follow the configuration prompts")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
