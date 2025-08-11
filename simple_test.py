#!/usr/bin/env python3
"""
Simple test to send a print job with data
"""

import socketio
import asyncio
import time

async def send_test_job():
    sio = socketio.AsyncClient()
    
    @sio.event
    async def connect():
        print("✅ Connected to server")
        
        # Send a test job with actual data
        test_job = {
            'job_id': 'test_data_001',
            'label_data': {
                'type': 'test',
                'firma': 'Test Şirketi A.Ş.',
                'product_code': 'TST001',
                'product_name': 'Test Ürünü Deneme',
                'production_date': '2025-08-11',
                'lot_code': 'LOT-TEST-001',
                'personel_code': 'OP001',
                'total_amount': '250',
                'hat_kodu': 'A',
                'bom': '123'
            },
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'requested_by': 'test_user'
        }
        
        print(f"📤 Sending test job with data: {test_job}")
        await sio.emit('print_job', test_job)
    
    @sio.event
    async def print_job_result(data):
        print(f"📄 Print job result: {data}")
    
    @sio.event
    async def disconnect():
        print("❌ Disconnected")
    
    try:
        await sio.connect('http://192.168.1.139:25625')
        await asyncio.sleep(5)  # Wait for responses
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await sio.disconnect()

if __name__ == "__main__":
    asyncio.run(send_test_job())
