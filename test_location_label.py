#!/usr/bin/env python3
"""
Test script for location label generation with new location.zpl template
"""

from label_generators import get_label_generator

def test_location_label():
    # Sample location data similar to what WebSocket sends
    test_data = {
        'type': 'location',
        'id': 900,
        'barcode': 'LOC000900', 
        'locationName': 'Mamul Alanı',
        'warehouseCode': 'DEPO-01',
        'locationType': 'AREA',
        'createdAt': '2025-08-07T06:40:25.994Z',
        'printedAt': '2025-08-12T06:12:51.660Z',
        'template': 'location_label'
    }
    
    print("Testing location label generation with location.zpl template...")
    print(f"Test data: {test_data}")
    print("\n" + "="*60)
    
    # Generate label using ZPL generator
    label_generator = get_label_generator("zpl")
    zpl_command = label_generator.generate_location_label(test_data)
    
    print("Generated ZPL command:")
    print(f"Length: {len(zpl_command)} characters")
    print("\n" + "="*60)
    print(zpl_command)
    print("="*60)
    
    print(f"\n✅ Location label generated successfully!")
    print(f"📏 ZPL command length: {len(zpl_command)} characters")
    
    # Test with different location ID
    print("\n" + "="*60)
    print("Testing with different location ID...")
    
    test_data2 = test_data.copy()
    test_data2['id'] = 5
    test_data2['barcode'] = 'LOC000005'
    test_data2['locationName'] = 'Hammadde Deposu'
    test_data2['warehouseCode'] = 'DEPO-02'
    
    zpl_command2 = label_generator.generate_location_label(test_data2)
    print(f"Location ID 5 ZPL length: {len(zpl_command2)} characters")
    
    # Show key differences
    if '{i}' in zpl_command2:
        print("❌ Template placeholder {i} not replaced!")
    else:
        print("✅ Template placeholder {i} successfully replaced")
        
    print(f"Looking for 'DP-S-51' and 'DP-S-52' in output...")
    if 'DP-S-51' in zpl_command2 and 'DP-S-52' in zpl_command2:
        print("✅ Location ID properly inserted into DP-S-{i}1 and DP-S-{i}2 patterns")
    else:
        print("❌ Location ID not properly inserted")
    
    if 'Hammadde Deposu' in zpl_command2:
        print("✅ Custom location name inserted")
    else:
        print("❌ Custom location name not inserted")
        
    if 'DEPO-02' in zpl_command2:
        print("✅ Custom warehouse code inserted")
    else:
        print("❌ Custom warehouse code not inserted")

if __name__ == "__main__":
    test_location_label()
