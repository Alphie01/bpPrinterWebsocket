#!/usr/bin/env python3
# filepath: fix_usb_busy.py

import subprocess
import usb.core
import usb.util
import os
import sys
import time
from typing import List, Dict, Any

def find_usb_processes() -> List[Dict[str, Any]]:
    """Find processes using USB devices"""
    print("🔍 USB cihazını kullanan process'leri bulma...")
    
    # Zebra yazıcıları bul
    zebra_devices = list(usb.core.find(find_all=True, idVendor=0x0a5f))
    
    if not zebra_devices:
        print("❌ Zebra USB cihazı bulunamadı")
        return []
    
    processes = []
    
    for device in zebra_devices:
        print(f"\n📱 Cihaz: Bus {device.bus:03d} Device {device.address:03d}")
        print(f"   Vendor ID: 0x{device.idVendor:04x}")
        print(f"   Product ID: 0x{device.idProduct:04x}")
        
        # lsof ile USB cihazını kullanan process'leri bul
        usb_path = f"/dev/bus/usb/{device.bus:03d}/{device.address:03d}"
        
        try:
            result = subprocess.run(
                ['lsof', usb_path], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                print(f"   ⚠️ Cihaz kullanımda:")
                lines = result.stdout.strip().split('\n')[1:]  # Header'ı atla
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 2:
                        process_name = parts[0]
                        pid = parts[1]
                        print(f"   📍 Process: {process_name} (PID: {pid})")
                        processes.append({
                            'name': process_name,
                            'pid': pid,
                            'device_path': usb_path,
                            'bus': device.bus,
                            'address': device.address
                        })
            else:
                print("   ✅ Cihaz boş")
                
        except subprocess.TimeoutExpired:
            print("   ⏰ lsof timeout")
        except FileNotFoundError:
            print("   ❌ lsof bulunamadı (sudo apt install lsof)")
        except Exception as e:
            print(f"   ❌ Hata: {e}")
    
    return processes

def kill_usb_processes(processes: List[Dict[str, Any]]) -> bool:
    """Kill processes using USB devices"""
    if not processes:
        print("✅ Sonlandırılacak process yok")
        return True
    
    print(f"\n🔥 {len(processes)} process sonlandırılacak...")
    
    success = True
    for proc in processes:
        try:
            pid = int(proc['pid'])
            process_name = proc['name']
            
            print(f"🔪 Sonlandırılıyor: {process_name} (PID: {pid})")
            
            # Önce SIGTERM gönder
            os.kill(pid, 15)  # SIGTERM
            time.sleep(1)
            
            # Process'in hala çalışıp çalışmadığını kontrol et
            try:
                os.kill(pid, 0)  # Process var mı kontrol et
                print(f"   ⚠️ Process hala çalışıyor, SIGKILL gönderiliyor...")
                os.kill(pid, 9)  # SIGKILL
                time.sleep(0.5)
            except ProcessLookupError:
                print(f"   ✅ Process sonlandırıldı")
                
        except ProcessLookupError:
            print(f"   ✅ Process zaten yok: {proc['name']}")
        except PermissionError:
            print(f"   ❌ İzin reddedildi: {proc['name']} (sudo gerekli)")
            success = False
        except Exception as e:
            print(f"   ❌ Hata: {proc['name']} - {e}")
            success = False
    
    return success

def reset_usb_device(vendor_id: int = 0x0a5f) -> bool:
    """Reset USB device to clear busy state"""
    print(f"\n🔄 USB cihaz reset ediliyor (Vendor ID: 0x{vendor_id:04x})...")
    
    try:
        devices = list(usb.core.find(find_all=True, idVendor=vendor_id))
        
        if not devices:
            print("❌ USB cihaz bulunamadı")
            return False
        
        for device in devices:
            try:
                print(f"🔄 Reset: Bus {device.bus:03d} Device {device.address:03d}")
                device.reset()
                print("   ✅ Reset başarılı")
                time.sleep(2)  # Reset sonrası bekleme
                
            except usb.core.USBError as e:
                if "busy" in str(e).lower() or "resource busy" in str(e).lower():
                    print(f"   ⚠️ Cihaz hala meşgul: {e}")
                    return False
                else:
                    print(f"   ⚠️ Reset hatası: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Reset hatası: {e}")
        return False

def unbind_kernel_driver() -> bool:
    """Unbind kernel driver from USB device"""
    print("\n🔓 Kernel driver unbind işlemi...")
    
    try:
        devices = list(usb.core.find(find_all=True, idVendor=0x0a5f))
        
        for device in devices:
            try:
                # Tüm interface'lerde kernel driver'ı kontrol et
                config = device.get_active_configuration()
                
                for interface in config:
                    interface_num = interface.bInterfaceNumber
                    
                    if device.is_kernel_driver_active(interface_num):
                        print(f"🔓 Kernel driver detach: Interface {interface_num}")
                        device.detach_kernel_driver(interface_num)
                        time.sleep(0.5)
                    else:
                        print(f"✅ Interface {interface_num} zaten detached")
                
            except usb.core.USBError as e:
                if "busy" in str(e).lower():
                    print(f"   ⚠️ Interface busy: {e}")
                else:
                    print(f"   ⚠️ Detach hatası: {e}")
            except Exception as e:
                print(f"   ❌ Unexpected error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Kernel driver unbind hatası: {e}")
        return False

def fix_usb_busy() -> bool:
    """Complete USB busy fix procedure"""
    print("🔧 USB Resource Busy (Errno 16) Düzeltme")
    print("=" * 50)
    
    # 1. USB process'leri bul
    processes = find_usb_processes()
    
    # 2. Process'leri sonlandır
    if processes:
        print(f"\n⚠️ {len(processes)} process USB cihazını kullanıyor!")
        choice = input("Process'leri sonlandırmak istiyor musunuz? (y/N): ").lower()
        
        if choice == 'y':
            if not kill_usb_processes(processes):
                print("❌ Bazı process'ler sonlandırılamadı")
                return False
        else:
            print("❌ Process'ler sonlandırılmadı, sorun devam edebilir")
            return False
    
    # 3. Kernel driver'ı unbind et
    time.sleep(1)
    unbind_kernel_driver()
    
    # 4. USB cihazı reset et
    time.sleep(1)
    if not reset_usb_device():
        print("❌ USB reset başarısız")
        return False
    
    # 5. Test et
    time.sleep(2)
    print("\n🧪 USB cihaz erişim testi...")
    
    try:
        devices = list(usb.core.find(find_all=True, idVendor=0x0a5f))
        
        if not devices:
            print("❌ Test: USB cihaz bulunamadı")
            return False
        
        for device in devices:
            try:
                device.set_configuration()
                print("✅ Test: USB cihaz erişimi başarılı")
                return True
                
            except usb.core.USBError as e:
                if "busy" in str(e).lower():
                    print(f"❌ Test: Cihaz hala busy - {e}")
                    return False
                else:
                    print(f"⚠️ Test: USB hatası - {e}")
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🐧 Linux USB Resource Busy Fixer")
    print("=" * 40)
    
    # Root kontrolü
    if os.geteuid() != 0:
        print("⚠️ Bu script root yetkileriyle çalışmalı")
        print("Çalıştırın: sudo python3 fix_usb_busy.py")
        
        # Root olmadan da denenebilir
        choice = input("\nRoot olmadan devam etmek istiyor musunuz? (y/N): ").lower()
        if choice != 'y':
            sys.exit(1)
    
    success = fix_usb_busy()
    
    if success:
        print("\n🎉 USB busy sorunu çözüldü!")
        print("✅ Artık yazıcı kullanıma hazır")
    else:
        print("\n❌ USB busy sorunu çözülemedi")
        print("💡 Çözüm önerileri:")
        print("   1. Sistemi yeniden başlatın")
        print("   2. USB cihazını fiziksel olarak çıkarıp takın") 
        print("   3. Farklı USB portunu deneyin")
        print("   4. sudo modprobe -r usblp && sudo modprobe usblp")