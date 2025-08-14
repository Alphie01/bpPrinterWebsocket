# Palet Özet Raporu Özelliği

## 🆕 Yeni Özellik: Otomatik A5 Özet Yazdırma

WebSocket Printer Client artık palet etiketleri için otomatik A5 format özet raporları oluşturuyor ve yazdırıyor.

### ✨ Özellikler

- **🏷️ Çift Yazdırma**: ZPL etiket + A5 özet raporu
- **📄 A5 Format**: Türkçe destekli, yazdırmaya hazır HTML
- **🖨️ Otomatik Yazdırma**: Varsayılan yazıcıya otomatik gönderim
- **💾 Dosya Kaydetme**: HTML ve text formatlarında yerel kayıt
- **🔄 Akıllı Yedekleme**: Birden fazla yazdırma yöntemi

### 🔄 İşleyiş

1. **ZPL Etiket Yazdırma**: Termal yazıcıda palet etiketi
2. **✅ Başarı Kontrolü**: ZPL yazdırma başarılı ise
3. **📋 Özet Oluşturma**: A5 format HTML + text raporu
4. **🖨️ Otomatik Yazdırma**: Varsayılan yazıcıya gönderim
5. **📁 Dosya Saklama**: `pallet_summaries/` klasörüne kayıt

### 📋 Özet İçeriği

- **📊 Palet Bilgileri**: ID, durum, ağırlık, tarihler
- **📦 Ürün Detayları**: Kod, ad, miktar, lot numarası
- **⚖️ Ağırlık Özeti**: Brüt, net, dara ağırlıkları
- **🏷️ QR Kod**: Palet takip kodu
- **📝 Notlar**: Operatör ve kalite kontrol notları

### 🚀 Kullanım

```python
# Palet verisi (print_summary=True varsayılan)
pallet_data = {
    'type': 'pallet',
    'palet_id': 'PLT2025001',
    'firma_adi': 'Bil Plastik Ambalaj',
    'print_summary': True,  # Özet yazdırmayı aktifleştirir
    'items': [...]  # Detaylı ürün listesi
}
```

### 📁 Çıktı Dosyaları

```
pallet_summaries/
├── pallet_summary_PLT2025001_20250814_095225.html  # A5 yazdırma
├── pallet_summary_PLT2025001_20250814_095225.txt   # Text yedek
└── ...
```

### 🖨️ Yazdırma Yöntemleri

**macOS:**
- `lpr` komutu (A5 format)
- CUPS `lp` komutu
- PDF dönüşümü + yazdırma
- Safari ile AppleScript
- Manuel Safari açma

**Windows:**
- `print` komutu
- PowerShell yazdırma
- Varsayılan tarayıcı

**Linux:**
- CUPS `lp` komutu
- `lpr` komutu
- PDF dönüşümü
- Varsayılan tarayıcı

### 📝 Test

```bash
# Demo test çalıştırma
python3 demo_pallet_print.py

# Gerçek sistem
python3 run_usb_client.py
```

### ⚙️ Konfigürasyon

- **Özet yazdırma**: `print_summary: true/false`
- **A5 format**: Otomatik CSS ayarları
- **Dil desteği**: Türkçe karakter desteği
- **Yazıcı**: Sistem varsayılan yazıcısı

### 🎯 Kullanım Alanları

- **📦 Sevkiyat Evrakları**: Müşteri teslimat belgeleri
- **✅ Kalite Kontrol**: Ürün onay raporları
- **📊 Depo Yönetimi**: Palet içerik kayıtları
- **📋 Envanter**: Stok takip raporları
- **🚚 Lojistik**: Nakliye evrakları

---

*Bu özellik ZPL etiket yazdırma işleminden sonra otomatik olarak devreye girer ve palet bilgilerinin detaylı A5 raporunu oluşturarak varsayılan yazıcıya gönderir.*
