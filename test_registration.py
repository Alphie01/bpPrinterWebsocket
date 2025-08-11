#!/usr/bin/env python3
"""
WebSocket Registration Test Script
=================================

Bu script, yazıcı kayıt işlemini test etmek için kullanılır.
WebSocket server'a bağlanır, yazıcı kaydı yapar ve sonucu kontrol eder.
"""

import asyncio
import logging
import os
import sys
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not available. Using system environment variables.")

import socketio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RegistrationTestClient:
    """Test client for printer registration"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.sio = socketio.AsyncClient()
        self.is_connected = False
        self.is_registered = False
        self.registration_result = None
        
        self._setup_events()
    
    def _setup_events(self):
        """Setup event handlers"""
        
        @self.sio.event
        async def connect():
            print("✅ Connected to WebSocket server")
            self.is_connected = True
            await self._test_registration()
        
        @self.sio.event
        async def disconnect():
            print("❌ Disconnected from WebSocket server")
            self.is_connected = False
        
        @self.sio.event
        async def registration_success(data):
            print(f"🎉 Registration SUCCESS: {data}")
            self.is_registered = True
            self.registration_result = "success"
        
        @self.sio.event
        async def registration_failed(data):
            print(f"💔 Registration FAILED: {data}")
            self.is_registered = False
            self.registration_result = "failed"
        
        @self.sio.event
        async def registration_error(data):
            print(f"💥 Registration ERROR: {data}")
            self.is_registered = False
            self.registration_result = "error"
        
        @self.sio.event
        async def pong():
            print("🏓 Pong received from server")
    
    async def _test_registration(self):
        """Test printer registration"""
        try:
            # Send ping first
            print("📡 Sending ping...")
            await self.sio.emit('ping')
            
            # Wait a moment
            await asyncio.sleep(1)
            
            # Test registration data
            registration_data = {
                'printerId': 'TEST_REGISTRATION_001',
                'printerName': 'Test Registration Printer',
                'printerType': 'zebra',
                'location': 'Test Location',
                'connectionType': 'usb',
                'capabilities': ['zpl', 'thermal', 'label'],
                'status': 'online',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            print("📋 Sending registration request...")
            print(f"   Printer ID: {registration_data['printerId']}")
            print(f"   Printer Name: {registration_data['printerName']}")
            print(f"   Printer Type: {registration_data['printerType']}")
            
            await self.sio.emit('register_printer', registration_data)
            
        except Exception as e:
            print(f"❌ Error in registration test: {e}")
    
    async def run_test(self, timeout=30):
        """Run the registration test"""
        try:
            print(f"🔗 Connecting to: {self.server_url}")
            await self.sio.connect(self.server_url)
            
            # Wait for registration result
            start_time = time.time()
            while not self.registration_result and (time.time() - start_time) < timeout:
                await asyncio.sleep(0.5)
            
            if self.registration_result:
                if self.registration_result == "success":
                    print("\\n🎉 REGISTRATION TEST PASSED! ✅")
                    print("   Yazıcı başarıyla kaydedildi.")
                    return True
                else:
                    print(f"\\n💔 REGISTRATION TEST FAILED! ❌")
                    print(f"   Result: {self.registration_result}")
                    return False
            else:
                print(f"\\n⏰ REGISTRATION TEST TIMEOUT! ⚠️")
                print(f"   No response received within {timeout} seconds")
                return False
                
        except Exception as e:
            print(f"\\n💥 REGISTRATION TEST ERROR! ❌")
            print(f"   Error: {e}")
            return False
        finally:
            if self.sio.connected:
                await self.sio.disconnect()


async def main():
    """Main test function"""
    print("WebSocket Printer Registration Test")
    print("=" * 50)
    
    # Get server URL from environment
    server_url = os.getenv('SERVER_URL', 'http://localhost:25625')
    print(f"Server URL: {server_url}")
    print()
    
    # Create test client
    test_client = RegistrationTestClient(server_url)
    
    # Run test
    success = await test_client.run_test(timeout=30)
    
    print("\\n" + "=" * 50)
    if success:
        print("TEST RESULT: ✅ PASSED")
        print("\\nYazıcı kayıt sistemi çalışıyor!")
        print("Şimdi normal client'ı çalıştırabilirsiniz:")
        print("  python run_usb_client.py")
    else:
        print("TEST RESULT: ❌ FAILED")
        print("\\nYazıcı kayıt sisteminde sorun var!")
        print("Kontrol edilecekler:")
        print("  1. WebSocket server çalışıyor mu?")
        print("  2. Server registration event'lerini destekliyor mu?")
        print("  3. Doğru SERVER_URL kullanılıyor mu?")
    
    return success


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\\n\\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\\n\\nFatal error: {e}")
        sys.exit(1)
