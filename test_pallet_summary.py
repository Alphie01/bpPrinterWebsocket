#!/usr/bin/env python3
"""
Test Pallet Summary Generation
=============================

Test script to demonstrate the new pallet summary generation feature.
This script shows how the system now generates both thermal labels and 
A5 summary reports for pallets.

Usage:
    python test_pallet_summary.py
"""

import asyncio
import json
import time
from pallet_summary_generator import get_pallet_summary_generator


def test_pallet_summary_generation():
    """Test pallet summary generation with sample data"""
    print("🔧 Testing Pallet Summary Generation")
    print("=" * 60)
    
    # Sample pallet data
    pallet_data = {
        'palet_id': 'PLT2025001',
        'firma_adi': 'Bil Plastik Ambalaj',
        'depo_adi': 'Ana Fabrika Deposu',
        'sevkiyat_bilgisi': 'Sevkiyat Ürün Deposu',
        'hammadde_ismi': 'PE Granül Doğal',
        'urun_adi': 'Polietilen Hammadde',
        'teslim_firma': 'ABC Plastik Ltd. Şti.',
        'siparis_tarihi': '2025-08-12',
        'lot_no': 'LOT001',
        'durum': 'HAZIR',
        'brut_kg': '125.5',
        'net_kg': '124.0',
        'created_by': 'Operatör: Ahmet Y.',
        'notes': 'Kalite kontrol tamamlandı. Sevkiyata hazır.',
        
        # Detailed items on the pallet
        'items': [
            {
                'product_code': 'PE001',
                'product_name': 'PE Granül Doğal Renksiz',
                'quantity': 50,
                'unit': 'kg',
                'weight_per_unit': 1.0,
                'total_weight': 50.0,
                'lot_number': 'LOT001A',
                'production_date': '2025-08-10'
            },
            {
                'product_code': 'PE002',
                'product_name': 'PE Granül Siyah',
                'quantity': 25,
                'unit': 'kg',
                'weight_per_unit': 1.0,
                'total_weight': 25.0,
                'lot_number': 'LOT001B',
                'production_date': '2025-08-10'
            },
            {
                'product_code': 'PE003',
                'product_name': 'PE Granül Mavi',
                'quantity': 49,
                'unit': 'kg',
                'weight_per_unit': 1.0,
                'total_weight': 49.0,
                'lot_number': 'LOT001C',
                'production_date': '2025-08-11'
            }
        ]
    }
    
    # Initialize generator
    generator = get_pallet_summary_generator()
    
    print("📋 Generating HTML Summary (A5 Format)...")
    html_summary = generator.generate_html_summary(pallet_data)
    
    print("📄 Generating Text Summary...")
    text_summary = generator.generate_text_summary(pallet_data)
    
    # Save files
    import os
    output_dir = "test_summaries"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    pallet_id = pallet_data['palet_id']
    
    # Save HTML
    html_file = f"{output_dir}/pallet_summary_{pallet_id}_{timestamp}.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_summary)
    
    # Save text
    text_file = f"{output_dir}/pallet_summary_{pallet_id}_{timestamp}.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(text_summary)
    
    print("✅ Files generated successfully:")
    print(f"   📄 HTML: {html_file}")
    print(f"   📝 Text: {text_file}")
    print()
    
    # Display text summary
    print("📝 Text Summary Preview:")
    print("-" * 60)
    print(text_summary[:800] + "..." if len(text_summary) > 800 else text_summary)
    print("-" * 60)
    
    return html_file, text_file


def test_websocket_data_format():
    """Test with WebSocket format data"""
    print("\n🌐 Testing WebSocket Data Format")
    print("=" * 60)
    
    # Simulate WebSocket data format
    websocket_data = {
        'jobId': 'pallet_job_002',
        'labelType': 'pallet',
        'labelData': {
            'type': 'pallet',
            'palet_id': 'PLT2025002',
            'firma_adi': 'Bil Plastik Ambalaj',
            'depo_adi': 'Ana Fabrika',
            'teslim_firma': 'XYZ İnşaat Malzemeleri',
            'hammadde_ismi': 'LDPE Film Malzemesi',
            'siparis_tarihi': '2025-08-12',
            'durum': 'HAZIR',
            'brut_kg': '85.5',
            'net_kg': '84.0',
            'print_summary': True  # This triggers summary generation
        }
    }
    
    # Test with minimal data (like what WebSocket might send)
    generator = get_pallet_summary_generator()
    
    label_data = websocket_data['labelData']
    html_summary = generator.generate_html_summary(label_data)
    
    # Save test file
    import os
    output_dir = "test_summaries"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    html_file = f"{output_dir}/websocket_test_{timestamp}.html"
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_summary)
    
    print(f"✅ WebSocket format test completed: {html_file}")
    
    return html_file


def demonstrate_integration():
    """Demonstrate how this integrates with the printer client"""
    print("\n🔧 Integration with USB Printer Client")
    print("=" * 60)
    
    print("When a pallet label is printed:")
    print("1. 🏷️  ZPL label is sent to thermal printer")
    print("2. 📋 A5 summary is generated automatically")
    print("3. 💾 Summary files are saved to 'pallet_summaries' folder")
    print("4. 🖨️  Summary is sent to default system printer")
    print("5. 📄 If printing fails, summary opens in browser")
    print()
    
    print("Generated files include:")
    print("- HTML file (A5 format, print-ready)")
    print("- Text file (for basic printers)")
    print("- Both files contain:")
    print("  • Company and pallet information")
    print("  • Detailed item breakdown")
    print("  • Weight summaries")
    print("  • QR codes and barcodes")
    print("  • Turkish language support")


def main():
    """Main test function"""
    print("🧪 Pallet Summary Generation Test Suite")
    print("=" * 60)
    print()
    
    try:
        # Test 1: Full data test
        html_file, text_file = test_pallet_summary_generation()
        
        # Test 2: WebSocket format test
        websocket_file = test_websocket_data_format()
        
        # Test 3: Integration explanation
        demonstrate_integration()
        
        print("\n✅ All tests completed successfully!")
        print()
        print("🔍 To view the generated summaries:")
        print(f"   📄 HTML: open {html_file}")
        print(f"   📝 Text: cat {text_file}")
        print(f"   🌐 WebSocket: open {websocket_file}")
        print()
        print("📌 Next steps:")
        print("1. Test with actual pallet data")
        print("2. Configure default printer settings")
        print("3. Customize A5 layout if needed")
        print("4. Test with run_usb_client.py")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
