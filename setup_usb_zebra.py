#!/usr/bin/env python3
"""
USB Zebra Printer Quick Setup
=============================

Bu script Zebra ZD220 printer'ını USB üzerinden direkt bağlamak için
gerekli ayarları yapar ve test eder.

Usage:
    python setup_usb_zebra.py
"""

import logging
import os
import sys
from typing import Optional

try:
    import usb.core
    import usb.util
    USB_AVAILABLE = True
except ImportError:
    USB_AVAILABLE = False
    print("❌ PyUSB bulunamadı. Yüklemek için: pip install pyusb")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Zebra printer USB IDs
ZEBRA_VID = 0x0A5F
ZEBRA_PID = 0x0164  # ZD220 için yaygın PID


def find_zebra_usb_device():
    """Zebra USB printer'ını bul"""
    logger.info("🔍 Zebra USB printer aranıyor...")
    
    # Bilinen Zebra PID'leri dene
    zebra_pids = [0x0164, 0x0161, 0x0049, 0x0061, 0x008A, 0x0078]
    
    for pid in zebra_pids:
        device = usb.core.find(idVendor=ZEBRA_VID, idProduct=pid)
        if device is not None:
            try:
                manufacturer = usb.util.get_string(device, device.iManufacturer) if device.iManufacturer else "Unknown"
                product = usb.util.get_string(device, device.iProduct) if device.iProduct else "Unknown"
                logger.info(f"✅ Zebra printer bulundu!")
                logger.info(f"   Vendor ID: 0x{ZEBRA_VID:04X}")
                logger.info(f"   Product ID: 0x{pid:04X}")
                logger.info(f"   Manufacturer: {manufacturer}")
                logger.info(f"   Product: {product}")
                return device, pid
            except Exception as e:
                logger.debug(f"Device info alınamadı: {e}")
                return device, pid
    
    logger.warning("❌ Zebra USB printer bulunamadı")
    return None, None


def check_libusb_driver():
    """libusb driver kontrolü"""
    logger.info("🔧 libusb driver kontrolü...")
    
    # Windows'ta WinUSB veya libusb driver gerekir
    if sys.platform.startswith('win'):
        logger.info("Windows sistemi tespit edildi")
        logger.info("💡 USB printer için WinUSB veya libusb driver gerekiyor")
        logger.info("   Zadig ile driver yükleyebilirsiniz: https://zadig.akeo.ie/")
        logger.info("   1. Zadig'i indirin ve çalıştırın")
        logger.info("   2. Options -> List All Devices'i seçin")
        logger.info("   3. Zebra printer'ınızı bulun")
        logger.info("   4. WinUSB driver'ını seçin ve Install/Replace tuşuna basın")


def test_usb_connection(device, pid):
    """USB bağlantısını test et"""
    logger.info("🧪 USB bağlantısı test ediliyor...")
    
    try:
        # Kernel driver'ı ayır (Linux'ta gerekli olabilir)
        if device.is_kernel_driver_active(0):
            device.detach_kernel_driver(0)
            logger.info("Kernel driver ayrıldı")
        
        # Konfigürasyonu ayarla
        device.set_configuration()
        logger.info("USB konfigürasyonu ayarlandı")
        
        # Output endpoint bul
        cfg = device.get_active_configuration()
        intf = cfg[(0, 0)]
        
        endpoint_out = usb.util.find_descriptor(
            intf,
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
        )
        
        if endpoint_out is None:
            logger.error("❌ Output endpoint bulunamadı")
            return False
        
        logger.info(f"✅ Output endpoint bulundu: 0x{endpoint_out.bEndpointAddress:02X}")
        
        # Test komutu gönder (ZPL status komutu)
        test_command = b"~HI\n"  # Host Identification komutu
        try:
            bytes_written = endpoint_out.write(test_command)
            logger.info(f"✅ Test komutu gönderildi ({bytes_written} bytes)")
            logger.info("USB bağlantısı çalışıyor!")
            return True
        except Exception as e:
            logger.error(f"❌ Test komutu gönderilemedi: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ USB bağlantı testi başarısız: {e}")
        if "access denied" in str(e).lower() or "permission" in str(e).lower():
            logger.error("💡 Driver sorunu olabilir. Zadig ile WinUSB driver yükleyin.")
        return False


def create_env_file(vid, pid):
    """Environment file oluştur"""
    env_content = f"""# USB Zebra Printer Configuration
CONNECTION_TYPE=usb
USB_VENDOR_ID=0x{vid:04X}
USB_PRODUCT_ID=0x{pid:04X}

# Printer Configuration
PRINTER_ID=ZEBRA_ZD220
PRINTER_NAME=Zebra ZD220 USB
PRINTER_TYPE=thermal
PRINTER_LOCATION=Warehouse A

# Server Configuration
SERVER_URL=http://192.168.1.139:25625
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        logger.info("✅ .env dosyası oluşturuldu")
        logger.info("Bu ayarlarla WebSocket client'ı çalıştırabilirsiniz")
    except Exception as e:
        logger.error(f"❌ .env dosyası oluşturulamadı: {e}")


def main():
    logger.info("🚀 Zebra USB Printer Kurulum Aracı")
    logger.info("=" * 50)
    
    if not USB_AVAILABLE:
        logger.error("❌ PyUSB gerekli ama yüklü değil")
        logger.error("Yüklemek için: pip install pyusb")
        return 1
    
    # USB device ara
    device, pid = find_zebra_usb_device()
    if device is None:
        logger.error("❌ Zebra USB printer bulunamadı")
        logger.error("Kontrol listesi:")
        logger.error("1. Printer USB ile bağlı mı?")
        logger.error("2. Printer açık mı?")
        logger.error("3. USB kablosu çalışıyor mu?")
        logger.error("4. Windows Device Manager'da görünüyor mu?")
        return 1
    
    # Driver kontrolü
    check_libusb_driver()
    
    # Bağlantı testi
    if test_usb_connection(device, pid):
        logger.info("🎉 USB bağlantısı başarılı!")
        
        # Environment dosyası oluştur
        create_env_file(ZEBRA_VID, pid)
        
        logger.info("🚀 Kurulum tamamlandı!")
        logger.info("WebSocket client'ı şu komutla çalıştırın:")
        logger.info("python run_client.py")
        
        return 0
    else:
        logger.error("❌ USB bağlantısı başarısız")
        logger.error("Driver kurulumu gerekebilir:")
        logger.error("1. Zadig'i indirin: https://zadig.akeo.ie/")
        logger.error("2. Zebra printer için WinUSB driver yükleyin")
        logger.error("3. Bu script'i tekrar çalıştırın")
        return 1


if __name__ == "__main__":
    sys.exit(main())
