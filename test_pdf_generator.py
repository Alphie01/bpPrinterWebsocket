#!/usr/bin/env python3
"""
Test PDF Pallet Generator
=========================

Bu script PDF palet özeti oluşturmayı test eder.
"""

import time

def test_pdf_pallet_generator():
    """PDF palet özeti test et"""
    print("📄 PDF Palet Özeti Testi")
    print("=" * 60)
    
    # Örnek palet verisi
    pallet_data = {
        'palet_id': 'PLT2025006',
        'firma_adi': 'Bil Plastik Ambalaj',
        'depo_adi': 'Ana Fabrika',
        'hammadde_ismi': 'LDPE Film',
        'urun_adi': 'Polietilen Hammadde',
        'teslim_firma': 'Test Firması Windows',
        'siparis_tarihi': '2025-08-14',
        'lot_no': 'LOT240814',
        'durum': 'HAZIR',
        'brut_kg': '32.5',
        'net_kg': '31.0',
        'items': [
            {'name': 'LDPE Film Roll A', 'weight': '10.5', 'lot': 'LOT001'},
            {'name': 'LDPE Film Roll B', 'weight': '11.0', 'lot': 'LOT002'},
            {'name': 'LDPE Film Roll C', 'weight': '9.5', 'lot': 'LOT003'}
        ]
    }
    
    print("📋 Test Verileri:")
    print(f"   🆔 Palet ID: {pallet_data['palet_id']}")
    print(f"   📦 Ürün: {pallet_data['urun_adi']}")
    print(f"   ⚖️  Brüt: {pallet_data['brut_kg']} kg")
    print(f"   📝 Items: {len(pallet_data.get('items', []))} adet")
    print()
    
    # PDF oluştur
    print("🔧 PDF Özet Oluşturuluyor...")
    try:
        from pdf_pallet_generator import get_pdf_pallet_generator
        pdf_generator = get_pdf_pallet_generator()
        
        pdf_file = pdf_generator.generate_pdf_summary(pallet_data)
        print(f"✅ PDF oluşturuldu: {pdf_file}")
        
        # Dosya boyutunu kontrol et
        import os
        if os.path.exists(pdf_file):
            size = os.path.getsize(pdf_file)
            print(f"📊 Dosya boyutu: {size:,} bytes ({size/1024:.1f} KB)")
        
        print()
        print("✅ Test tamamlandı!")
        print("🚀 Windows'ta bu PDF:")
        print("   1️⃣ PowerShell ile otomatik yazdırılacak")
        print("   2️⃣ Başarısız olursa default PDF viewer açılacak")
        print()
        print(f"📁 PDF dosyası: {pdf_file}")
        
    except ImportError as e:
        print(f"❌ PDF generator import hatası: {e}")
        print("💡 reportlab kurulumu gerekiyor: pip install reportlab")
    except Exception as e:
        print(f"❌ PDF oluşturma hatası: {e}")

if __name__ == "__main__":
    test_pdf_pallet_generator()
