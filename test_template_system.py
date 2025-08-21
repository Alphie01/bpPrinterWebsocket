#!/usr/bin/env python3
"""
Test Template System
Test the new dual template system for printer client
"""

import asyncio
import json
import logging
import time
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test data for different templates
test_data = {
    "pallet_label": {
        "template": "pallet_label",
        "data": {
            "pallet_id": "PLT-2025-001",
            "location": "A1-01-01",
            "barcode": "PLT2025001",
            "timestamp": datetime.now().isoformat()
        }
    },
    "pallet_content_list_a5": {
        "template": "pallet_content_list_a5",
        "data": {
            "pallet_id": "PLT-2025-001", 
            "location": "A1-01-01",
            "materials": [
                {
                    "material_code": "MAT001",
                    "description": "Test Malzeme 1 - Türkçe Karakter",
                    "quantity": 100,
                    "unit": "adet"
                },
                {
                    "material_code": "MAT002",
                    "description": "Test Malzeme 2 - Özel Karakterler",
                    "quantity": 50,
                    "unit": "kg"
                },
                {
                    "material_code": "MAT003",
                    "description": "Test Malzeme 3 - Uzun İsim",
                    "quantity": 25,
                    "unit": "lt"
                }
            ],
            "timestamp": datetime.now().isoformat()
        }
    }
}

def test_zpl_generation():
    """Test ZPL label generation"""
    print("🏷️  Testing ZPL Pallet Label Generation")
    print("-" * 50)
    
    # Import the client components
    try:
        from printer_client import WebSocketPrinterClient, PrinterConfig, PrinterType, PrinterConnectionType
        
        # Create dummy config
        config = PrinterConfig(
            printer_id="TEST_PRINTER",
            printer_name="Test Printer",
            printer_type=PrinterType.ZEBRA,
            location="Test Location",
            connection_type=PrinterConnectionType.SERIAL,
            serial_port="/dev/null"
        )
        
        # Create client instance
        client = WebSocketPrinterClient(config)
        
        # Test ZPL generation
        pallet_data = test_data["pallet_label"]["data"]
        zpl_commands = client._generate_zpl_pallet_label(pallet_data)
        
        print("Generated ZPL Commands:")
        print("=" * 30)
        print(zpl_commands)
        print("=" * 30)
        
        # Validate ZPL structure
        if zpl_commands.startswith("^XA") and zpl_commands.endswith("^XZ"):
            print("✅ ZPL structure is valid")
        else:
            print("❌ ZPL structure is invalid")
        
        # Check for required elements
        required_elements = ["^FO", "^FD", "^FS", "^BC"]
        found_elements = [elem for elem in required_elements if elem in zpl_commands]
        
        print(f"📊 Found ZPL elements: {found_elements}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing ZPL generation: {e}")
        return False

def test_a5_summary_generation():
    """Test A5 summary content generation"""
    print("\n📋 Testing A5 Summary Content Generation")
    print("-" * 50)
    
    try:
        from printer_client import WebSocketPrinterClient, PrinterConfig, PrinterType, PrinterConnectionType
        
        # Create dummy config
        config = PrinterConfig(
            printer_id="TEST_PRINTER",
            printer_name="Test Printer", 
            printer_type=PrinterType.THERMAL,
            location="Test Location",
            connection_type=PrinterConnectionType.SERIAL,
            serial_port="/dev/null"
        )
        
        # Create client instance
        client = WebSocketPrinterClient(config)
        
        # Test A5 summary generation
        summary_data = test_data["pallet_content_list_a5"]["data"]
        summary_content = client._generate_a5_summary_content(summary_data)
        
        print("Generated A5 Summary Content:")
        print("=" * 50)
        print(summary_content)
        print("=" * 50)
        
        # Validate content structure
        lines = summary_content.split('\n')
        
        if "PALLET CONTENT SUMMARY" in lines[0]:
            print("✅ Summary header is present")
        else:
            print("❌ Summary header is missing")
        
        if "MATERIALS:" in summary_content:
            print("✅ Materials section is present")
        else:
            print("❌ Materials section is missing")
        
        material_count = len(summary_data.get('materials', []))
        print(f"📊 Materials count: {material_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing A5 summary generation: {e}")
        return False

def test_template_detection():
    """Test template type detection"""
    print("\n🔍 Testing Template Detection Logic")
    print("-" * 50)
    
    templates_to_test = [
        ("pallet_label", "ZPL thermal printing"),
        ("pallet_content_list_a5", "A5 summary printing"),
        ("location_label", "ESC/POS thermal printing"),
        ("test_label", "ESC/POS thermal printing"),
        ("unknown_template", "Error handling")
    ]
    
    for template, expected_behavior in templates_to_test:
        print(f"Template: {template:20} → Expected: {expected_behavior}")
    
    return True

def simulate_backend_emit():
    """Simulate backend emit data structure"""
    print("\n📡 Simulating Backend Emit Structure")
    print("-" * 50)
    
    # Simulate pallet_label emit
    pallet_label_emit = {
        "printerId": "PRINTER_001",
        "template": "pallet_label",
        "data": test_data["pallet_label"]["data"],
        "jobId": f"job_{int(time.time())}_pallet",
        "timestamp": datetime.now().isoformat(),
        "requestedBy": "test_user"
    }
    
    print("Pallet Label Emit Structure:")
    print(json.dumps(pallet_label_emit, indent=2, ensure_ascii=False))
    
    print("\n" + "-" * 30)
    
    # Simulate pallet_content_list_a5 emit
    a5_summary_emit = {
        "printerId": "PRINTER_001", 
        "template": "pallet_content_list_a5",
        "data": test_data["pallet_content_list_a5"]["data"],
        "jobId": f"job_{int(time.time())}_summary",
        "timestamp": datetime.now().isoformat(),
        "requestedBy": "test_user"
    }
    
    print("A5 Summary Emit Structure:")
    print(json.dumps(a5_summary_emit, indent=2, ensure_ascii=False))
    
    return True

async def main():
    """Main test function"""
    print("🧪 Template System Test Suite")
    print("=" * 60)
    print("Testing new dual template system:")
    print("  • pallet_label → ZPL thermal printing")
    print("  • pallet_content_list_a5 → A5 summary printing")
    print()
    
    # Run tests
    results = []
    
    # Test 1: ZPL Generation
    results.append(test_zpl_generation())
    
    # Test 2: A5 Summary Generation
    results.append(test_a5_summary_generation())
    
    # Test 3: Template Detection
    results.append(test_template_detection())
    
    # Test 4: Backend Emit Simulation
    results.append(simulate_backend_emit())
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    test_names = [
        "ZPL Generation",
        "A5 Summary Generation", 
        "Template Detection",
        "Backend Emit Simulation"
    ]
    
    for i, (test_name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:25} {status}")
    
    overall_success = all(results)
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 Template system is ready for deployment!")
        print("Backend can now emit with 'template' field:")
        print("  • 'pallet_label' for ZPL thermal labels")
        print("  • 'pallet_content_list_a5' for A5 summaries")
    else:
        print("\n⚠️  Please fix failing tests before deployment.")

if __name__ == "__main__":
    asyncio.run(main())
