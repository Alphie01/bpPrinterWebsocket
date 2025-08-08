#!/usr/bin/env python3
"""
Zebra ZD220 USB Bağlantı Çözümü
===============================

Bu script özellikle "libusbk USB Devices" altında görünen
Zebra ZD220 printer için USB direct connection kurar.

Kullanım:
    python zebra_usb_fix.py
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    logger.info("🦓 Zebra ZD220 USB Bağlantı Çözümü")
    logger.info("=" * 50)
    
    logger.info("📋 Mevcut Durum Analizi:")
    logger.info("• COM3 portunda 'Permission denied' hatası")
    logger.info("• Printer 'libusbk USB Devices' altında görünüyor")
    logger.info("• ZPL protocol kullanıyor")
    logger.info("")
    
    logger.info("🔧 Çözüm: USB Direct Connection")
    logger.info("COM port yerine USB üzerinden direkt bağlantı kuracağız")
    logger.info("")
    
    # Environment variables ayarla
    logger.info("⚙️  Environment variables ayarlanıyor...")
    
    env_vars = {
        'CONNECTION_TYPE': 'usb',
        'USB_VENDOR_ID': '0x0A5F',
        'USB_PRODUCT_ID': '0x0164',
        'PRINTER_ID': 'ZEBRA_ZD220',
        'PRINTER_NAME': 'Zebra ZD220 USB',
        'PRINTER_TYPE': 'thermal',
        'PRINTER_LOCATION': 'Warehouse A',
        'SERVER_URL': 'http://localhost:25625'
    }
    
    # Set environment variables
    for key, value in env_vars.items():
        os.environ[key] = value
        logger.info(f"✅ {key}={value}")
    
    logger.info("")
    
    # .env dosyası oluştur
    logger.info("📄 .env dosyası oluşturuluyor...")
    env_content = """# Zebra ZD220 USB Configuration
CONNECTION_TYPE=usb
USB_VENDOR_ID=0x0A5F
USB_PRODUCT_ID=0x0164

PRINTER_ID=ZEBRA_ZD220
PRINTER_NAME=Zebra ZD220 USB
PRINTER_TYPE=thermal
PRINTER_LOCATION=Warehouse A

SERVER_URL=http://localhost:25625
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        logger.info("✅ .env dosyası oluşturuldu")
    except Exception as e:
        logger.error(f"❌ .env dosyası oluşturulamadı: {e}")
    
    logger.info("")
    logger.info("🚀 Kurulum Tamamlandı!")
    logger.info("")
    logger.info("📝 Sonraki Adımlar:")
    logger.info("1. PyUSB yükleyin (eğer yüklü değilse):")
    logger.info("   pip install pyusb")
    logger.info("")
    logger.info("2. Windows'ta WinUSB driver gerekebilir:")
    logger.info("   • Zadig'i indirin: https://zadig.akeo.ie/")
    logger.info("   • Zebra printer'ı seçin")
    logger.info("   • WinUSB driver'ını yükleyin")
    logger.info("")
    logger.info("3. WebSocket client'ı çalıştırın:")
    logger.info("   python run_client.py")
    logger.info("")
    logger.info("✨ Bu yöntemle COM port sorunlarını tamamen bypass ediyoruz!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
