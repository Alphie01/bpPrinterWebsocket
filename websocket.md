# 🔌 Postman WebSocket Test Dokümantasyonu

## ⚠️ Önemli Not
Bu sistem Socket.IO kullandığı için, Postman'da direkt WebSocket bağlantısı kurmak karmaşık olabilir. Socket.IO kendi protokolünü kullanır.

## 🌐 Alternatif Test Yöntemleri

### 1. Web Test Sayfası (Önerilen)
En kolay test yöntemi web sayfasını kullanmaktır:
```
http://localhost:25625/label-test.html
```

### 2. Socket.IO Client Library ile Test
Node.js veya Python ile Socket.IO client kullanarak test edebilirsiniz.

## 📤 Socket.IO Event'leri

Socket.IO kullandığı için mesajlar `socket.emit(event, data)` formatında gönderilir:

### 1. Ping Testi
```javascript
socket.emit('ping');
```

### 2. Yazıcı Kaydı
```javascript
socket.emit('register_printer', {
  printerId: 'USB_PRINTER_001',          // Benzersiz yazıcı ID'si
  printerName: 'Zebra ZD420',            // Yazıcı adı
  printerType: 'zebra',                  // Yazıcı tipi (zebra, thermal, label)
  location: 'Warehouse A',               // Lokasyon
  connectionType: 'usb',                 // Bağlantı tipi
  capabilities: ['zpl', 'thermal'],      // Desteklenen formatlar
  status: 'online',                      // Durum
  timestamp: '2025-08-08 15:30:00'       // Zaman damgası
});
```

**Kayıt Yanıtları:**
```javascript
// Başarılı kayıt
socket.on('registration_success', (data) => {
  console.log('✅ Yazıcı kaydı başarılı:', data);
});

// Başarısız kayıt
socket.on('registration_failed', (data) => {
  console.log('❌ Yazıcı kaydı başarısız:', data);
});

// Kayıt hatası
socket.on('registration_error', (data) => {
  console.log('💥 Yazıcı kayıt hatası:', data);
});
```

### 3. Etiket Basma İsteği
```javascript
socket.emit('print_label', {
  targetPrinterId: 'HEDEF_YAZICI_ID',
  labelData: {
    type: 'location',
    barcode: 'LOC000001',
    locationName: 'A-01-01',
    warehouseCode: 'WH001',
    template: 'location_label'
  }
});
```

## 🧪 Socket.IO Client Test Kodu (Node.js)

### Kurulum:
```bash
npm install socket.io-client
```

### Test Scripti:
```javascript
const io = require('socket.io-client');

// Bağlantı kur
const socket = io('http://localhost:25625');

socket.on('connect', () => {
  console.log('✅ Bağlantı başarılı!', socket.id);
  
  // Ping testi
  socket.emit('ping');
});

socket.on('pong', () => {
  console.log('🏓 Pong alındı!');
  
  // Yazıcı kaydı
  socket.emit('register_printer', {
    printerId: 'TEST_PRINTER_001',
    printerName: 'Test Yazıcısı',
    printerType: 'zebra',
    location: 'Test Masası',
    connectionType: 'usb',
    capabilities: ['zpl', 'thermal'],
    status: 'online'
  });
});

socket.on('registration_success', (data) => {
  console.log('📋 Yazıcı kaydı başarılı:', data);
  
  // Test etiketi gönder
  setTimeout(() => {
    socket.emit('print_label', {
      targetPrinterId: 'BAŞKA_YAZICI_ID', // Başka bir yazıcının ID'si
      labelData: {
        type: 'test',
        message: 'Test Etiketi',
        timestamp: new Date().toISOString()
      }
    });
  }, 2000);
});

socket.on('registration_failed', (data) => {
  console.log('❌ Yazıcı kaydı başarısız:', data);
  // Yeniden deneme mantığı eklenebilir
});

socket.on('registration_error', (data) => {
  console.log('💥 Yazıcı kayıt hatası:', data);
});

socket.on('print_job', (data) => {
  console.log('🖨️ Yazdırma işi alındı:', data);
  
  // İşlem simülasyonu (2 saniye bekle)
  setTimeout(() => {
    socket.emit(`print_result_${data.jobId}`, {
      success: true,
      message: 'Etiket başarıyla yazdırıldı'
    });
    console.log('✅ Print job tamamlandı');
  }, 2000);
});

socket.on('disconnect', () => {
  console.log('❌ Bağlantı kesildi');
});

socket.on('connect_error', (error) => {
  console.error('🚫 Bağlantı hatası:', error.message);
});
```

## 🐍 Python Socket.IO Client Test

### Kurulum:
```bash
pip install python-socketio
```

### Test Scripti:
```python
import socketio
import time
import threading

# Socket.IO client oluştur
sio = socketio.Client()

@sio.event
def connect():
    print('✅ Bağlantı başarılı!')
    sio.emit('ping')

@sio.event
def pong():
    print('🏓 Pong alındı!')
    # Yazıcı kaydı
    sio.emit('register_printer', {
        'printerId': 'PYTHON_PRINTER_001',
        'printerName': 'Python Test Yazıcısı',
        'printerType': 'zebra',
        'location': 'Python Test',
        'connectionType': 'usb',
        'capabilities': ['zpl', 'thermal'],
        'status': 'online'
    })

@sio.event
def registration_success(data):
    print('📋 Yazıcı kaydı başarılı:', data)

@sio.event  
def registration_failed(data):
    print('❌ Yazıcı kaydı başarısız:', data)

@sio.event
def registration_error(data):
    print('💥 Yazıcı kayıt hatası:', data)

@sio.event
def print_job(data):
    print('🖨️ Yazdırma işi alındı:', data)
    # İşlem simülasyonu
    time.sleep(2)
    sio.emit(f"print_result_{data['jobId']}", {
        'success': True,
        'message': 'Python ile yazdırıldı'
    })
    print('✅ Print job tamamlandı')

@sio.event
def disconnect():
    print('❌ Bağlantı kesildi')

# Bağlan
try:
    sio.connect('http://localhost:25625')
    sio.wait()
except Exception as e:
    print(f'🚫 Hata: {e}')
```

## 🔧 REST API ile Test (Postman'da Kolayca Test Edilebilir)

Socket.IO yerine REST API'yi test etmek daha kolay olabilir:

### 1. Bağlı Yazıcıları Listele
```http
GET http://localhost:25625/labels/printers
```

### 2. Location Etiketi Bas
```http
POST http://localhost:25625/labels/location
Content-Type: application/json

{
  "locationId": 1,
  "printerId": "YAZICI_ID"
}
```

### 3. Test Etiketi Bas
```http
POST http://localhost:25625/labels/test-printer
Content-Type: application/json

{
  "printerId": "YAZICI_ID"
}
```

## 🌐 Web Test Sayfası Kullanımı

1. **Sayfayı Açın:** http://localhost:25625/label-test.html
2. **Otomatik Bağlantı:** Sayfa yüklendiğinde otomatik olarak WebSocket bağlantısı kurulur
3. **Yazıcı Kaydı:** Formdan yazıcı bilgilerini girerek kayıt yapın
4. **Test Etiketleri:** Farklı etiket türlerini test edin
5. **Log Takibi:** Tüm mesajlar log alanında görüntülenir

## � Neden Socket.IO?

Socket.IO, düz WebSocket'lere göre şu avantajları sağlar:
- **Automatic reconnection** (otomatik yeniden bağlanma)
- **Fallback to polling** (WebSocket desteklenmezse HTTP polling'e geçiş)
- **Room and namespace support** (oda ve namespace desteği)
- **Event-based messaging** (olay tabanlı mesajlaşma)

## 🔍 Troubleshooting

### Problem: Bağlantı kurulamıyor
**Çözüm:** 
- Server'ın çalıştığını kontrol edin
- Web test sayfasını kullanın
- Socket.IO client library kullanın

### Problem: Yazıcı kaydı başarısız
**Çözüm:**
- printerId'nin benzersiz olduğundan emin olun
- Gerekli alanların dolu olduğunu kontrol edin (printerId, printerName, printerType, location)
- Yazıcının USB bağlantısının aktif olduğunu kontrol edin
- registration_success, registration_failed event'lerini dinleyin
- Kayıt yanıtını 5-30 saniye içinde beklemeyin
- Kayıt başarısız olursa otomatik yeniden deneme yapılır

### Problem: Print job gönderilemiyor
**Çözüm:**
- Hedef yazıcının kayıtlı ve online olduğundan emin olun
- Yazıcı ID'sinin doğru olduğunu kontrol edin
- registration_success event'ini aldıktan sonra print job gönderin
- is_registered durumunu kontrol edin

Bu rehber ile Socket.IO tabanlı sistemizi başarıyla test edebilirsiniz! 🚀
