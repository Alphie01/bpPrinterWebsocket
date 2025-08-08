# USB-Only WebSocket Printer Client

Bu proje, COM port bağımlılıklarını kaldırarak sadece doğrudan USB iletişimi kullanan WebSocket printer client'ıdır. Tüm seri port (COM port) iletişimi kaldırılmış ve sadece USB üzerinden direkt yazıcı iletişimi sağlanmaktadır.

## Özellikler

- ✅ **Doğrudan USB İletişimi**: COM port olmadan direkt USB üzerinden yazıcı iletişimi
- ✅ **WebSocket Bağlantısı**: Print server ile WebSocket üzerinden bağlantı
- ✅ **ZPL Desteği**: Zebra yazıcılar için ZPL komut desteği
- ✅ **Otomatik Yazıcı Tespiti**: Desteklenen USB yazıcıların otomatik tespiti
- ✅ **Hata Yönetimi**: Kapsamlı hata yönetimi ve yeniden bağlanma mantığı
- ❌ **COM Port Yok**: Seri port bağımlılıkları tamamen kaldırıldı

## Desteklenen Yazıcılar

### Zebra Yazıcılar
- ZD410/ZD420 (VID: 0x0A5F, PID: 0x0164)
- ZD510 (VID: 0x0A5F, PID: 0x0181)
- GC420t (VID: 0x0A5F, PID: 0x0049)
- GK420t/GK420d (VID: 0x0A5F, PID: 0x0061/0x0078)
- ZT410/ZT411 (VID: 0x0A5F, PID: 0x008A/0x0166)

### Brother Yazıcılar
- QL-700 (VID: 0x04F9, PID: 0x2028)
- QL-710W (VID: 0x04F9, PID: 0x202A)
- QL-720NW (VID: 0x04F9, PID: 0x202B)
- QL-800/QL-820NWB (VID: 0x04F9, PID: 0x2100/0x209D)

### Epson Yazıcılar
- TM-T20 (VID: 0x04B8, PID: 0x0202)
- TM-T88/TM-T88V (VID: 0x04B8, PID: 0x0203/0x0204)

## Kurulum

### 1. Gereksinimler
```bash
pip install -r requirements.txt
```

**Önemli**: PyUSB için sistem bağımlılıkları:

**macOS:**
```bash
brew install libusb
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install libusb-1.0-0-dev
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install libusb1-devel
```

### 2. USB İzinleri (Linux)
Linux'ta USB yazıcılara erişim için kullanıcı izinleri gerekebilir:

```bash
# Kullanıcıyı dialout grubuna ekle
sudo usermod -a -G dialout $USER

# Veya udev kuralı oluştur
sudo nano /etc/udev/rules.d/99-usb-printer.rules
```

Udev kuralı içeriği:
```
# Zebra printers
SUBSYSTEM=="usb", ATTR{idVendor}=="0a5f", MODE="0666"
# Brother printers  
SUBSYSTEM=="usb", ATTR{idVendor}=="04f9", MODE="0666"
# Epson printers
SUBSYSTEM=="usb", ATTR{idVendor}=="04b8", MODE="0666"
```

## Kullanım

### 1. Mevcut USB Yazıcıları Listele
```bash
python test_usb_printer.py
```

### 2. WebSocket Client Başlat
```bash
python run_usb_client.py
```

### 3. Ortam Değişkenleri ile Yapılandırma
```bash
export PRINTER_ID="USB_PRINTER_001"
export PRINTER_NAME="Zebra ZD420"
export PRINTER_TYPE="zebra"
export PRINTER_LOCATION="Warehouse A"
export SERVER_URL="http://localhost:25625"
export USB_VENDOR_ID="0x0A5F"
export USB_PRODUCT_ID="0x0164"
export AUTO_DETECT="true"

python run_usb_client.py
```

## Dosya Yapısı

### Yeni USB-Only Dosyalar
- `usb_direct_printer.py` - Doğrudan USB yazıcı arayüzü
- `usb_printer_client.py` - USB-only WebSocket client
- `run_usb_client.py` - USB client başlatıcı
- `test_usb_printer.py` - USB yazıcı test scripti

### Eski Dosyalar (COM Port İçeren)
- `printer_client.py` - Eski hibrit client (serial + USB)
- `run_client.py` - Eski client başlatıcı
- `usb_printer.py` - Eski USB arayüzü

## API Kullanımı

### Basit ZPL Gönderme
```python
from usb_direct_printer import send_zpl_to_printer_via_usb

# Basit ZPL komutu gönder
zpl = "^XA^FO50,50^A0N,50,50^FDTest Print^FS^XZ"
success = send_zpl_to_printer_via_usb(zpl)
```

### Arayüz Kullanımı
```python
from usb_direct_printer import DirectUSBPrinter

# Yazıcı oluştur ve bağlan
printer = DirectUSBPrinter(auto_detect=True)
if printer.connect():
    # ZPL gönder
    printer.send_zpl_command("^XA^FO50,50^A0N,50,50^FDTest^FS^XZ")
    printer.disconnect()
```

### WebSocket Client
```python
from usb_printer_client import WebSocketPrinterClient, USBPrinterConfig, PrinterType

# Yapılandırma oluştur
config = USBPrinterConfig(
    printer_id="USB_PRINTER_001",
    printer_name="Zebra ZD420",
    printer_type=PrinterType.ZEBRA,
    location="Warehouse A",
    auto_detect=True
)

# Client başlat
client = WebSocketPrinterClient("http://localhost:25625", config)
await client.start()
```

## main.py ile Uyumluluk

Mevcut `main.py` dosyasındaki `send_zpl_to_printer_via_usb` fonksiyonu ile tam uyumludur:

```python
# main.py'deki kullanım
send_zpl_to_printer_via_usb(zpl_command)

# Yeni modüldeki kullanım (aynı fonksiyon)
from usb_direct_printer import send_zpl_to_printer_via_usb
send_zpl_to_printer_via_usb(zpl_command)
```

## Test Etme

### 1. Basit Test
```bash
python test_usb_printer.py
```

### 2. JSON Verisi ile Test
JSON dosyası oluşturun (örnek: `test_data.json`):
```json
[
    {
        "tarih": "2025-08-08",
        "etiket": "TEST_001", 
        "sicil": "001",
        "total_amount": "150"
    }
]
```

### 3. main.py Tarzı Kullanım
```python
from usb_direct_printer import send_zpl_to_printer_via_usb
import json

# JSON verisini yükle
with open('test_data.json', 'r') as f:
    data = json.load(f)

# Her kayıt için etiket bas
for obj in data:
    zpl_label = generate_zpl_label(...)  # main.py'deki fonksiyon
    send_zpl_to_printer_via_usb(zpl_label)
```

## Hata Giderme

### USB Yazıcı Bulunamıyor
1. Yazıcının USB ile bağlı ve açık olduğundan emin olun
2. Desteklenen bir yazıcı modeli olup olmadığını kontrol edin
3. USB izinlerini kontrol edin (Linux)
4. PyUSB kurulumunu kontrol edin

### PyUSB Kurulum Sorunları
```bash
# macOS
brew install libusb
pip install pyusb

# Linux
sudo apt-get install libusb-1.0-0-dev
pip install pyusb

# Windows
# Libusb-win32 veya WinUSB driver gerekebilir
```

### İzin Hataları (Linux)
```bash
# Kullanıcı gruplarını kontrol et
groups $USER

# dialout grubuna ekle
sudo usermod -a -G dialout $USER

# Yeniden giriş yap veya
newgrp dialout
```

## Değişiklik Özeti

### Kaldırılan Özellikler
- ❌ COM port (serial) iletişimi
- ❌ PySerial bağımlılığı
- ❌ Serial port tarama ve yapılandırması
- ❌ Hibrit bağlantı türleri

### Eklenen Özellikler
- ✅ Doğrudan USB iletişimi
- ✅ Sadeleştirilmiş API
- ✅ main.py uyumluluğu
- ✅ Kapsamlı USB yazıcı desteği
- ✅ Otomatik yazıcı tespiti

Bu yeni yapı ile tüm iletişim doğrudan USB üzerinden gerçekleşir ve COM port bağımlılıkları tamamen ortadan kalkar.
