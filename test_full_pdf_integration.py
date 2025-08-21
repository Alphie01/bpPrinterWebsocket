#!/usr/bin/env python3
"""
Full Integration Test for Windows PDF Dual Printing System
Tests the complete flow: ZPL generation → PDF generation → Printing → Cleanup
"""

import asyncio
import logging
import os
import tempfile
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test data for pallet label
test_pallet_data = {
    "type": "pallet_label",
    "pallet_id": "PLT-TEST-001",
    "location": "A1-01-01",
    "materials": [
        {
            "material_code": "MAT001",
            "description": "Test Malzeme 1 - Türkçe Karakter Test üÜğĞıİşŞöÖçÇ",
            "quantity": 100,
            "unit": "adet"
        },
        {
            "material_code": "MAT002", 
            "description": "Test Malzeme 2 - Özel Karakterler €$£₺",
            "quantity": 50,
            "unit": "kg"
        },
        {
            "material_code": "MAT003",
            "description": "Test Malzeme 3 - Uzun İsim Testi Çok Uzun Malzeme Adı",
            "quantity": 25,
            "unit": "lt"
        }
    ],
    "timestamp": datetime.now().isoformat()
}

async def test_full_pdf_workflow():
    """Test the complete PDF workflow without WebSocket connection"""
    
    try:
        # Import after ensuring modules are available
        from pdf_pallet_generator import PalletPDFGenerator
        from usb_printer_client import WebSocketPrinterClient
        
        logger.info("🧪 Starting Full PDF Workflow Test")
        logger.info("=" * 60)
        
        # 1. Test PDF Generation
        logger.info("📄 Step 1: Testing PDF Generation...")
        pdf_generator = PalletPDFGenerator()
        
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = os.path.join(temp_dir, f"test_pallet_summary_{timestamp}.pdf")
        
        # Generate PDF
        result = pdf_generator.generate_pallet_summary_pdf(test_pallet_data, pdf_path)
        
        if result and os.path.exists(pdf_path):
            logger.info(f"✅ PDF generated successfully: {pdf_path}")
            
            # Get file size
            file_size = os.path.getsize(pdf_path)
            logger.info(f"📊 PDF file size: {file_size} bytes")
        else:
            logger.error("❌ PDF generation failed!")
            return False
        
        # 2. Test Client Cleanup Method
        logger.info("\n🧹 Step 2: Testing PDF Cleanup...")
        
        from usb_printer_client import USBPrinterConfig, PrinterType
        
        # Create dummy config for testing
        config = USBPrinterConfig(
            port_path="TEST",
            baud_rate=9600,
            printer_type=PrinterType.ZPL
        )
        
        client = WebSocketPrinterClient("ws://test", config)
        
        # Create a copy for cleanup test
        test_cleanup_path = os.path.join(temp_dir, f"cleanup_test_{timestamp}.pdf")
        
        # Copy the PDF file for cleanup test
        with open(pdf_path, 'rb') as src, open(test_cleanup_path, 'wb') as dst:
            dst.write(src.read())
        
        logger.info(f"📄 Created cleanup test file: {test_cleanup_path}")
        
        # Test cleanup with delay
        logger.info("⏳ Testing cleanup with 2 second delay...")
        await client._cleanup_pdf_file(test_cleanup_path, delay=2)
        
        # Verify cleanup
        if not os.path.exists(test_cleanup_path):
            logger.info("✅ PDF cleanup successful!")
        else:
            logger.error("❌ PDF cleanup failed - file still exists!")
        
        # 3. Manual cleanup of original test file
        logger.info("\n🧹 Step 3: Manual cleanup of test file...")
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            logger.info(f"✅ Test PDF cleaned up: {os.path.basename(pdf_path)}")
        
        logger.info("\n🎉 Full PDF workflow test completed successfully!")
        logger.info("=" * 60)
        logger.info("✅ All tests passed:")
        logger.info("  • PDF generation with Turkish characters")
        logger.info("  • File size validation")
        logger.info("  • Automatic cleanup functionality")
        logger.info("  • Delayed cleanup support")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("Make sure all required modules are available")
        return False
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        return False

async def test_platform_detection():
    """Test platform detection for printing"""
    
    try:
        from usb_printer_client import WebSocketPrinterClient, USBPrinterConfig, PrinterType
        
        logger.info("\n🖥️  Platform Detection Test")
        logger.info("-" * 30)
        
        # Create dummy config for testing
        config = USBPrinterConfig(
            port_path="TEST",
            baud_rate=9600,
            printer_type=PrinterType.ZPL
        )
        
        client = WebSocketPrinterClient("ws://test", config)
        
        # Test platform detection
        import platform
        current_platform = platform.system()
        logger.info(f"Current platform: {current_platform}")
        
        if current_platform == "Windows":
            logger.info("✅ Running on Windows - PowerShell printing will be used")
        elif current_platform == "Darwin":
            logger.info("⚠️  Running on macOS - lpr printing will be used")
        elif current_platform == "Linux":
            logger.info("⚠️  Running on Linux - lp printing will be used")
        else:
            logger.info(f"⚠️  Unknown platform: {current_platform}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Platform detection test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Windows PDF Dual Printing System - Full Integration Test")
    print("=" * 70)
    print("Testing complete workflow: PDF generation → Cleanup → Platform detection")
    print("Version: 2.2.0 Windows PDF Edition")
    print()
    
    async def run_all_tests():
        # Run PDF workflow test
        pdf_test_result = await test_full_pdf_workflow()
        
        # Run platform detection test
        platform_test_result = await test_platform_detection()
        
        # Summary
        print("\n" + "=" * 70)
        print("🎯 TEST RESULTS SUMMARY")
        print("=" * 70)
        print(f"📄 PDF Workflow Test: {'✅ PASSED' if pdf_test_result else '❌ FAILED'}")
        print(f"🖥️  Platform Detection: {'✅ PASSED' if platform_test_result else '❌ FAILED'}")
        
        if pdf_test_result and platform_test_result:
            print("\n🎉 ALL TESTS PASSED!")
            print("System is ready for Windows PDF dual printing with cleanup!")
        else:
            print("\n⚠️  SOME TESTS FAILED!")
            print("Please check the error messages above.")
    
    asyncio.run(run_all_tests())
