#!/usr/bin/env python3
"""
Quick test of WebSocket connection without printer hardware
"""

import asyncio
import sys
import os
import json
from config import PrinterConfig, PrinterType, PrinterConnectionType

# Mock printer config for testing
test_config = PrinterConfig(
    printer_id="TEST_PRINTER_001",
    printer_name="Test Printer",
    printer_type=PrinterType.ESCPOS,
    location="Test Location",
    connection_type=PrinterConnectionType.AUTO,
    serial_port=None,
    baud_rate=9600
)

async def test_connection():
    """Test WebSocket connection to server"""
    try:
        from printer_client import WebSocketPrinterClient
        
        server_url = "ws://localhost:25625"
        print(f"Testing connection to {server_url}")
        print(f"Using test printer config: {test_config.printer_id}")
        
        # Create client
        client = WebSocketPrinterClient(test_config, server_url)
        
        print("Attempting to connect...")
        
        # Try to connect for 5 seconds
        try:
            await asyncio.wait_for(client.start(), timeout=5.0)
        except asyncio.TimeoutError:
            print("Connection test completed (timeout reached)")
        
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("WebSocket Connection Test")
    print("=" * 30)
    
    result = asyncio.run(test_connection())
    if result:
        print("✅ Test completed successfully")
    else:
        print("❌ Test failed")
