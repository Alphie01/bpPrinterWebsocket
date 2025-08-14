#!/usr/bin/env python3
"""
Turkish Font Test
================
"""

def test_turkish_characters():
    """Test Turkish character handling"""
    print("🇹🇷 Turkish Font Test")
    print("=" * 50)
    
    # Test data with Turkish characters
    pallet_data = {
        'palet_id': 'PLT2025TÜRKÇE',
        'firma_adi': 'Bil Plastik Ambalaj Şirketi',
        'depo_adi': 'İstanbul Merkez Deposu',
        'teslim_firma': 'Müşteri Şirketi Ltd. Şti.',
        'siparis_tarihi': '2025-08-14',
        'durum': 'HAZIR',
        'brut_kg': '45.5',
        'net_kg': '44.8',
        'items': [
            {'name': 'Özel Ürün Çeşidi', 'weight': '15.2', 'lot': 'LOT001'},
            {'name': 'İkinci Ürün Türü', 'weight': '14.8', 'lot': 'LOT002'},
            {'name': 'Üçüncü Ürün Grubu', 'weight': '14.8', 'lot': 'LOT003'}
        ]
    }
    
    print("📋 Turkish Test Data:")
    for key, value in pallet_data.items():
        if key != 'items':
            print(f"   {key}: {value}")
    print(f"   items: {len(pallet_data['items'])} adet")
    print()
    
    try:
        from pdf_pallet_generator import get_pdf_pallet_generator
        
        pdf_generator = get_pdf_pallet_generator()
        pdf_file = pdf_generator.generate_pdf_summary(pallet_data)
        
        print(f"✅ Turkish PDF generated: {pdf_file}")
        
        import os
        if os.path.exists(pdf_file):
            size = os.path.getsize(pdf_file)
            print(f"📊 File size: {size:,} bytes")
            
            # Open PDF to check
            print("📖 Opening PDF to check Turkish characters...")
            os.system(f"open '{pdf_file}'")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_turkish_characters()
