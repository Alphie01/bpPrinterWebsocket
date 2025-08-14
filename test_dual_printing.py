#!/usr/bin/env python3
"""
Test Dual Pallet Printing
=========================

Bu script hem ZPL etiketi hem de A5 özet yazdırmayı test eder.
"""

import time
from label_generators import get_label_generator

def test_dual_pallet_printing():
    """Hem ZPL etiketi hem A5 özeti test et"""
    print("🏷️ + 📄 Dual Palet Yazdırma Testi")
    print("=" * 60)
    
    # Örnek palet verisi
    pallet_data = {
        'type': 'pallet',
        'palet_id': 'PLT2025005',
        'firma_adi': 'Bil Plastik Ambalaj',
        'depo_adi': 'Ana Fabrika',
        'hammadde_ismi': 'LDPE Film',
        'urun_adi': 'Polietilen Hammadde',
        'teslim_firma': 'Test Firması',
        'siparis_tarihi': '2025-08-14',
        'lot_no': 'LOT240814',
        'durum': 'HAZIR',
        'brut_kg': '28.5',
        'net_kg': '27.0',
        'items': [
            {'name': 'LDPE Film Roll 1', 'weight': '9.0', 'lot': 'LOT001'},
            {'name': 'LDPE Film Roll 2', 'weight': '9.5', 'lot': 'LOT002'},
            {'name': 'LDPE Film Roll 3', 'weight': '8.5', 'lot': 'LOT003'}
        ]
    }
    
    print("📋 Test Verileri:")
    print(f"   🆔 Palet ID: {pallet_data['palet_id']}")
    print(f"   📦 Ürün: {pallet_data['urun_adi']}")
    print(f"   ⚖️  Brüt: {pallet_data['brut_kg']} kg")
    print(f"   📝 Items: {len(pallet_data.get('items', []))} adet")
    print()
    
    # 1. ZPL etiket oluştur
    print("🔧 1️⃣ ZPL Etiket Oluşturuluyor...")
    label_generator = get_label_generator("zpl")
    zpl_command = label_generator.generate_pallet_label(pallet_data)
    print(f"   ✅ ZPL komutu oluşturuldu ({len(zpl_command)} karakter)")
    
    # 2. A5 özet oluştur (simulation)
    print("🔧 2️⃣ A5 Özet Hazırlanıyor...")
    try:
        from pallet_summary_generator import get_pallet_summary_generator
        summary_generator = get_pallet_summary_generator()
        
        # HTML özet
        html_content = summary_generator.generate_html_summary(pallet_data)
        print(f"   ✅ HTML özet oluşturuldu ({len(html_content)} karakter)")
        
        # Text özet  
        text_content = summary_generator.generate_text_summary(pallet_data)
        print(f"   ✅ Text özet oluşturuldu ({len(text_content)} karakter)")
        
    except ImportError as e:
        print(f"   ❌ Özet generator bulunamadı: {e}")
        return
    
    # Dosyaları kaydet
    import os
    output_dir = "test_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    pallet_id = pallet_data['palet_id']
    
    # ZPL dosyası
    zpl_file = f"{output_dir}/dual_zpl_{pallet_id}_{timestamp}.zpl"
    with open(zpl_file, 'w', encoding='utf-8') as f:
        f.write(zpl_command)
    
    # HTML dosyası
    html_file = f"{output_dir}/dual_summary_{pallet_id}_{timestamp}.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Text dosyası
    text_file = f"{output_dir}/dual_summary_{pallet_id}_{timestamp}.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(text_content)
    
    print()
    print("💾 Dosyalar:")
    print(f"   🏷️  ZPL Etiket: {zpl_file}")
    print(f"   📄 HTML Özet: {html_file}")
    print(f"   📝 Text Özet: {text_file}")
    print()
    
    print("✅ Test tamamlandı!")
    print("🚀 Sistem şimdi:")
    print("   1️⃣ ZPL etiketi → Termal yazıcıya gönderir")
    print("   2️⃣ A5 özeti → Varsayılan yazıcıya gönderir")

if __name__ == "__main__":
    test_dual_pallet_printing()
