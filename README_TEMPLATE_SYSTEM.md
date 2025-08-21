# Dual Template Printer System

## Genel Bakış

Bu sistem artık 2 farklı basım tipini destekliyor:

1. **`pallet_label`** - ZPL termal etiket basımı
2. **`pallet_content_list_a5`** - A5 boyutunda stok özeti basımı

## Backend Entegrasyonu

### Yeni Emit Formatı

```javascript
// ZPL Termal Etiket için
socket.emit('print_job', {
  printerId: 'PRINTER_001',
  template: 'pallet_label',  // ZPL termal basım
  data: {
    pallet_id: 'PLT-2025-001',
    location: 'A1-01-01',
    barcode: 'PLT2025001',
    timestamp: '2025-08-21T10:18:12.181406'
  },
  jobId: 'job_1755760692_pallet',
  timestamp: '2025-08-21T10:18:12.591601',
  requestedBy: 'user_id'
})

// A5 Stok Özeti için
socket.emit('print_job', {
  printerId: 'PRINTER_001', 
  template: 'pallet_content_list_a5',  // A5 özet basım
  data: {
    pallet_id: 'PLT-2025-001',
    location: 'A1-01-01',
    materials: [
      {
        material_code: 'MAT001',
        description: 'Test Malzeme 1 - Türkçe Karakter',
        quantity: 100,
        unit: 'adet'
      },
      {
        material_code: 'MAT002',
        description: 'Test Malzeme 2 - Özel Karakterler', 
        quantity: 50,
        unit: 'kg'
      }
    ],
    timestamp: '2025-08-21T10:18:12.181412'
  },
  jobId: 'job_1755760692_summary',
  timestamp: '2025-08-21T10:18:12.591637',
  requestedBy: 'user_id'
})
```

## Template Tipleri

### 1. `pallet_label` - ZPL Termal Etiket

**Kullanım:** Zebra ve uyumlu termal yazıcılar için etiket basımı

**Veri Formatı:**
```javascript
{
  pallet_id: string,      // Palet ID
  location: string,       // Lokasyon kodu  
  barcode: string,        // Barkod (opsiyonel)
  timestamp: string       // ISO timestamp
}
```

**Çıktı:** ZPL komutları ile termal yazıcıya gönderilir

### 2. `pallet_content_list_a5` - A5 Stok Özeti

**Kullanım:** Varsayılan sistem yazıcısına A5 boyutunda stok listesi

**Veri Formatı:**
```javascript
{
  pallet_id: string,      // Palet ID
  location: string,       // Lokasyon kodu
  materials: [            // Malzeme listesi
    {
      material_code: string,   // Malzeme kodu
      description: string,     // Malzeme açıklaması
      quantity: number,        // Miktar
      unit: string            // Birim (adet, kg, lt vb.)
    }
  ],
  timestamp: string       // ISO timestamp
}
```

**Çıktı:** Formatlanmış metin halinde varsayılan yazıcıya gönderilir

## Client Konfigürasyonu

### Printer Config

```python
from printer_client import PrinterConfig, PrinterType, PrinterConnectionType

# Zebra/Termal yazıcı için
config = PrinterConfig(
    printer_id="PRINTER_001",
    printer_name="Zebra Thermal Printer",
    printer_type=PrinterType.ZEBRA,
    location="Warehouse A",
    connection_type=PrinterConnectionType.USB,  # USB veya SERIAL
    serial_port="/dev/ttyUSB0",  # Serial bağlantı için
    baud_rate=9600
)
```

### Client Başlatma

```python
from printer_client import WebSocketPrinterClient

# Client oluştur ve başlat
client = WebSocketPrinterClient(config, "ws://192.168.1.139:25625")
await client.start()
```

## Platform Desteği

### A5 Basım Desteği

- **Windows:** `notepad /p` komutu ile
- **macOS:** `lpr -P default` komutu ile  
- **Linux:** `lp -d default` komutu ile

### Termal Basım Desteği

- **USB:** pyusb ile doğrudan USB iletişimi
- **Serial:** pyserial ile seri port iletişimi
- **Auto:** Önce USB, sonra Serial deneme

## Test Etme

```bash
# Template sistemini test et
python3 test_template_system.py

# Client'ı başlat
python3 printer_client.py
```

## Önemli Notlar

1. **Template Alanı Zorunlu:** Backend'den gelen her print_job'da `template` alanı bulunmalı
2. **Platform Bağımlılığı:** A5 basım platforma bağımlı komutlar kullanır
3. **Hata Yönetimi:** Bilinmeyen template tipleri için hata döndürülür
4. **Türkçe Karakter:** A5 özetlerde UTF-8 karakter desteği mevcuttur

## Hata Kodları

- `success: true` - Basım başarılı
- `success: false, error: "Unknown template: xxx"` - Bilinmeyen template
- `success: false, error: "Printer not connected"` - Yazıcı bağlantı hatası
- `success: false, error: "Error printing to default printer"` - Varsayılan yazıcı hatası
