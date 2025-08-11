#!/bin/bash
# filepath: fix_usb_permissions.sh

echo "🔧 Linux USB Yazıcı İzinlerini Düzeltme"
echo "====================================="

# Kullanıcıyı gruplara ekle
echo "👥 Kullanıcı gruplarına ekleniyor..."
sudo usermod -a -G dialout $USER
sudo usermod -a -G plugdev $USER
sudo usermod -a -G tty $USER

# udev kuralları oluştur
echo "📋 udev kuralları oluşturuluyor..."
sudo tee /etc/udev/rules.d/99-zebra-printer.rules << 'EOF'
# Zebra USB Printers - Full access
SUBSYSTEM=="usb", ATTR{idVendor}=="0a5f", MODE="0666", GROUP="plugdev"
KERNEL=="hidraw*", ATTRS{idVendor}=="0a5f", MODE="0666", GROUP="plugdev"
EOF

# udev kurallarını yenile
echo "🔄 udev kuralları yenileniyor..."
sudo udevadm control --reload-rules
sudo udevadm trigger

# Gerekli paketleri kontrol et
echo "📦 Gerekli paketler kontrol ediliyor..."
sudo apt update
sudo apt install -y libusb-1.0-0-dev libudev-dev usbutils

echo "✅ İzin düzeltme tamamlandı!"
echo "🔄 Lütfen USB cihazını çıkarıp tekrar takın"
echo "🔄 Ardından oturumu yeniden başlatın: newgrp plugdev"