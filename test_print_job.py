#!/usr/bin/env python3
"""
Simple test script to send print jobs to WebSocket printer client
"""

import socketio
import asyncio
import time
import json

# Connect to the server
sio = socketio.AsyncClient()

@sio.event
async def connect():
    print("✅ Connected to WebSocket server")

@sio.event
async def disconnect():
    print("❌ Disconnected from WebSocket server")

@sio.event
async def print_job_result(data):
    print(f"📄 Print job result: {data}")

async def test_print_jobs():
    """Test various print job scenarios"""
    
    # Wait a bit to ensure connection is established
    await asyncio.sleep(2)
    
    print("\n🧪 Testing print jobs...")
    
    # Test 1: Simple test label with no data
    print("\n1️⃣ Test 1: Simple test label (no data)")
    test_job_1 = {
        'job_id': 'test_001',
        'label_data': {
            'type': 'test'
        },
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'requested_by': 'test_script'
    }
    await sio.emit('print_job', test_job_1)
    await asyncio.sleep(3)
    
    # Test 2: Test label with actual data
    print("\n2️⃣ Test 2: Test label with actual data")
    test_job_2 = {
        'job_id': 'test_002',
        'label_data': {
            'type': 'test',
            'firma': 'ACME Corporation',
            'product_code': 'AC001',
            'product_name': 'Test Product',
            'production_date': '2025-08-11',
            'lot_code': 'LOT-2025-001',
            'personel_code': 'OP001',
            'total_amount': '500',
            'hat_kodu': 'A',
            'bom': '123',
            'firma_kodu': 'ACME'
        },
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'requested_by': 'test_script'
    }
    await sio.emit('print_job', test_job_2)
    await asyncio.sleep(3)
    
    # Test 3: Custom label
    print("\n3️⃣ Test 3: Custom label")
    test_job_3 = {
        'job_id': 'test_003',
        'label_data': {
            'type': 'custom',
            'firma': 'Custom Company Ltd',
            'product_code': 'CUST001',
            'product_name': 'Custom Product Name',
            'production_date': '2025-08-11',
            'lot_code': 'CUSTOM-LOT-001',
            'personel_code': 'CP001',
            'total_amount': '1000',
            'hat_kodu': 'B',
            'bom': '456',
            'adet_bilgisi': '500'
        },
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'requested_by': 'test_script'
    }
    await sio.emit('print_job', test_job_3)
    await asyncio.sleep(3)
    
    # Test 4: Auto-detect type (no type specified)
    print("\n4️⃣ Test 4: Auto-detect label type")
    test_job_4 = {
        'job_id': 'test_004',
        'label_data': {
            'firma': 'Auto Detect Company',
            'product_code': 'AUTO001',
            'product_name': 'Auto Product',
            'production_date': '2025-08-11',
            'lot_code': 'AUTO-LOT-001',
            'personel_code': 'AU001'
        },
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'requested_by': 'test_script'
    }
    await sio.emit('print_job', test_job_4)
    await asyncio.sleep(3)
    
    print("\n✅ All test jobs sent!")

async def main():
    try:
        # Connect to server
        await sio.connect('http://192.168.1.139:25625')
        
        # Run tests
        await test_print_jobs()
        
        # Keep connection for a while to receive responses
        await asyncio.sleep(10)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await sio.disconnect()

if __name__ == "__main__":
    print("🧪 WebSocket Print Job Tester")
    print("=" * 50)
    asyncio.run(main())
