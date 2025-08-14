#!/usr/bin/env python3
"""
Test Windows PDF Printing Simulation
====================================

Bu script Windows PDF yazdırma komutlarını test eder.
"""

import subprocess
import platform
import os

def test_windows_pdf_printing():
    """Windows PDF yazdırma simülasyonu"""
    print("🖨️  Windows PDF Yazdırma Testi")
    print("=" * 60)
    
    # Test PDF dosyası
    pdf_files = [f for f in os.listdir('.') if f.startswith('pallet_summary_') and f.endswith('.pdf')]
    
    if not pdf_files:
        print("❌ Test için PDF dosyası bulunamadı")
        return
    
    pdf_file = pdf_files[0]  # En son oluşturulan dosyayı al
    pdf_path = os.path.abspath(pdf_file)
    
    print(f"📄 Test PDF: {pdf_file}")
    print(f"📁 Tam yol: {pdf_path}")
    print()
    
    system = platform.system()
    print(f"🖥️  Platform: {system}")
    
    if system == "Windows":
        print("🎯 Windows tespit edildi - Gerçek komutlar çalıştırılacak")
        
        # Windows PowerShell komutu
        powershell_cmd = f'''
        Add-Type -AssemblyName System.Drawing
        Add-Type -AssemblyName System.Printing
        
        $printerName = (Get-WmiObject -Query "SELECT * FROM Win32_Printer WHERE Default=$true").Name
        if ($printerName) {{
            Write-Host "Default printer: $printerName"
            Start-Process -FilePath "{pdf_path}" -Verb Print -WindowStyle Hidden
            Write-Host "PDF sent to printer: $printerName"
        }} else {{
            Write-Host "No default printer found"
        }}
        '''
        
        print("🔧 PowerShell komutu:")
        print(powershell_cmd)
        print()
        
        try:
            cmd = ["powershell", "-Command", powershell_cmd]
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            print(f"Return code: {result.returncode}")
            if result.stdout:
                print(f"STDOUT: {result.stdout}")
            if result.stderr:
                print(f"STDERR: {result.stderr}")
                
            if result.returncode == 0:
                print("✅ PowerShell komutu başarılı")
            else:
                print("❌ PowerShell komutu başarısız - Fallback:")
                print("   📖 PDF default viewer ile açılacak")
                
        except Exception as e:
            print(f"❌ PowerShell hatası: {e}")
    
    else:
        print(f"ℹ️  {system} tespit edildi - Windows simülasyonu")
        print()
        print("🎯 Windows'ta çalışacak komutlar:")
        print("1️⃣ PowerShell ile varsayılan yazıcı bulma")
        print("2️⃣ PDF dosyasını Print verb ile gönderme")
        print("3️⃣ Başarısız olursa default PDF viewer açma")
        print()
        print("📋 PowerShell komutu özeti:")
        print("   • Get-WmiObject ile default printer bulma")
        print("   • Start-Process -Verb Print ile yazdırma")
        print("   • WindowStyle Hidden ile arka planda çalıştırma")
        
        # macOS'ta test amaçlı PDF açma
        print()
        print("🔧 Test amaçlı PDF açma (macOS):")
        try:
            cmd = ["open", pdf_path]
            subprocess.run(cmd)
            print("✅ PDF açıldı")
        except Exception as e:
            print(f"❌ PDF açma hatası: {e}")

if __name__ == "__main__":
    test_windows_pdf_printing()
