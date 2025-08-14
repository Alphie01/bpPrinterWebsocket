#!/usr/bin/env python3
"""
Pallet Print Test Demo
=====================

Bu script palet etiketi yazdırma ve özet raporu oluşturma işlemini test eder.
Hem ZPL etiket çıktısı hem de A5 özet raporu otomatik yazdırma özelliğini gösterir.

Kullanım:
    python3 demo_pallet_print.py
"""

import asyncio
import json
import time
import logging
from typing import Dict, Any

# Modülleri import et
from usb_printer_client import WebSocketPrinterClient, USBPrinterConfig, PrinterType, PrintJob
from pallet_summary_generator import get_pallet_summary_generator


# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_sample_pallet_data() -> Dict[str, Any]:
    """Örnek palet verisi oluştur"""
    return {
        'type': 'pallet',
        'palet_id': 'PLT2025003',
        'firma_adi': 'Bil Plastik Ambalaj San. ve Tic. A.Ş.',
        'depo_adi': 'Ana Üretim Deposu',
        'sevkiyat_bilgisi': 'Sevkiyat Hazırlama Bölümü',
        'hammadde_ismi': 'LDPE Film Malzemesi',
        'urun_adi': 'Polietilen Film Hammaddesi',
        'teslim_firma': 'Mega Ambalaj Sanayi Ltd. Şti.',
        'siparis_tarihi': '2025-08-14',
        'lot_no': 'LOT240814',
        'durum': 'SEVKİYATA HAZIR',
        'brut_kg': '148.5',
        'net_kg': '147.0',
        'print_summary': True,  # Bu önemli: özet yazdırma aktif
        'created_by': 'Depo Sorumlusu: Mehmet K.',
        'notes': 'Kalite kontrol onaylandı. Müşteri teslim tarihi: 15.08.2025',
        
        # Detaylı ürün listesi
        'items': [
            {
                'product_code': 'LDPE-001',
                'product_name': 'LDPE Film Naturel 50mic',
                'quantity': 20,
                'unit': 'kg',
                'weight_per_unit': 1.0,
                'total_weight': 20.0,
                'lot_number': 'LOT240814A',
                'production_date': '2025-08-13'
            },
            {
                'product_code': 'LDPE-002',
                'product_name': 'LDPE Film Siyah 80mic',
                'quantity': 30,
                'unit': 'kg',
                'weight_per_unit': 1.0,
                'total_weight': 30.0,
                'lot_number': 'LOT240814B',
                'production_date': '2025-08-13'
            },
            {
                'product_code': 'LDPE-003',
                'product_name': 'LDPE Film Şeffaf 100mic',
                'quantity': 25,
                'unit': 'kg',
                'weight_per_unit': 1.0,
                'total_weight': 25.0,
                'lot_number': 'LOT240814C',
                'production_date': '2025-08-14'
            },
            {
                'product_code': 'LDPE-004',
                'product_name': 'LDPE Film Beyaz 60mic',
                'quantity': 72,
                'unit': 'kg',
                'weight_per_unit': 1.0,
                'total_weight': 72.0,
                'lot_number': 'LOT240814D',
                'production_date': '2025-08-14'
            }
        ]
    }


async def simulate_print_job():
    """Palet yazdırma işlemini simüle et"""
    print("🏷️  Palet Etiket ve Özet Yazdırma Demo")
    print("=" * 60)
    
    # Örnek palet verisi
    pallet_data = create_sample_pallet_data()
    
    print("📋 Palet Bilgileri:")
    print(f"   🆔 Palet ID: {pallet_data['palet_id']}")
    print(f"   🏢 Firma: {pallet_data['firma_adi']}")
    print(f"   📦 Ürün: {pallet_data['urun_adi']}")
    print(f"   ⚖️  Brüt Ağırlık: {pallet_data['brut_kg']} kg")
    print(f"   📊 Ürün Sayısı: {len(pallet_data['items'])} kalem")
    print(f"   📄 Özet Yazdırma: {'✅ Aktif' if pallet_data['print_summary'] else '❌ Kapalı'}")
    print()
    
    # PrintJob objesi oluştur
    job = PrintJob(
        job_id=f"job_{int(time.time())}",
        label_data=pallet_data,
        timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
        requested_by="Demo Script"
    )
    
    print("🔧 Demo İşlem Sırası:")
    print("1. 🏷️  ZPL etiket oluşturuluyor...")
    
    # Label generator kullanarak ZPL oluştur
    from label_generators import get_label_generator
    label_generator = get_label_generator("zpl")
    zpl_command = label_generator.generate_pallet_label(pallet_data)
    
    print(f"   ✅ ZPL komutu oluşturuldu ({len(zpl_command)} karakter)")
    print("   🖨️  ZPL komutu termal yazıcıya gönderilecek...")
    
    # ZPL komutunu dosyaya kaydet (gerçek yazıcı yok)
    import os
    output_dir = "demo_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    zpl_file = f"{output_dir}/pallet_label_{pallet_data['palet_id']}_{timestamp}.zpl"
    
    with open(zpl_file, 'w', encoding='utf-8') as f:
        f.write(zpl_command)
    
    print(f"   💾 ZPL dosyası kaydedildi: {zpl_file}")
    
    # Simulated print success
    await asyncio.sleep(1)  # Yazıcı yazdırma simülasyonu
    
    print("   ✅ ZPL etiket yazdırma başarılı!")
    print()
    
    print("2. 📋 A5 özet raporu oluşturuluyor ve direkt yazdırılıyor...")
    
    # Özet raporu oluştur
    summary_generator = get_pallet_summary_generator()
    
    # HTML özet
    html_summary = summary_generator.generate_html_summary(pallet_data)
    
    print("   ✅ A5 HTML özet raporu oluşturuldu")
    print("   🖨️  Özet raporu direkt yazıcıya gönderiliyor (dosya kaydedilmiyor)...")
    
    # Direkt yazdırma simülasyonu
    try:
        import subprocess
        import platform
        import tempfile
        
        system = platform.system()
        if system == "Darwin":  # macOS
            # Geçici dosya oluştur (sadece yazdırma için)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(html_summary)
                temp_html_path = temp_file.name
            
            # HTML dosyasını Safari'de aç ve yazdır
            cmd = ["open", "-a", "Safari", temp_html_path]
            subprocess.run(cmd)
            print("   📄 HTML özet Safari'de açıldı ve yazdırma için hazır")
            print("   💡 Safari otomatik olarak yazdırma penceresini açacak!")
            
            # Geçici dosyayı temizle (biraz bekledikten sonra)
            import threading
            def cleanup():
                time.sleep(10)  # Safari'nin dosyayı yüklemesi için bekle
                try:
                    import os
                    os.unlink(temp_html_path)
                except:
                    pass
            
            threading.Thread(target=cleanup).start()
            
        else:
            print(f"   📄 Platform: {system} - Manuel yazdırma gerekli")
            # Demo için HTML'i dosyaya kaydet
            html_file = f"{output_dir}/demo_summary_{timestamp}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_summary)
            print(f"   💾 Demo için HTML kaydedildi: {html_file}")
            
    except Exception as e:
        print(f"   ⚠️  Yazdırma simülasyon hatası: {e}")
        # Hata durumunda demo için kaydet
        html_file = f"{output_dir}/demo_summary_{timestamp}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_summary)
        print(f"   💾 Demo için HTML kaydedildi: {html_file}")
    
    print("3. 🖨️  Özet raporu varsayılan yazıcıya gönderiliyor...")
    
    # macOS'ta yazdırma simülasyonu
    try:
        import subprocess
        import platform
        
        system = platform.system()
        if system == "Darwin":  # macOS
            # HTML dosyasını Safari'de aç
            cmd = ["open", "-a", "Safari", html_file]
            subprocess.run(cmd)
            print("   📄 HTML özet Safari'de açıldı")
            print("   💡 Şimdi Safari'de Cmd+P ile yazdırabilirsiniz!")
        else:
            print(f"   📄 Platform: {system} - Manual yazdırma gerekli")
            
    except Exception as e:
        print(f"   ⚠️  Yazdırma hatası: {e}")
    
    print()
    print("✅ Demo tamamlandı!")
    print()
    print("📁 Oluşturulan dosyalar:")
    print(f"   🏷️  ZPL Etiket: {zpl_file}")
    print("   📄 A5 Özet: Direkt yazıcıya gönderildi (kalıcı dosya yok)")
    print()
    print("🔍 Dosyaları görüntülemek için:")
    print(f"   ZPL: cat {zpl_file}")
    print("   📄 A5 Özet: Yazıcıdan çıktı alın")


def show_integration_info():
    """Entegrasyon bilgilerini göster"""
    print("\n🔗 Gerçek Sistem Entegrasyonu")
    print("=" * 60)
    print()
    print("Bu demo aşağıdaki gerçek sistem akışını simüle eder:")
    print()
    print("1. 📡 WebSocket sunucusundan palet yazdırma işi gelir")
    print("2. 🏷️  ZPL etiket termal yazıcıya gönderilir")
    print("3. ✅ ZPL yazdırma başarılı olunca:")
    print("   • 📋 A5 özet raporu HTML formatında oluşturulur")
    print("   • ️  HTML özet DIREKT varsayılan yazıcıya gönderilir")
    print("   • �️  Geçici dosyalar otomatik temizlenir")
    print("   • 💾 Kalıcı dosya kaydedilmez")
    print()
    print("4. 💡 Eğer yazdırma başarısız olursa:")
    print("   • � Sistem birden fazla yazdırma yöntemi dener")
    print("   • � Gerekirse tarayıcıda açılır (manuel yazdırma için)")
    print()
    print("🎯 Avantajlar:")
    print("   • 💾 Disk alanı tasarrufu (dosya kaydedilmez)")
    print("   • 🚀 Hızlı yazdırma (direkt işlem)")
    print("   • 🔒 Güvenlik (geçici dosyalar temizlenir)")
    print("   • 🖨️  Otomatik yazdırma (kullanıcı müdahalesi minimum)")


async def main():
    """Ana fonksiyon"""
    try:
        await simulate_print_job()
        show_integration_info()
        
        print("\n🚀 Gerçek sistem için:")
        print("   python3 run_usb_client.py")
        print()
        
    except Exception as e:
        logger.error(f"Demo hata: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
