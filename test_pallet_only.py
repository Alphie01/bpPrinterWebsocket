#!/usr/bin/env python3
"""
Test Pallet Label Only
=====================

Bu script sadece palet ZPL etiketinin çalışıp çalışmadığını test eder.
Özet yazdırma devre dışı bırakılmış durumda.
"""

import time
from label_generators import get_label_generator

def test_pallet_label_only():
    """Sadece palet ZPL etiketi test et"""
    print("🏷️  Palet ZPL Etiket Testi (Özet Yazdırma Kapalı)")
    print("=" * 60)
    
    # Örnek palet verisi
    pallet_data = {
        'type': 'pallet',
        'palet_id': 'PLT2025004',
        'firma_adi': 'Bil Plastik Ambalaj',
        'depo_adi': 'Ana Fabrika',
        'hammadde_ismi': 'LDPE Film',
        'urun_adi': 'Polietilen Hammadde',
        'teslim_firma': 'Test Firması',
        'siparis_tarihi': '2025-08-14',
        'lot_no': 'LOT240814',
        'durum': 'HAZIR',
        'brut_kg': '25.5',
        'net_kg': '24.0',
        'print_summary': False  # Özet yazdırma kapalı
    }
    
    print("📋 Test Verileri:")
    print(f"   🆔 Palet ID: {pallet_data['palet_id']}")
    print(f"   📦 Ürün: {pallet_data['urun_adi']}")
    print(f"   ⚖️  Brüt: {pallet_data['brut_kg']} kg")
    print(f"   📄 Özet: {'✅ Aktif' if pallet_data.get('print_summary', False) else '❌ Kapalı'}")
    print()
    
    # ZPL etiket oluştur
    print("🔧 ZPL Etiket Oluşturuluyor...")
    label_generator = get_label_generator("zpl")
    zpl_command = label_generator.generate_pallet_label(pallet_data)
    
    print(f"✅ ZPL komutu oluşturuldu ({len(zpl_command)} karakter)")
    
    # ZPL'i dosyaya kaydet
    import os
    output_dir = "test_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    zpl_file = f"{output_dir}/pallet_only_{pallet_data['palet_id']}_{timestamp}.zpl"
    
    with open(zpl_file, 'w', encoding='utf-8') as f:
        f.write(zpl_command)
    
    print(f"💾 ZPL dosyası: {zpl_file}")
    print()
    
    # ZPL'nin başını göster
    print("📄 ZPL İçeriği (İlk 10 satır):")
    print("-" * 40)
    lines = zpl_command.split('\n')
    for i, line in enumerate(lines[:10]):
        print(f"{i+1:2d}: {line}")
    if len(lines) > 10:
        print(f"... (toplam {len(lines)} satır)")
    print("-" * 40)
    print()
    
    print("✅ Test tamamlandı!")
    print("🏷️  Sadece ZPL etiket oluşturuldu, özet yazdırma yapılmadı")
    print(f"📁 Dosya: {zpl_file}")

if __name__ == "__main__":
    test_pallet_label_only()
