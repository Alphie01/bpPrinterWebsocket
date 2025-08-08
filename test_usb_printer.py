#!/usr/bin/env python3
"""
USB Printer Test Script
======================

Simple test script to demonstrate direct USB printer communication
without any COM port dependencies. This script is based on the main.py
implementation and can be used to test USB printer connectivity.

Usage:
    python test_usb_printer.py
"""

import json
import time
import logging
import os
from typing import Dict, Any, List
import sys

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    logging.warning("python-dotenv not available. Install with: pip install python-dotenv")

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from usb_direct_printer import DirectUSBPrinter, send_zpl_to_printer_via_usb
    USB_AVAILABLE = True
except ImportError as e:
    print(f"ERROR: Could not import USB printer module: {e}")
    print("Make sure pyusb is installed: pip install pyusb")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_zpl_label(
    firma, production_date, lot_code, product_code, product_name, personel_code,
    total_amount, qr_code, bom, hat_kodu, siparis_kodu, firma_kodu, adet_bilgisi,
    uretim_miktari_checked=True, adet_girisi_checked=True,
    firma_bilgileri_checked=True, brut_kg_checked=True
):
    """
    Generate ZPL label (same as main.py implementation)
    """
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


def test_simple_print():
    """Test simple ZPL print"""
    print("\\n=== Testing Simple ZPL Print ===")
    
    # Simple test ZPL
    test_zpl = "^XA^FO50,50^A0N,50,50^FDTest Print USB^FS^XZ"
    
    print("Sending simple test print...")
    success = send_zpl_to_printer_via_usb(test_zpl)
    
    if success:
        print("✓ Simple test print sent successfully")
    else:
        print("✗ Simple test print failed")
    
    return success


def test_custom_label():
    """Test custom label print (like main.py)"""
    print("\\n=== Testing Custom Label Print ===")
    
    # Generate a test label
    zpl_label = generate_zpl_label(
        "T. İŞ BANKASI A.Ş DESTEL",
        "2025-08-08",
        "98649 - 004",
        "TEST_LABEL_001",
        "(LDPE) SEFFAF 12 DELiKLi PARA TORBASI BASKISIZ SEFFAF 100 Mic 38x60",
        "TEST001",
        "100",
        "TEST_LABEL_001",
        "",
        "S",
        "",
        "NAYLON PARA POSETI BÜYÜK",
        "250",
        brut_kg_checked=False,
        uretim_miktari_checked=False,
        adet_girisi_checked=True,
        firma_bilgileri_checked=True
    )
    
    print(f"Generated ZPL (length: {len(zpl_label)} chars)")
    print("Sending custom label...")
    
    success = send_zpl_to_printer_via_usb(zpl_label)
    
    if success:
        print("✓ Custom label sent successfully")
    else:
        print("✗ Custom label failed")
    
    return success


def test_with_json_data():
    """Test with JSON data (like main.py)"""
    print("\\n=== Testing with JSON Data ===")
    
    # Create test data similar to data_IS.json
    test_data = [
        {
            "tarih": "2025-08-08",
            "etiket": "TEST_001",
            "sicil": "001",
            "total_amount": "150"
        },
        {
            "tarih": "2025-08-08", 
            "etiket": "TEST_002",
            "sicil": "002",
            "total_amount": "200"
        }
    ]
    
    print(f"Processing {len(test_data)} test records...")
    
    success_count = 0
    for i, obj in enumerate(test_data, 1):
        print(f"\\nProcessing record {i}/{len(test_data)}...")
        
        zpl_label = generate_zpl_label(
            "T. İŞ BANKASI A.Ş DESTEL",
            obj['tarih'],
            "98649 - 004",
            obj['etiket'],
            "(LDPE) SEFFAF 12 DELiKLi PARA TORBASI BASKISIZ SEFFAF 100 Mic 38x60",
            obj['sicil'],
            obj.get("total_amount", "100"),
            obj['etiket'],
            "",
            "S",
            "",
            "NAYLON PARA POSETI BÜYÜK",
            "250",
            brut_kg_checked=False,
            uretim_miktari_checked=False,
            adet_girisi_checked=True,
            firma_bilgileri_checked=True
        )
        
        print(f"  Label ID: {obj['etiket']}")
        success = send_zpl_to_printer_via_usb(zpl_label)
        
        if success:
            print(f"  ✓ Record {i} sent successfully")
            success_count += 1
        else:
            print(f"  ✗ Record {i} failed")
    
    print(f"\\nCompleted: {success_count}/{len(test_data)} successful")
    return success_count == len(test_data)


def test_printer_interface():
    """Test the DirectUSBPrinter interface"""
    print("\\n=== Testing DirectUSBPrinter Interface ===")
    
    # List available printers
    printers = DirectUSBPrinter.list_available_printers()
    print(f"Found {len(printers)} USB printer(s):")
    
    for i, printer in enumerate(printers, 1):
        print(f"  {i}. {printer['manufacturer']} {printer['model']}")
        print(f"     Type: {printer['type']}, VID: 0x{printer['vendor_id']:04X}, PID: 0x{printer['product_id']:04X}")
    
    if not printers:
        print("  No USB printers found")
        return False
    
    # Test connection to first printer
    print(f"\\nTesting connection to first printer...")
    printer = DirectUSBPrinter(auto_detect=True)
    
    if printer.connect():
        info = printer.get_printer_info()
        print(f"✓ Connected: {info}")
        
        # Test simple print
        test_zpl = "^XA^FO50,50^A0N,50,50^FDInterface Test^FS^XZ"
        if printer.send_zpl_command(test_zpl):
            print("✓ Test print sent via interface")
            success = True
        else:
            print("✗ Test print failed via interface")
            success = False
        
        printer.disconnect()
        print("✓ Disconnected")
        
        return success
    else:
        print("✗ Connection failed")
        return False


def main():
    """Main test function"""
    print("USB Printer Test Script")
    print("======================")
    print("Testing direct USB communication (no COM ports)")
    print()
    
    # Check available printers
    printers = DirectUSBPrinter.list_available_printers()
    if not printers:
        print("ERROR: No USB printers found!")
        print()
        print("Please make sure:")
        print("1. A supported USB printer is connected")
        print("2. The printer is powered on")
        print("3. PyUSB is installed (pip install pyusb)")
        print()
        print("Supported printers:")
        print("- Zebra thermal printers (ZD410, ZD420, GK420d, etc.)")
        print("- Brother label printers")
        print("- Epson thermal printers")
        return False
    
    print(f"Found {len(printers)} USB printer(s). Starting tests...\\n")
    
    # Run tests
    tests = [
        ("Printer Interface", test_printer_interface),
        ("Simple Print", test_simple_print),
        ("Custom Label", test_custom_label),
        ("JSON Data Processing", test_with_json_data)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            print(f"\\n{'='*60}")
            print(f"Running: {test_name}")
            print('='*60)
            
            result = test_func()
            results[test_name] = result
            
            if result:
                print(f"\\n✓ {test_name} PASSED")
            else:
                print(f"\\n✗ {test_name} FAILED")
                
        except Exception as e:
            print(f"\\n✗ {test_name} ERROR: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<30} {status}")
    
    print(f"\\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\\n🎉 All tests passed! USB printer communication is working correctly.")
    else:
        print(f"\\n⚠️  {total - passed} test(s) failed. Check printer connection and configuration.")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\\n\\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\\n\\nFatal error: {e}")
        sys.exit(1)
