#!/usr/bin/env python3
"""
Test PDF Cleanup Functionality
Windows PDF Dual Printing System v2.2.0 - Test Suite
"""

import asyncio
import os
import logging
import tempfile
from pathlib import Path

# Import our client
from usb_printer_client import WebSocketPrinterClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_pdf_cleanup():
    """Test PDF cleanup functionality"""
    
    # Create a temporary PDF file
    temp_dir = tempfile.gettempdir()
    test_pdf_path = os.path.join(temp_dir, "test_cleanup.pdf")
    
    # Create a dummy PDF file
    with open(test_pdf_path, 'w') as f:
        f.write("Test PDF content for cleanup testing")
    
    logger.info(f"🧪 Created test PDF: {test_pdf_path}")
    logger.info(f"📄 File exists: {os.path.exists(test_pdf_path)}")
    
    # Create client instance (without starting WebSocket connection)
    from usb_printer_client import USBPrinterConfig, PrinterType
    
    # Create dummy config
    config = USBPrinterConfig(
        port_path="TEST",
        baud_rate=9600,
        printer_type=PrinterType.ZPL
    )
    
    client = WebSocketPrinterClient("ws://test", config)
    
    # Test cleanup without delay
    logger.info("\n🔧 Testing immediate cleanup...")
    await client._cleanup_pdf_file(test_pdf_path, delay=0)
    logger.info(f"📄 File exists after cleanup: {os.path.exists(test_pdf_path)}")
    
    # Create another test file for delayed cleanup
    test_pdf_path_2 = os.path.join(temp_dir, "test_cleanup_delayed.pdf")
    with open(test_pdf_path_2, 'w') as f:
        f.write("Test PDF content for delayed cleanup testing")
    
    logger.info(f"\n🧪 Created second test PDF: {test_pdf_path_2}")
    
    # Test cleanup with delay
    logger.info("🔧 Testing delayed cleanup (3 seconds)...")
    await client._cleanup_pdf_file(test_pdf_path_2, delay=3)
    logger.info(f"📄 File exists after delayed cleanup: {os.path.exists(test_pdf_path_2)}")
    
    # Test cleanup of non-existent file
    logger.info("\n🔧 Testing cleanup of non-existent file...")
    fake_path = os.path.join(temp_dir, "non_existent.pdf")
    await client._cleanup_pdf_file(fake_path, delay=0)
    
    logger.info("\n✅ All cleanup tests completed!")

if __name__ == "__main__":
    print("🧪 PDF Cleanup Test Suite")
    print("=" * 50)
    print("Testing PDF file cleanup functionality")
    print("Windows PDF Dual Printing System v2.2.0")
    print()
    
    asyncio.run(test_pdf_cleanup())
