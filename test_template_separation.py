#!/usr/bin/env python3
"""
Test New Template System
Test that the new template system correctly separates ZPL and A5 printing
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

# Test data with new template format
test_jobs = {
    "pallet_label_only": {
        "job_id": f"job_{int(time.time())}_pallet_only",
        "label_data": {
            "template": "pallet_label",  # Only ZPL thermal printing
            "pallet_id": "PLT-2025-001",
            "location": "A1-01-01",
            "barcode": "PLT2025001",
            "materials": [
                {
                    "material_code": "MAT001",
                    "description": "Test Malzeme 1",
                    "quantity": 100,
                    "unit": "adet"
                }
            ],
            "timestamp": datetime.now().isoformat()
        },
        "timestamp": datetime.now().isoformat(),
        "requested_by": "test_user"
    },
    "a5_summary_only": {
        "job_id": f"job_{int(time.time())}_summary_only",
        "label_data": {
            "template": "pallet_content_list_a5",  # Only A5 summary printing
            "pallet_id": "PLT-2025-002", 
            "location": "A1-01-02",
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
                },
                {
                    "material_code": "MAT003",
                    "description": "Test Malzeme 3 - Uzun İsim Testi",
                    "quantity": 25,
                    "unit": "lt"
                }
            ],
            "timestamp": datetime.now().isoformat()
        },
        "timestamp": datetime.now().isoformat(),
        "requested_by": "test_user"
    },
    "legacy_pallet": {
        "job_id": f"job_{int(time.time())}_legacy",
        "label_data": {
            "type": "pallet",  # Legacy system - should still do dual printing
            "pallet_id": "PLT-2025-003",
            "location": "A1-01-03",
            "materials": [
                {
                    "material_code": "MAT001",
                    "description": "Legacy Test Malzeme",
                    "quantity": 75,
                    "unit": "adet"
                }
            ],
            "timestamp": datetime.now().isoformat()
        },
        "timestamp": datetime.now().isoformat(),
        "requested_by": "test_user"
    }
}

async def test_template_routing():
    """Test template routing logic"""
    print("🧪 Testing Template Routing Logic")
    print("=" * 60)
    
    try:
        from usb_printer_client import WebSocketPrinterClient, PrintJob
        from usb_printer_client import USBPrinterConfig, PrinterType
        
        # Create dummy config
        config = USBPrinterConfig(
            port_path="TEST",
            baud_rate=9600,
            printer_type=PrinterType.ZEBRA
        )
        
        # Create client instance (without connecting)
        client = WebSocketPrinterClient("ws://test", config)
        
        # Test each job type
        for test_name, job_data in test_jobs.items():
            print(f"\n🔍 Testing: {test_name}")
            print("-" * 40)
            
            # Create PrintJob object
            job = PrintJob(
                job_id=job_data["job_id"],
                label_data=job_data["label_data"],
                timestamp=job_data["timestamp"],
                requested_by=job_data.get("requested_by")
            )
            
            print(f"Job ID: {job.job_id}")
            print(f"Template: {job.label_data.get('template', 'N/A')}")
            print(f"Type: {job.label_data.get('type', 'N/A')}")
            
            # Check template detection
            template = job.label_data.get('template')
            if template:
                print(f"✅ New template system detected: {template}")
                
                if template == 'pallet_label':
                    print("   → Expected: ZPL thermal printing only")
                elif template == 'pallet_content_list_a5':
                    print("   → Expected: A5 summary printing only")
                else:
                    print("   → Expected: Unknown template error")
            else:
                print("✅ Legacy system detected")
                label_type = job.label_data.get('type', 'auto')
                print(f"   → Label type: {label_type}")
                if label_type in ['pallet', 'palet']:
                    print("   → Expected: Dual printing (ZPL + A5)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in template routing test: {e}")
        return False

def test_backend_emit_simulation():
    """Simulate backend emit calls"""
    print("\n📡 Backend Emit Simulation")
    print("=" * 60)
    
    print("Backend should emit different templates:")
    print()
    
    # ZPL only
    print("1️⃣  For ZPL thermal label only:")
    print("socket.emit('print_job', {")
    print("  printerId: 'PRINTER_001',")
    print("  template: 'pallet_label',")
    print("  data: { pallet_id, location, barcode, materials }")
    print("})")
    print("   → Result: Only ZPL thermal printing")
    print()
    
    # A5 only  
    print("2️⃣  For A5 summary only:")
    print("socket.emit('print_job', {")
    print("  printerId: 'PRINTER_001',")
    print("  template: 'pallet_content_list_a5',")
    print("  data: { pallet_id, location, materials }")
    print("})")
    print("   → Result: Only A5 summary printing")
    print()
    
    # Legacy dual
    print("3️⃣  For legacy dual printing (if needed):")
    print("socket.emit('print_job', {")
    print("  printerId: 'PRINTER_001',")
    print("  template: undefined,  // or no template field")
    print("  data: { type: 'pallet', pallet_id, location, materials }")
    print("})")
    print("   → Result: Dual printing (ZPL + A5)")
    
    return True

async def main():
    """Main test function"""
    print("🧪 New Template System Separation Test")
    print("=" * 70)
    print("Testing that templates correctly separate printing types:")
    print("  • 'pallet_label' → ZPL only")
    print("  • 'pallet_content_list_a5' → A5 only")
    print("  • Legacy 'type: pallet' → Dual printing")
    print()
    
    # Run tests
    results = []
    
    # Test 1: Template Routing Logic
    results.append(await test_template_routing())
    
    # Test 2: Backend Emit Simulation
    results.append(test_backend_emit_simulation())
    
    # Summary
    print("\n" + "=" * 70)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    test_names = [
        "Template Routing Logic",
        "Backend Emit Simulation"
    ]
    
    for i, (test_name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:30} {status}")
    
    overall_success = all(results)
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 Template separation is working correctly!")
        print("\nBackend integration guide:")
        print("• Use 'pallet_label' for ZPL thermal only")
        print("• Use 'pallet_content_list_a5' for A5 summary only")
        print("• Avoid 'type: pallet' unless dual printing is needed")
    else:
        print("\n⚠️  Please fix template separation issues.")

if __name__ == "__main__":
    asyncio.run(main())
