#!/usr/bin/env python3
"""
Test PDF Generator Functions
Test that the PDF generator functions are working correctly
"""

import asyncio
import logging
import time
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test data
test_pallet_data = {
    "pallet_id": "PLT-TEST-001",
    "location": "A1-01-01",
    "materials": [
        {
            "material_code": "MAT001",
            "description": "Test Malzeme 1 - Türkçe Karakter üÜğĞıİşŞöÖçÇ",
            "quantity": 100,
            "unit": "adet"
        },
        {
            "material_code": "MAT002",
            "description": "Test Malzeme 2 - Özel Karakterler €$£₺",
            "quantity": 50,
            "unit": "kg"
        }
    ],
    "timestamp": datetime.now().isoformat()
}

def test_pdf_generator_import():
    """Test PDF generator import and function availability"""
    print("🧪 Testing PDF Generator Import")
    print("-" * 40)
    
    try:
        from pdf_pallet_generator import get_pdf_pallet_generator
        pdf_generator = get_pdf_pallet_generator()
        print("✅ PDF generator imported successfully")
        
        # Check if generate_pdf_summary method exists
        if hasattr(pdf_generator, 'generate_pdf_summary'):
            print("✅ generate_pdf_summary method found")
        else:
            print("❌ generate_pdf_summary method not found")
            return False
            
        # Check available methods
        methods = [method for method in dir(pdf_generator) if not method.startswith('_')]
        print(f"📋 Available methods: {methods}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_pdf_generation():
    """Test actual PDF generation"""
    print("\n🧪 Testing PDF Generation")
    print("-" * 40)
    
    try:
        from pdf_pallet_generator import get_pdf_pallet_generator
        pdf_generator = get_pdf_pallet_generator()
        
        # Generate PDF
        pdf_file_path = pdf_generator.generate_pdf_summary(test_pallet_data)
        
        if pdf_file_path:
            print(f"✅ PDF generated: {pdf_file_path}")
            
            # Check if file exists
            import os
            if os.path.exists(pdf_file_path):
                print(f"✅ PDF file exists on disk")
                file_size = os.path.getsize(pdf_file_path)
                print(f"📊 File size: {file_size} bytes")
                
                # Clean up test file
                os.remove(pdf_file_path)
                print("🗑️  Test PDF file cleaned up")
                
                return True
            else:
                print("❌ PDF file not found on disk")
                return False
        else:
            print("❌ No PDF file path returned")
            return False
            
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        return False

async def test_template_system_functions():
    """Test template system with correct function calls"""
    print("\n🧪 Testing Template System Functions")
    print("-" * 40)
    
    try:
        from usb_printer_client import WebSocketPrinterClient, USBPrinterConfig, PrinterType, PrintJob
        
        # Create dummy config
        config = USBPrinterConfig(
            printer_id="TEST_PRINTER",
            printer_name="Test Printer",
            printer_type=PrinterType.ZEBRA,
            location="Test Location"
        )
        
        # Create client instance (without connecting)
        client = WebSocketPrinterClient("ws://test", config)
        
        # Test A5 summary generation function
        job = PrintJob(
            job_id="test_job_001",
            label_data={
                "template": "pallet_content_list_a5",
                **test_pallet_data
            },
            timestamp=datetime.now().isoformat(),
            requested_by="test_user"
        )
        
        print(f"Testing with job: {job.job_id}")
        print(f"Template: {job.label_data.get('template')}")
        
        # This should work now with the corrected function call
        result = await client._generate_and_print_pallet_summary_only(job.label_data, job.job_id)
        
        if result:
            print("✅ Template system function test passed")
        else:
            print("❌ Template system function test failed")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in template system test: {e}")
        return False

async def main():
    """Main test function"""
    print("🧪 PDF Generator Function Test Suite")
    print("=" * 60)
    print("Testing PDF generator functions and template system")
    print()
    
    # Run tests
    results = []
    
    # Test 1: PDF Generator Import
    results.append(test_pdf_generator_import())
    
    # Test 2: PDF Generation
    results.append(test_pdf_generation())
    
    # Test 3: Template System Functions
    results.append(await test_template_system_functions())
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    test_names = [
        "PDF Generator Import",
        "PDF Generation", 
        "Template System Functions"
    ]
    
    for i, (test_name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:25} {status}")
    
    overall_success = all(results)
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 PDF generator functions are working correctly!")
        print("Template system should now work without errors.")
    else:
        print("\n⚠️  Please fix the failing tests.")

if __name__ == "__main__":
    asyncio.run(main())
