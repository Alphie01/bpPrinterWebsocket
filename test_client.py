#!/usr/bin/env python3
"""
Test script for WebSocket Printer Client
"""

import asyncio
import sys
import time
from printer_client import WebSocketPrinterClient, SerialPrinterInterface
from config import PrinterConfig, PrinterType
from label_generators import get_label_generator
import serial.tools.list_ports


def test_serial_ports():
    """Test serial port listing"""
    print("Testing serial port listing...")
    try:
        ports = serial.tools.list_ports.comports()
        print(f"Found {len(ports)} serial ports:")
        for i, port in enumerate(ports):
            print(f"  {i}: {port.device} - {port.description}")
        return len(ports) > 0
    except Exception as e:
        print(f"Error listing serial ports: {e}")
        return False


def test_label_generation():
    """Test label generation"""
    print("\nTesting label generation...")
    
    try:
        generator = get_label_generator("thermal")
        
        # Test location label
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
            'maxWeight': 1000,
            'maxVolume': 500,
            'createdAt': '2025-08-07T10:30:00.000Z',
            'printedAt': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        location_commands = generator.generate_location_label(location_data)
        print("✓ Location label generated successfully")
        print(f"  Command length: {len(location_commands)} characters")
        
        # Test pallet label
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
            'createdAt': '2025-08-07T10:30:00.000Z',
            'printedAt': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        pallet_commands = generator.generate_pallet_label(pallet_data)
        print("✓ Pallet label generated successfully")
        print(f"  Command length: {len(pallet_commands)} characters")
        
        # Test test label
        test_data = {
            'type': 'test',
            'message': 'Printer Test',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        test_commands = generator.generate_test_label(test_data)
        print("✓ Test label generated successfully")
        print(f"  Command length: {len(test_commands)} characters")
        
        return True
        
    except Exception as e:
        print(f"✗ Label generation failed: {e}")
        return False


async def test_websocket_connection():
    """Test WebSocket connection"""
    print("\nTesting WebSocket connection...")
    
    try:
        import socketio
        
        sio = socketio.AsyncClient()
        connected = False
        
        @sio.event
        async def connect():
            nonlocal connected
            connected = True
            print("✓ WebSocket connection successful")
        
        @sio.event
        async def connect_error(data):
            print(f"✗ WebSocket connection failed: {data}")
        
        try:
            await asyncio.wait_for(sio.connect('http://192.168.1.139:25625'), timeout=5.0)
            await asyncio.sleep(1)  # Give time for connection event
            await sio.disconnect()
            return connected
        except asyncio.TimeoutError:
            print("✗ WebSocket connection timeout (server not running?)")
            return False
        except Exception as e:
            print(f"✗ WebSocket connection error: {e}")
            return False
            
    except Exception as e:
        print(f"✗ WebSocket test failed: {e}")
        return False


def test_configuration():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        # Test default configuration
        config = PrinterConfig(
            printer_id="TEST_PRINTER",
            printer_name="Test Printer",
            printer_type=PrinterType.THERMAL,
            location="Test Location",
            serial_port="/dev/null",  # Use null device for testing
            baud_rate=9600
        )
        
        print("✓ Configuration created successfully")
        print(f"  Printer ID: {config.printer_id}")
        print(f"  Printer Type: {config.printer_type.value}")
        print(f"  Serial Port: {config.serial_port}")
        print(f"  Baud Rate: {config.baud_rate}")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("WebSocket Printer Client - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Serial Port Listing", test_serial_ports),
        ("Configuration", test_configuration),
        ("Label Generation", test_label_generation),
        ("WebSocket Connection", test_websocket_connection),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n🎉 All tests passed! The client is ready to use.")
        return 0
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Check the output above.")
        return 1


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(result)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
