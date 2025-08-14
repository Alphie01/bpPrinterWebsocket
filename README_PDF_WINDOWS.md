# WebSocket Printer Client - Windows PDF Edition

Bu WebSocket yazıcı client'ı Windows platformu için optimize edilmiş olup, hem termal etiket yazdırma hem de A5 boyutunda PDF özet raporları yazdırma özelliği sunar.

## ✨ Özellikler

### 🏷️ Termal Etiket Yazdırma
- **USB bağlantısı** ile direkt termal yazıcı kontrolü
- **ZPL komut desteği** (Zebra Programming Language)
- **Otomatik yazıcı tespiti** (Zebra, Brother, Epson)
- **Palet, lokasyon ve test etiketleri**

### 📄 PDF Özet Raporları
- **A5 boyutunda profesyonel PDF formatı**
- **Windows PowerShell ile otomatik yazdırma**
- **Varsayılan yazıcı tespiti ve kullanımı**
- **Türkçe dil desteği ve formatlaması**

### 🔄 Dual Printing System
1. **ZPL Etiket** → USB termal yazıcıya gönderilir
2. **PDF Özet** → Windows varsayılan yazıcısına gönderilir

## 🖥️ Platform Desteği

### ✅ Windows (Ana Platform)
- **PowerShell** ile otomatik PDF yazdırma
- **WMI** ile yazıcı tespiti
- **Start-Process -Verb Print** ile direkt yazdırma
- **Fallback**: PDF viewer ile manuel yazdırma

### 🍎 macOS (Test/Development)
- **lpr** komutu ile PDF yazdırma
- **Fallback**: PDF viewer ile manuel yazdırma

### 🐧 Linux (Destek)
- **lp** komutu ile PDF yazdırma
- **xdg-open** fallback

## 📦 Kurulum

### Gereksinimler
```bash
pip install -r requirements.txt
```

### Ana Bağımlılıklar
- `python-socketio` - WebSocket iletişimi
- `pyusb` - USB yazıcı bağlantısı
- `reportlab` - PDF oluşturma
- `python-dotenv` - Konfigürasyon

## 🚀 Kullanım

### 1. Client Başlatma
```bash
python run_usb_client.py
```

### 2. Örnek Çıktı
```
USB-Only WebSocket Printer Client
Version: 2.1.0 (Enhanced with PDF Summary Generation)

🆕 NEW FEATURE: Automatic PDF Summary Generation
   📋 A5 format PDF summaries for pallet labels
   🖨️  Automatic printing to default Windows printer
   💾 Professional PDF formatting
   🇹🇷 Full Turkish language support

============================================================
USB Printer Detection
============================================================
Found 1 USB printer(s):
1. Zebra ZD410/ZD420
   Type: ZEBRA
   USB ID: VID=0x0A5F, PID=0x0164

✅ USB printer connected successfully
✅ WebSocket connection established
🎯 Waiting for print jobs...
```

## 📋 Print Job Akışı

### Palet Etiketi İşlemi
1. **WebSocket'ten print job alınır**
2. **ZPL etiket** oluşturulur ve USB yazıcıya gönderilir
3. **PDF özet** oluşturulur ve Windows yazıcısına gönderilir

### Örnek Log Çıktısı
```
2025-08-14 11:11:37 - INFO - Processing print job with type: pallet
2025-08-14 11:11:37 - INFO - Generating pallet label using provided data
2025-08-14 11:11:37 - INFO - Generating pallet PDF summary for default printer
2025-08-14 11:11:37 - INFO - ✅ PDF summary sent to default printer successfully (PowerShell)
2025-08-14 11:11:37 - INFO - Sending ZPL command to printer (length: 1324 chars)
2025-08-14 11:11:37 - INFO - Print job completed successfully
```

## 🔧 Konfigürasyon

### Environment Variables (.env)
```env
WEBSOCKET_SERVER_URL=http://192.168.1.139:25625
PRINTER_TYPE=zebra
PRINTER_LOCATION=Warehouse A
AUTO_DETECT_PRINTER=true
```

### Windows PowerShell Execution Policy
Eğer PowerShell execution policy hatası alırsanız:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📊 PDF Özet Formatı

### A5 Boyut Özellikleri
- **Sayfa Boyutu**: 148mm x 210mm (A5)
- **Margin**: 10mm
- **Font**: Helvetica (Windows uyumlu)
- **Encoding**: UTF-8 (Türkçe karakter desteği)

### İçerik Yapısı
1. **Şirket Başlığı** (Bil Plastik Ambalaj)
2. **Palet Özet Raporu** başlığı
3. **Temel Bilgiler Tablosu**
   - Palet ID, Durum
   - Depo, Tarih
   - Teslim Alacak Firma
4. **Ağırlık Bilgileri**
   - Brüt Ağırlık
   - Net Ağırlık
5. **İçerik Detayı** (varsa)
   - Ürün listesi
   - Miktar/Ağırlık
   - Lot numaraları
6. **Footer Bilgileri**
   - Rapor tarihi
   - Otomatik oluşturulma notu

## 🛠️ Test Araçları

### PDF Generator Testi
```bash
python test_pdf_generator.py
```

### Windows Printing Testi
```bash
python test_windows_printing.py
```

### Dual Printing Testi
```bash
python test_dual_printing.py
```

## 🔍 Sorun Giderme

### USB Yazıcı Bulunamıyor
```bash
python setup_usb_zebra.py
```

### PDF Yazdırma Sorunları
1. **Varsayılan yazıcı kontrolü**:
   ```powershell
   Get-WmiObject -Query "SELECT * FROM Win32_Printer WHERE Default=$true"
   ```

2. **Execution Policy kontrolü**:
   ```powershell
   Get-ExecutionPolicy
   ```

3. **PDF Viewer fallback**: PDF dosyası otomatik açılır

### Log Seviyeleri
- **INFO**: Normal işlem logları
- **WARNING**: Yazdırma fallback durumları
- **ERROR**: Kritik hatalar

## 📝 Version History

### v2.1.0 - PDF Windows Edition
- ✅ PDF özet raporu oluşturma
- ✅ Windows PowerShell ile otomatik yazdırma
- ✅ A5 boyut optimizasyonu
- ✅ Türkçe dil desteği
- ✅ Multi-platform fallback desteği

### v2.0.0 - USB-Only
- ✅ USB direkt bağlantı
- ✅ COM port bağımlılığı kaldırma
- ✅ Otomatik yazıcı tespiti

## 📞 Destek

Bu sistem Windows platformunda en iyi performansı gösterir. Sorun yaşamanız durumunda:

1. **Log dosyalarını** kontrol edin
2. **USB yazıcı bağlantısını** test edin  
3. **PowerShell execution policy** ayarlarını kontrol edin
4. **Varsayılan yazıcı** ayarlarını doğrulayın

---

**Not**: Bu sistem Windows ortamında çalışmak üzere optimize edilmiştir. macOS ve Linux desteği test amaçlıdır.
